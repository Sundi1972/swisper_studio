"""
Observability Consumer - Reads trace events from Redis Streams

Connects to Swisper's Redis to consume observability events,
then inserts into SwisperStudio's PostgreSQL database.

Architecture:
- Reads events from Redis Streams (batch processing)
- Uses consumer groups for reliability and retry
- Writes heartbeat for connection status monitoring
- Handles all event types (trace_start, observation_start/end/error)

v0.4.0: Initial Redis Streams consumer implementation
"""

import asyncio
import redis.asyncio as redis
import json
import logging
from datetime import datetime
from typing import Callable, Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Trace, Observation
from app.core.config import settings
from app.api.services.cost_calculation_service import calculate_llm_cost

logger = logging.getLogger(__name__)


class ObservabilityConsumer:
    """
    Consumer for observability events from Redis Streams.

    Reads from Swisper's Redis instance, processes events in batches,
    and stores in SwisperStudio's PostgreSQL database.

    Features:
    - Consumer groups for automatic retry on failure
    - Batch processing for efficiency
    - Heartbeat mechanism for health monitoring
    - Graceful shutdown handling
    """

    def __init__(
        self,
        redis_url: str,
        db_session_factory: Callable,
        stream_name: str = "observability:events",
        group_name: str = "swisper_studio_consumers",
        consumer_name: str = "consumer_1",
        batch_size: int = 50,
    ):
        """
        Initialize the observability consumer.

        Args:
            redis_url: Redis connection URL (e.g., "redis://172.17.0.1:6379")
            db_session_factory: Async session factory for database
            stream_name: Redis stream name
            group_name: Consumer group name
            consumer_name: This consumer's unique name
            batch_size: Number of events to read per batch
        """
        self.redis_url = redis_url
        self.stream_name = stream_name
        self.group_name = group_name
        self.consumer_name = consumer_name
        self.batch_size = batch_size
        self.db_session_factory = db_session_factory
        self.redis_client = None
        self.running = False
        self.events_processed_counter = 0
        self.heartbeat_task = None

    async def start(self):
        """Start the consumer (blocking call - runs until stopped)"""
        logger.info(f"Starting ObservabilityConsumer...")
        logger.info(f"  Redis URL: {self.redis_url}")
        logger.info(f"  Stream: {self.stream_name}")
        logger.info(f"  Group: {self.group_name}")
        logger.info(f"  Consumer: {self.consumer_name}")

        # Connect to Redis
        self.redis_client = redis.from_url(
            self.redis_url,
            decode_responses=True,  # Auto-decode strings
        )

        # Test connection
        try:
            await self.redis_client.ping()
            logger.info("✅ Connected to Redis successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise

        # Create consumer group (if doesn't exist)
        try:
            await self.redis_client.xgroup_create(
                name=self.stream_name,
                groupname=self.group_name,
                id="0",  # Read from beginning
                mkstream=True,  # Create stream if doesn't exist
            )
            logger.info(f"✅ Created consumer group: {self.group_name}")
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.info(f"✅ Consumer group already exists: {self.group_name}")
            else:
                raise

        # Start heartbeat worker
        self.running = True
        self.heartbeat_task = asyncio.create_task(self._heartbeat_worker())
        logger.info("✅ Consumer heartbeat started")

        # Start consuming
        logger.info("✅ ObservabilityConsumer started - processing events...")
        await self._consume_loop()

    async def stop(self):
        """Gracefully stop the consumer"""
        logger.info("Stopping ObservabilityConsumer...")
        self.running = False
        
        # Stop heartbeat
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("✅ ObservabilityConsumer stopped")

    async def _heartbeat_worker(self):
        """
        Write heartbeat every 5 seconds.

        Heartbeat enables SDKs to verify consumer is running.
        """
        while self.running:
            try:
                # Get current stream length
                stream_length = await self.redis_client.xlen(self.stream_name)
                
                # Write heartbeat (expires in 15 seconds)
                await self.redis_client.setex(
                    "swisper_studio:consumer:heartbeat",
                    15,  # TTL: 15 seconds (3x heartbeat interval for safety)
                    json.dumps({
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": "healthy",
                        "consumer_name": self.consumer_name,
                        "group_name": self.group_name,
                        "events_processed": self.events_processed_counter,
                        "stream_length": stream_length,
                    })
                )
                
                logger.debug(f"Heartbeat written (processed: {self.events_processed_counter}, queued: {stream_length})")
                await asyncio.sleep(5)  # Every 5 seconds
                
            except Exception as e:
                logger.warning(f"Failed to write heartbeat: {e}")
                await asyncio.sleep(5)

    async def _consume_loop(self):
        """Main consumption loop - runs continuously"""
        while self.running:
            try:
                # Read batch of events (blocks for max 1 second)
                events = await self.redis_client.xreadgroup(
                    groupname=self.group_name,
                    consumername=self.consumer_name,
                    streams={self.stream_name: ">"},  # ">" = new events only
                    count=self.batch_size,
                    block=1000,  # 1 second timeout
                )

                if events:
                    # events = [('observability:events', [('msg_id', {data}), ...])]
                    for stream_name, messages in events:
                        await self._process_batch(messages)

            except asyncio.CancelledError:
                logger.info("Consumer loop cancelled - shutting down")
                break
            except Exception as e:
                logger.error(f"❌ Consumer error: {e}")
                await asyncio.sleep(1.0)  # Back off on error

    async def _process_batch(self, messages: List[Tuple[str, Dict[str, str]]]):
        """
        Process batch of messages.

        IMPORTANT: Process trace_start events FIRST, then observations.
        This ensures traces exist before observations reference them.

        Inserts into database and acknowledges successful processing.
        Failed messages are not acknowledged and will be retried.
        """
        if not messages:
            return

        logger.debug(f"Processing batch of {len(messages)} events")

        # Sort events: trace_start first, then observation_start, then observation_end/error
        event_priority = {
            "trace_start": 0,
            "observation_start": 1,
            "observation_end": 2,
            "observation_error": 2,
        }
        
        sorted_messages = sorted(
            messages,
            key=lambda msg: event_priority.get(msg[1].get("event_type", ""), 99)
        )

        async with self.db_session_factory() as session:
            processed_ids = []

            for message_id, data in sorted_messages:
                try:
                    await self._process_event(session, data)
                    
                    # Commit after each trace_start to make trace available
                    # Commit after each observation_start to make observation available for observation_end
                    event_type = data.get("event_type")
                    if event_type in ["trace_start", "observation_start"]:
                        await session.commit()
                    
                    processed_ids.append(message_id)

                except Exception as e:
                    logger.error(f"❌ Failed to process event {message_id}: {e}")
                    logger.error(f"   Event type: {data.get('event_type')}")
                    logger.error(f"   Trace ID: {data.get('trace_id')}")
                    # Rollback the failed transaction
                    await session.rollback()
                    # Don't add to processed_ids - will be retried by consumer group

            # Final commit for remaining events (observation_end, etc.)
            if processed_ids:
                try:
                    await session.commit()
                except:
                    # Already committed incrementally
                    pass

                # Acknowledge processed messages
                for msg_id in processed_ids:
                    await self.redis_client.xack(
                        self.stream_name,
                        self.group_name,
                        msg_id
                    )

                self.events_processed_counter += len(processed_ids)
                logger.info(f"✅ Processed {len(processed_ids)} events (total: {self.events_processed_counter})")

    async def _process_event(self, session: AsyncSession, data: Dict[str, str]):
        """
        Process single event and insert/update database.

        Event types:
        - trace_start: Create new trace
        - observation_start: Create new observation
        - observation_end: Update observation with output
        - observation_error: Mark observation as failed
        """
        event_type = data.get("event_type")
        trace_id = data.get("trace_id")
        observation_id = data.get("observation_id")
        project_id = data.get("project_id")  # Get from top level!
        
        # Parse event data (JSON string)
        event_data = {}
        if "data" in data:
            try:
                event_data = json.loads(data.get("data"))
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse event data: {e}")
                return

        if event_type == "trace_start":
            await self._handle_trace_start(session, trace_id, project_id, event_data)
        
        elif event_type == "observation_start":
            await self._handle_observation_start(session, trace_id, observation_id, event_data)
        
        elif event_type == "observation_end":
            await self._handle_observation_end(session, observation_id, event_data)
        
        elif event_type == "observation_error":
            await self._handle_observation_error(session, observation_id, event_data)
        
        else:
            logger.warning(f"Unknown event type: {event_type}")

    async def _handle_trace_start(self, session: AsyncSession, trace_id: str, project_id: str, data: Dict[str, Any]):
        """Create new trace in database"""
        trace = Trace(
            id=trace_id,
            project_id=project_id or settings.DEFAULT_PROJECT_ID,  # From event top level
            name=data.get("name", "unnamed_trace"),
            user_id=data.get("user_id"),  # External user ID (no FK constraint!)
            session_id=data.get("session_id"),
            meta=data.get("meta", {}),
            tags=data.get("tags", []),
            timestamp=datetime.fromisoformat(data.get("timestamp")) if data.get("timestamp") else datetime.utcnow(),
        )
        session.add(trace)
        logger.debug(f"Created trace: {trace_id} for project: {project_id}")

    async def _handle_observation_start(
        self, 
        session: AsyncSession, 
        trace_id: str, 
        observation_id: str, 
        data: Dict[str, Any]
    ):
        """Create new observation in database"""
        observation = Observation(
            id=observation_id,
            trace_id=trace_id,
            parent_observation_id=data.get("parent_observation_id"),
            type=data.get("type", "SPAN"),
            name=data.get("name", "unnamed_observation"),
            input=data.get("input"),
            start_time=datetime.fromisoformat(data.get("start_time")) if data.get("start_time") else datetime.utcnow(),
            level="DEFAULT",
        )
        session.add(observation)
        logger.debug(f"Created observation: {observation_id} ({observation.name})")

    async def _handle_observation_end(
        self, 
        session: AsyncSession, 
        observation_id: str, 
        data: Dict[str, Any]
    ):
        """Update observation with output, tokens, and calculate costs"""
        # Fetch observation with trace relationship
        result = await session.execute(
            select(Observation).where(Observation.id == observation_id)
        )
        observation = result.scalar_one_or_none()
        
        if observation:
            output = data.get("output")
            observation.output = output
            observation.end_time = datetime.fromisoformat(data.get("end_time")) if data.get("end_time") else datetime.utcnow()
            observation.level = data.get("level", "DEFAULT")
            
            # Update type if provided (for AUTO type detection)
            if "type" in data:
                observation.type = data.get("type")
            
            # Extract token data from SDK capture (output._llm_tokens)
            if output and isinstance(output, dict) and '_llm_tokens' in output:
                llm_tokens = output['_llm_tokens']
                observation.prompt_tokens = llm_tokens.get('prompt')
                observation.completion_tokens = llm_tokens.get('completion')
                observation.total_tokens = llm_tokens.get('total')
                
                # If tokens are None (streaming without usage), estimate from text
                if observation.total_tokens is None or observation.total_tokens == 0:
                    estimated = self._estimate_tokens_from_output(output)
                    if estimated:
                        observation.prompt_tokens = estimated['prompt']
                        observation.completion_tokens = estimated['completion']
                        observation.total_tokens = estimated['total']
                        logger.debug(f"Estimated tokens (streaming): {observation.total_tokens} ({observation.prompt_tokens}↑ {observation.completion_tokens}↓)")
                else:
                    logger.debug(f"Extracted tokens: {observation.total_tokens} ({observation.prompt_tokens}↑ {observation.completion_tokens}↓)")
                
                # Extract model name from SDK capture (output._llm_model)
                model_name = output.get('_llm_model')
                
                # Calculate costs if we have model name and tokens
                if model_name and observation.prompt_tokens and observation.completion_tokens:
                    try:
                        # Import cost calculation service
                        from app.api.services.cost_calculation_service import calculate_llm_cost
                        
                        # Get trace to find project_id
                        trace_result = await session.execute(
                            select(Trace).where(Trace.id == observation.trace_id)
                        )
                        trace = trace_result.scalar_one_or_none()
                        
                        if trace:
                            # Calculate costs using OUR pricing configuration
                            cost_result = await calculate_llm_cost(
                                session=session,
                                project_id=trace.project_id,
                                model=model_name,
                                prompt_tokens=observation.prompt_tokens,
                                completion_tokens=observation.completion_tokens
                            )
                            
                            if cost_result:
                                observation.calculated_input_cost = cost_result.input_cost
                                observation.calculated_output_cost = cost_result.output_cost
                                observation.calculated_total_cost = cost_result.total_cost
                                observation.model = model_name  # Also store model name
                                logger.debug(
                                    f"Calculated cost: ${cost_result.total_cost} "
                                    f"(input: ${cost_result.input_cost}, output: ${cost_result.output_cost}) "
                                    f"for {model_name}"
                                )
                            else:
                                logger.warning(f"No pricing found for model: {model_name}")
                        else:
                            logger.warning(f"Trace not found for observation {observation_id}")
                    
                    except Exception as e:
                        logger.warning(f"Cost calculation failed: {e}")
                        # Continue without costs - not critical
            
            session.add(observation)
            logger.debug(f"Updated observation: {observation_id} ({observation.name}) - type: {observation.type}")
        else:
            logger.warning(f"⚠️ Observation not found for update: {observation_id}")

    def _estimate_tokens_from_output(self, output: Dict[str, Any]) -> Dict[str, int] | None:
        """
        Estimate tokens when actual counts unavailable (e.g., streaming without usage).
        
        Uses industry-standard approximation: ~0.75 tokens per word
        
        Returns:
            dict with prompt, completion, total tokens (estimated)
            None if can't estimate
        """
        try:
            prompt_tokens = 0
            completion_tokens = 0
            
            # Estimate prompt tokens from _llm_messages
            if '_llm_messages' in output and isinstance(output['_llm_messages'], list):
                for msg in output['_llm_messages']:
                    if isinstance(msg, dict) and 'content' in msg:
                        # ~0.75 tokens per word (conservative estimate)
                        word_count = len(str(msg['content']).split())
                        prompt_tokens += int(word_count * 0.75)
            
            # Estimate completion tokens from _llm_result
            if '_llm_result' in output and output['_llm_result']:
                result_text = str(output['_llm_result'])
                word_count = len(result_text.split())
                completion_tokens = int(word_count * 0.75)
            
            # If we got some estimates
            if prompt_tokens > 0 or completion_tokens > 0:
                return {
                    'prompt': prompt_tokens,
                    'completion': completion_tokens,
                    'total': prompt_tokens + completion_tokens
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Token estimation failed: {e}")
            return None

    async def _handle_observation_error(
        self, 
        session: AsyncSession, 
        observation_id: str, 
        data: Dict[str, Any]
    ):
        """Mark observation as failed"""
        # Fetch observation
        result = await session.execute(
            select(Observation).where(Observation.id == observation_id)
        )
        observation = result.scalar_one_or_none()
        
        if observation:
            observation.level = "ERROR"
            observation.status_message = data.get("error") or data.get("status_message")
            observation.end_time = datetime.fromisoformat(data.get("end_time")) if data.get("end_time") else datetime.utcnow()
            session.add(observation)
            logger.debug(f"Marked observation as error: {observation_id}")
        else:
            logger.warning(f"⚠️ Observation not found for error: {observation_id}")

