"""
GK Catalog Agent - Retail shopping assistant for DIY projects

Helps users:
1. Select DIY project type (calls DocAgent for tutorials)
2. Match required materials to catalog products
3. Add store locations and navigation
4. Generate shopping list with tutorial

Uses HITL for:
- Shelf type selection (3 options)
- Adhesive choice (2 options)
"""

from typing import cast

from langgraph.graph import END, StateGraph

from app.api.services.llm_adapter.llm_adapter_interface import LLMAdapterInterface
from app.core.correlation import get_correlated_logger

from ..domain_agent_interface import (
    AgentStatus,
    DomainAgentInput,
    DomainAgentInterface,
    DomainAgentResult,
)
from .gk_catalog_state import GKCatalogState
from .nodes.availability_check_node import AvailabilityCheckNode
from .nodes.product_matcher_node import ProductMatcherNode

# Import nodes
from .nodes.project_discovery_node import ProjectDiscoveryNode
from .nodes.shopping_list_builder_node import ShoppingListBuilderNode
from .nodes.store_navigation_node import StoreNavigationNode

logger = get_correlated_logger(__name__)


class GKCatalogAgent(DomainAgentInterface):
    """
    GK Catalog Agent - Helps users complete DIY projects with retail shopping assistance.

    Flow:
    1. ProjectDiscoveryNode - Call DocAgent, present shelf options (HITL), get tutorial
    2. ProductMatcherNode - Match materials to products, handle adhesive choice (HITL)
    3. StoreNavigationNode - Add store locations
    4. ShoppingListBuilderNode - Format final output with tutorial
    """

    def __init__(
        self,
        llm_adapter: LLMAdapterInterface,
        max_iterations: int = 10,
        correlation_id: str = "",
    ):
        self.logger = get_correlated_logger(__name__)
        self.llm_adapter = llm_adapter
        self.max_iterations = max_iterations
        self._graph_cache = None
        self.correlation_id = correlation_id

        # Initialize nodes
        self.project_discovery_node = ProjectDiscoveryNode(llm_adapter, correlation_id)
        self.product_matcher_node = ProductMatcherNode(llm_adapter, correlation_id)
        self.store_navigation_node = StoreNavigationNode(llm_adapter, correlation_id)
        self.shopping_list_builder_node = ShoppingListBuilderNode(
            llm_adapter, correlation_id
        )
        self.availability_check_node = AvailabilityCheckNode(
            llm_adapter, correlation_id
        )

    @property
    def agent_name(self) -> str:
        """Return the unique name of this domain agent"""
        return "gk_catalog_agent"

    @property
    def agent_description(self) -> str:
        """Return a description of what this agent does"""
        return "Retail shopping assistant for DIY projects. Helps users select project types, match materials to catalog products, find items in store, and generate shopping lists with building instructions."

    async def execute(self, input_data: DomainAgentInput) -> DomainAgentResult:
        """Execute the GK Catalog Agent workflow"""

        logger.info(
            f"🛒 GKCatalogAgent.execute() - plan: {input_data.current_plan[:100]}..."
        )

        # Use original user input for routing detection, fallback to plan if not available
        # This ensures keyword-based routing works correctly
        user_request_for_routing = input_data.user_input or input_data.current_plan

        # Use plan for execution (contains planner's instructions)
        user_request = input_data.current_plan
        owned_items = self._extract_owned_items(user_request)

        initial_state: GKCatalogState = {
            "chat_id": input_data.chat_id,
            "correlation_id": self.correlation_id,
            "user_request": user_request,
            "user_request_for_routing": user_request_for_routing,  # For routing logic
            "owned_items": owned_items,
            "global_plan": input_data.current_plan,
            "memory_domain": input_data.memory_domain,
            "user_timezone": input_data.user_timezone,
            "current_time": input_data.current_time,
            "user_locale": getattr(input_data, "user_locale", None),
            "llm_reasoning_language": getattr(
                input_data, "llm_reasoning_language", "english"
            ),
            "user_in_the_loop": input_data.user_in_the_loop,
            "iteration_count": 0,
            # Initialize outputs
            "selected_shelf_type": None,
            "shelf_name": None,
            "tutorial": None,
            "materials_needed": [],
            "estimated_cost": None,
            "matched_products": [],
            "owned_products": [],
            "route": None,
            "shopping_list": None,
            "total_price": None,
            "availability_result": None,  # Phase 4
            "query_type": None,  # Phase 4
        }

        final_state = None

        try:
            # Run the workflow
            workflow = self.build_graph()
            final_state = cast(
                GKCatalogState,
                await workflow.ainvoke(
                    initial_state,
                    config={
                        "run_name": "Graph - GK Catalog Agent",
                        "metadata": {
                            "correlation_id": self.correlation_id,
                            "chat_id": input_data.chat_id,
                        },
                    },
                ),
            )

            # Extract results
            user_in_the_loop = final_state.get("user_in_the_loop")
            shopping_list = final_state.get("shopping_list")
            availability_result = final_state.get("availability_result")

            # Handle escaping
            if user_in_the_loop and user_in_the_loop.escaping:
                return DomainAgentResult(
                    status=AgentStatus.INCOMPLETE,
                    result=f"User cancelled: {user_in_the_loop.answer}",
                    user_in_the_loop=user_in_the_loop,
                )

            # Success - availability result (simple query)
            if availability_result:
                return DomainAgentResult(
                    status=AgentStatus.COMPLETE,
                    result=availability_result,
                    user_in_the_loop=None,
                )

            # Success - shopping list (project query)
            if shopping_list:
                return DomainAgentResult(
                    status=AgentStatus.COMPLETE,
                    result=shopping_list,
                    user_in_the_loop=None,
                )
            else:
                return DomainAgentResult(
                    status=AgentStatus.INCOMPLETE,
                    result=None,
                    user_in_the_loop=user_in_the_loop,
                )

        except Exception as e:
            from app.core.error_handler import is_graph_interrupt

            # Handle GraphInterrupt (HITL)
            if is_graph_interrupt(e):
                logger.info(f"GKCatalogAgent: User input required - {e}")
                user_in_the_loop = e.args[0][0].value if e.args else None

                return DomainAgentResult(
                    status=AgentStatus.WAITING_FOR_INPUT,
                    result=None,
                    user_in_the_loop=user_in_the_loop,
                )
            else:
                raise

    def _extract_owned_items(self, user_request: str) -> list[str]:
        """Extract owned items from user request (simple keyword matching for demo)"""
        owned = []
        request_lower = user_request.lower()

        if "screwdriver" in request_lower or "drill" in request_lower:
            owned.append("screwdriver")
        if "hammer" in request_lower:
            owned.append("hammer")

        logger.info(f"Extracted owned items: {owned}")
        return owned

    def build_graph(self):
        """Build the LangGraph workflow with routing"""
        if self._graph_cache is not None:
            return self._graph_cache

        workflow = StateGraph(GKCatalogState)

        # Add all nodes
        workflow.add_node("availability_check", self.availability_check_node.execute)
        workflow.add_node("project_discovery", self.project_discovery_node.execute)
        workflow.add_node("product_matcher", self.product_matcher_node.execute)
        workflow.add_node("store_navigation", self.store_navigation_node.execute)
        workflow.add_node(
            "shopping_list_builder", self.shopping_list_builder_node.execute
        )

        # Set entry point with conditional routing
        workflow.add_conditional_edges(
            "__start__",
            self._route_from_entry,
            {
                "availability_check": "availability_check",
                "project_discovery": "project_discovery",
            },
        )

        # Availability check goes directly to END
        workflow.add_edge("availability_check", END)

        # Project flow routing (unchanged)
        workflow.add_conditional_edges(
            "project_discovery",
            self._route_from_project_discovery,
            {
                "project_discovery": "project_discovery",  # Loop back if HITL waiting
                "product_matcher": "product_matcher",
                "end": END,
            },
        )

        workflow.add_conditional_edges(
            "product_matcher",
            self._route_from_product_matcher,
            {
                "product_matcher": "product_matcher",  # Loop back if HITL waiting
                "store_navigation": "store_navigation",
                "end": END,
            },
        )

        workflow.add_edge("store_navigation", "shopping_list_builder")
        workflow.add_edge("shopping_list_builder", END)

        self._graph_cache = workflow.compile()
        return self._graph_cache

    def _route_from_entry(self, state: GKCatalogState) -> str:
        """Route from entry point based on query type"""
        # CRITICAL: If resuming from HITL, go directly to the node that created it
        hitl = state.get("user_in_the_loop")
        if hitl and hasattr(hitl, "answer") and hitl.answer:
            # User just answered a HITL question - resume at project_discovery
            logger.debug("Resuming from HITL - routing to project_discovery")
            return "project_discovery"

        # Fresh request - use keyword-based routing
        # Use original user message for routing (not planner's interpretation)
        user_request = state.get("user_request_for_routing", "") or state.get(
            "user_request", ""
        )

        if self._is_availability_query(user_request):
            logger.debug(
                f"Routing to availability_check for query: {user_request[:50]}"
            )
            return "availability_check"
        else:
            logger.debug(f"Routing to project_discovery for query: {user_request[:50]}")
            return "project_discovery"

    def _is_availability_query(self, user_request: str) -> bool:
        """
        Detect if query is about product availability/pricing (simple query)
        vs DIY project building (complex query)

        Uses keyword-based detection for demo purposes.
        """
        query_lower = user_request.lower()

        # Availability/pricing keywords
        availability_keywords = [
            "do you have",
            "is there",
            "available",
            "in stock",
            "how much",
            "price",
            "cost",
            "show me",
            "find",
            "what's the price",
            "how much is",
        ]

        # Project/DIY keywords
        project_keywords = [
            "build",
            "make",
            "create",
            "diy",
            "project",
            "how to",
            "shelf",
            "furniture",
            "construct",
            "help me build",
            "help me make",
        ]

        # Check for keywords
        has_availability = any(kw in query_lower for kw in availability_keywords)
        has_project = any(kw in query_lower for kw in project_keywords)

        # Decision logic:
        # - If both: prefer project (more complex)
        # - If neither: default to availability (simpler)
        # - If only availability: route to availability
        # - If only project: route to project

        if has_project:
            # Has project keywords → always go to project (even if also has availability)
            return False

        # No project keywords → default to availability (whether has availability keywords or not)
        return True

    def _route_from_project_discovery(self, state: GKCatalogState) -> str:
        """Route from project discovery"""
        user_in_the_loop = state.get("user_in_the_loop")

        # If waiting for user input, stay in node
        if user_in_the_loop and user_in_the_loop.is_waiting:
            logger.debug("Routing back to project_discovery - waiting for user input")
            return "project_discovery"

        # If tutorial is loaded, proceed to product matching
        if state.get("tutorial"):
            logger.debug("Routing to product_matcher - tutorial loaded")
            return "product_matcher"

        logger.error("No tutorial found and not waiting - ending")
        return "end"

    def _route_from_product_matcher(self, state: GKCatalogState) -> str:
        """Route from product matcher"""
        user_in_the_loop = state.get("user_in_the_loop")

        # If waiting for user input, stay in node
        if user_in_the_loop and user_in_the_loop.is_waiting:
            logger.debug("Routing back to product_matcher - waiting for user input")
            return "product_matcher"

        # If products matched, proceed to navigation
        if state.get("matched_products"):
            logger.debug("Routing to store_navigation - products matched")
            return "store_navigation"

        logger.error("No products matched and not waiting - ending")
        return "end"
