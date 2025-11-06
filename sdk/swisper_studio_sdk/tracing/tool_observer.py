"""
Tool observation creator - extracts individual tools from tool_results

Creates separate TOOL observations for each tool call within tool_execution.
This provides better visibility and analytics for individual tool usage.

Handles Swisper's tool_results format:
{
    "batch_read_20251106_123456": {
        "results": {
            "office365_search_emails_folder_inbox_...": {
                "tool_name": "office365_search_emails",
                "result": {...},
                "error": None
            }
        }
    }
}
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def create_tool_observations(
    trace_id: str,
    parent_observation_id: str,
    tool_results: Dict[str, Any]
) -> int:
    """
    Create individual TOOL observations from tool_results structure.
    
    Args:
        trace_id: Trace ID
        parent_observation_id: tool_execution observation ID (parent)
        tool_results: Swisper's tool_results dict
    
    Returns:
        Number of tool observations created
    """
    from .redis_publisher import publish_event
    
    tool_count = 0
    
    try:
        # Iterate through batches
        for batch_key, batch_data in tool_results.items():
            if not isinstance(batch_data, dict) or 'results' not in batch_data:
                continue
            
            results = batch_data.get('results', {})
            
            # Iterate through individual tools in this batch
            for tool_key, tool_data in results.items():
                try:
                    # Create observation for this tool
                    tool_obs_id = str(uuid.uuid4())
                    
                    # Extract tool name
                    tool_name = tool_data.get('tool_name')
                    if not tool_name:
                        # Extract from key (first part before underscore)
                        tool_name = tool_key.split('_')[0] if '_' in tool_key else tool_key
                    
                    # Parse parameters
                    parameters = parse_tool_parameters(tool_key, tool_data)
                    
                    # Check status
                    has_error = bool(tool_data.get('error'))
                    
                    # Create observation start
                    await publish_event(
                        event_type="observation_start",
                        trace_id=trace_id,
                        observation_id=tool_obs_id,
                        data={
                            "name": tool_name,
                            "type": "TOOL",
                            "parent_observation_id": parent_observation_id,
                            "input": {
                                "tool_name": tool_name,
                                "parameters": parameters,
                                "batch_key": batch_key,
                                "tool_key": tool_key,
                            },
                            "start_time": datetime.utcnow().isoformat(),
                        }
                    )
                    
                    # Create observation end (tool already executed)
                    await publish_event(
                        event_type="observation_end",
                        trace_id=trace_id,
                        observation_id=tool_obs_id,
                        data={
                            "output": {
                                "status": "failure" if has_error else "success",
                                "result": tool_data.get('result'),
                                "error": tool_data.get('error'),
                            },
                            "level": "ERROR" if has_error else "DEFAULT",
                            "end_time": datetime.utcnow().isoformat(),
                        }
                    )
                    
                    tool_count += 1
                    logger.debug(f"Created TOOL observation: {tool_name} ({tool_obs_id[:12]}...)")
                
                except Exception as e:
                    logger.warning(f"Failed to create tool observation for {tool_key}: {e}")
                    # Continue with other tools
        
        if tool_count > 0:
            logger.info(f"Created {tool_count} TOOL observations for tool_execution")
        
        return tool_count
    
    except Exception as e:
        logger.warning(f"Failed to process tool_results: {e}")
        return 0


def parse_tool_parameters(tool_key: str, tool_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse tool parameters from tool key and/or tool data.
    
    Tool keys encode parameters: toolname_param1_value1_param2_value2
    Example: office365_search_emails_folder_inbox_filter_receivedDateTime...
    
    Args:
        tool_key: Encoded tool key
        tool_data: Tool data dict (may contain explicit parameters)
    
    Returns:
        Parameters dict
    """
    params = {}
    
    # Check if tool_data has explicit parameters
    if 'parameters' in tool_data and isinstance(tool_data['parameters'], dict):
        params = tool_data['parameters'].copy()
    
    # Try to parse from tool_key (encoded parameters)
    try:
        parts = tool_key.split('_')
        
        # Skip tool name parts (first 1-3 parts depending on tool)
        # Look for key-value pairs in remaining parts
        start_idx = 2  # After tool name
        
        for i in range(start_idx, len(parts), 2):
            if i + 1 < len(parts):
                key = parts[i]
                value = parts[i + 1]
                
                # Only add if looks like a parameter (not part of tool name)
                if key and value and len(key) > 1:
                    # Decode common encodings
                    value = value.replace('ge', '>=').replace('lt', '<').replace('eq', '==')
                    params[key] = value
    
    except Exception as e:
        logger.debug(f"Could not parse parameters from key: {e}")
    
    return params

