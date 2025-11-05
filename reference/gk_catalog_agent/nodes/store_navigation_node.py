"""
Store Navigation Node - Enrich products with store locations

Flow:
1. Take products_needed from state
2. For each product, call Store Layout API
3. Add aisle, section, category to ProductMatch
4. Update state
"""
import logging
import httpx
from typing import List
from app.core.correlation import get_correlated_logger

from app.api.services.llm_adapter.llm_adapter_interface import LLMAdapterInterface
from ..gk_catalog_state import GKCatalogState, ProductMatch
from app.core.config import settings

logger = get_correlated_logger(__name__)


class StoreNavigationNode:
    """
    Node 3: Store Navigation
    - Enriches products with store locations
    - Calls Mock Store Layout API
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
        """Enrich products with store locations"""

        self.logger.info("🗺️ StoreNavigationNode START")

        products = state.get("products_needed", [])

        if not products:
            self.logger.warning("⚠️ No products to enrich")
            return state

        self.logger.info(f"📍 Enriching {len(products)} products with locations...")

        enriched_products = []

        async with httpx.AsyncClient(timeout=10.0) as client:
            for product in products:
                try:
                    # Call Store Layout API
                    response = await client.get(
                        f"{self.api_base_url}/api/gk/store/location/{product.product_id}"
                    )
                    response.raise_for_status()
                    location = await response.json()

                    # Enrich product
                    product.aisle = location["aisle"]
                    product.section = location["section"]
                    product.category = location["category"]
                    product.quantity = location["stock"]

                    self.logger.info(
                        f"✅ {product.name}: Aisle {location['aisle']} "
                        f"({location['section']}) - {location['stock']} in stock"
                    )

                    enriched_products.append(product)

                except Exception as e:
                    self.logger.error(f"❌ Error getting location for {product.name}: {e}")
                    # Keep product without location
                    enriched_products.append(product)

        state["products_needed"] = enriched_products

        self.logger.info(f"✅ Enriched {len(enriched_products)} products")

        return state

