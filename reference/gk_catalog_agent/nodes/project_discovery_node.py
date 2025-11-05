"""
Project Discovery Node - Present shelf options and load tutorial

Simplified approach (no DocAgent):
1. Present 3 hardcoded shelf options (HITL)
2. User selects one
3. Load tutorial from filesystem
4. Extract materials
"""

from langgraph.types import interrupt

from app.api.services.llm_adapter.llm_adapter_interface import LLMAdapterInterface
from app.core.correlation import get_correlated_logger

from ...global_supervisor_state import UserInTheLoop
from ..gk_catalog_state import GKCatalogState
from ..tutorial_catalog import (
    get_materials,
    get_shelf_metadata,
    get_shelf_options,
    get_tutorial,
)

logger = get_correlated_logger(__name__)


class ProjectDiscoveryNode:
    """
    Node 1: Project Discovery
    - Present 3 shelf options to user (HITL)
    - Load selected tutorial from catalog
    - Extract materials list
    """

    def __init__(self, llm_adapter: LLMAdapterInterface, correlation_id: str):
        self.llm_adapter = llm_adapter
        self.correlation_id = correlation_id
        self.logger = get_correlated_logger(__name__)

    async def execute(self, state: GKCatalogState) -> GKCatalogState:
        """Execute project discovery"""
        self.logger.info("📋 ProjectDiscoveryNode START")

        user_in_the_loop = state.get("user_in_the_loop")

        # Resume after user selection
        if user_in_the_loop and not user_in_the_loop.is_waiting:
            return await self._handle_user_selection(state)

        # Initial: Present shelf options
        return await self._present_shelf_options(state)

    async def _present_shelf_options(self, state: GKCatalogState) -> GKCatalogState:
        """Present shelf options to user"""

        self.logger.info("📋 Presenting shelf options to user...")

        # Get shelf options from catalog
        shelf_options = get_shelf_options()

        self.logger.info(f"📋 Found {len(shelf_options)} shelf options")

        # Get current plan from state (needed for resumption)
        current_plan = state.get("user_request") or "Build kitchen shelf"

        # Create HITL request with options as top-level fields
        hitl = UserInTheLoop(
            question="Great! I can help you build a shelf. Which type would you like to build?",
            is_waiting=True,
            target_agent="gk_catalog_agent",
            options=shelf_options,  # Top-level field (frontend expects this)
            response_type="choice",  # Top-level field
            current_plan=current_plan,  # Needed for resumption after HITL
        )

        state["user_in_the_loop"] = hitl

        # Raise interrupt to pause workflow
        interrupt(hitl)

        return state

    async def _handle_user_selection(self, state: GKCatalogState) -> GKCatalogState:
        """User selected a shelf - load tutorial"""

        user_in_the_loop = state["user_in_the_loop"]
        shelf_id = user_in_the_loop.answer

        self.logger.info(f"✅ User selected shelf: {shelf_id}")

        # Load tutorial from catalog
        tutorial = get_tutorial(shelf_id)
        materials = get_materials(shelf_id)
        metadata = get_shelf_metadata(shelf_id)

        self.logger.info(f"📖 Tutorial loaded: {len(tutorial)} chars")
        self.logger.info(f"🛠️ Materials needed: {materials}")

        # Update state
        state["selected_shelf_type"] = shelf_id
        state["shelf_name"] = metadata["name"]
        state["tutorial"] = tutorial
        state["materials_needed"] = materials
        state["estimated_cost"] = metadata["cost"]
        state["user_in_the_loop"] = None  # Clear HITL

        return state
