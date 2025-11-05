"""
Product Matcher Node - Match materials to catalog products via HTTP

Flow:
1. Get materials from state (from tutorial)
2. For each material, call Mock Catalog API
3. Filter owned items (if user already has cordless screwdriver)
4. Check for multiple adhesive options → HITL
5. Build products_needed list
"""

import httpx
from langgraph.types import interrupt

from app.api.services.llm_adapter.llm_adapter_interface import LLMAdapterInterface
from app.core.correlation import get_correlated_logger

from ...global_supervisor_state import UserInTheLoop
from ..gk_catalog_state import GKCatalogState, ProductMatch

logger = get_correlated_logger(__name__)


class ProductMatcherNode:
    """
    Node 2: Product Matcher
    - Calls Mock Catalog API to match materials to products
    - Filters owned items
    - HITL for adhesive selection
    """

    def __init__(self, llm_adapter: LLMAdapterInterface, correlation_id: str):
        self.llm_adapter = llm_adapter
        self.correlation_id = correlation_id
        self.logger = get_correlated_logger(__name__)

        # Mock API base URL (local backend, default port 8000)
        import os

        port = os.getenv("BACKEND_PORT", "8000")
        self.api_base_url = f"http://localhost:{port}"

    async def execute(self, state: GKCatalogState) -> GKCatalogState:
        """Execute product matching"""
        self.logger.info("🔍 ProductMatcherNode START")

        user_in_the_loop = state.get("user_in_the_loop")

        # Resume after adhesive selection
        if user_in_the_loop and not user_in_the_loop.is_waiting:
            return await self._handle_adhesive_selection(state)

        # Initial: Match products
        return await self._match_products(state)

    async def _match_products(self, state: GKCatalogState) -> GKCatalogState:
        """Match materials to catalog products via HTTP"""

        materials = state.get("materials_needed", [])
        owned_items_str = state.get("owned_items", [])

        self.logger.info(f"📋 Matching {len(materials)} materials to products...")
        self.logger.info(f"🔧 User owns: {owned_items_str}")

        # Convert owned items to lowercase for matching
        owned_items_lower = [item.lower() for item in owned_items_str]

        products_found = []
        adhesive_options = []

        async with httpx.AsyncClient(timeout=10.0) as client:
            for material in materials:
                self.logger.info(f"🔍 Searching for: {material}")

                # Skip if user already owns it (check if material keyword is in any owned item)
                if any(
                    material.lower() in owned.lower() for owned in owned_items_lower
                ):
                    self.logger.info(f"✅ User already owns: {material}")
                    continue

                # Search catalog API using semantic search
                try:
                    response = await client.post(
                        f"{self.api_base_url}/api/v1/gk/catalog/products/search_semantic",
                        json={"query": material, "limit": 3},
                    )
                    response.raise_for_status()
                    data = response.json()
                    results = data.get("results", [])

                    if results:
                        # Take first match (best semantic similarity)
                        product = results[0]

                        # Map API response to ProductMatch format
                        mapped_product = {
                            "product_id": product["id"],
                            "name": product["name"],
                            "description": product.get("description", ""),
                            "price": product["price"],
                            "sku": product["id"],  # Use ID as SKU for now
                            "features": product.get("features", []),
                            "in_stock": True,  # Mock data always in stock
                            "quantity": 10,  # Mock quantity
                        }

                        self.logger.info(
                            f"✅ Found: {mapped_product['name']} (€{mapped_product['price']})"
                        )

                        # Check if it's adhesive (for HITL)
                        if "adhesive" in material.lower() or "glue" in material.lower():
                            adhesive_options.append(mapped_product)
                        else:
                            products_found.append(mapped_product)
                    else:
                        self.logger.warning(f"⚠️ No match for: {material}")

                except Exception as e:
                    self.logger.error(f"❌ Error searching for {material}: {e}")

        self.logger.info(f"📦 Found {len(products_found)} products")
        self.logger.info(f"🧪 Found {len(adhesive_options)} adhesive options")

        # If multiple adhesives, ask user
        if len(adhesive_options) > 1:
            return await self._ask_adhesive_choice(
                state, products_found, adhesive_options
            )

        # Otherwise, add first adhesive and continue
        if adhesive_options:
            products_found.append(adhesive_options[0])

        state["matched_products"] = [ProductMatch(**p) for p in products_found]
        state["user_in_the_loop"] = None

        return state

    async def _ask_adhesive_choice(
        self,
        state: GKCatalogState,
        products_found: list[dict],
        adhesive_options: list[dict],
    ) -> GKCatalogState:
        """Ask user to choose adhesive type (HITL)"""

        self.logger.info("🧪 Multiple adhesives found - asking user...")

        # Format options
        options = [
            {
                "id": p["product_id"],
                "label": f"{p['name']} - €{p['price']:.2f}",
                "name": p["name"],
                "price": p["price"],
            }
            for p in adhesive_options[:2]  # Max 2 options
        ]

        hitl = UserInTheLoop(
            question="I found two adhesive options. Which one would you prefer?",
            options=options,
            is_waiting=True,
            target_agent="gk_catalog_agent",
            response_type="choice",
        )

        # Store partial state
        state["_products_found"] = products_found
        state["_adhesive_options"] = adhesive_options
        state["user_in_the_loop"] = hitl

        # Raise interrupt
        interrupt(hitl)

        return state

    async def _handle_adhesive_selection(self, state: GKCatalogState) -> GKCatalogState:
        """User selected adhesive - finalize products"""

        user_in_the_loop = state["user_in_the_loop"]
        selected_id = user_in_the_loop.answer

        self.logger.info(f"✅ User selected adhesive: {selected_id}")

        # Get products from partial state
        products_found = state.get("_products_found", [])
        adhesive_options = state.get("_adhesive_options", [])

        # Find selected adhesive
        selected_adhesive = next(
            (p for p in adhesive_options if p["product_id"] == selected_id),
            adhesive_options[0],  # Fallback
        )

        # Add selected adhesive to products
        products_found.append(selected_adhesive)

        # Convert to ProductMatch
        state["products_needed"] = [ProductMatch(**p) for p in products_found]

        # Clean up
        state["user_in_the_loop"] = None
        state.pop("_products_found", None)
        state.pop("_adhesive_options", None)

        return state
