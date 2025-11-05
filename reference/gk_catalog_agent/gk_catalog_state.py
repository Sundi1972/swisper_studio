"""
GK Catalog Agent State - simplified for retail demo
"""

from typing import Any, TypedDict

from pydantic import BaseModel


class ProductMatch(BaseModel):
    """Matched product from catalog"""

    product_id: str
    name: str
    description: str
    price: float
    sku: str
    features: list[str]
    in_stock: bool
    quantity: int
    # Enriched by store navigation node
    aisle: str | None = None
    section: str | None = None
    category: str | None = None


class GKCatalogState(TypedDict):
    """State for GK Catalog Agent workflow"""

    # Core
    chat_id: str
    correlation_id: str

    # Input from GlobalSupervisor
    user_request: str  # "I want to build a shelf" (planner's interpretation)
    user_request_for_routing: str  # Original user message for keyword detection
    owned_items: list[str]  # ["Cordless Screwdriver"]

    # From global supervisor
    global_plan: str
    memory_domain: dict[str, Any] | None
    user_timezone: str | None
    current_time: str | None
    user_locale: str | None
    llm_reasoning_language: str | None

    # Node 1: Project Discovery output
    selected_shelf_type: str | None  # "floating_spice"
    shelf_name: str | None  # "Floating Spice Shelf"
    tutorial: str | None  # Full markdown tutorial from DocAgent
    materials_needed: list[str]  # ["MDF board", "adhesive", "cutter"]
    estimated_cost: float | None

    # Node 2: Product Matcher output
    matched_products: list[ProductMatch]
    owned_products: list[dict[str, str]]  # Products user already owns

    # Node 3: Store Navigation output
    route: dict[str, Any] | None  # Shopping route info

    # Node 4: Shopping List Builder output
    shopping_list: str | None  # Final markdown output
    total_price: float | None

    # HITL support
    user_in_the_loop: Any | None  # UserInTheLoop object
    iteration_count: int

    # Phase 4: Availability check support
    availability_result: str | None  # Formatted availability result
    query_type: str | None  # "availability" or "project"
