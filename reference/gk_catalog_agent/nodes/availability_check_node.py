"""
Availability Check Node - Simple product availability queries

Handles queries like:
- "Do you have MDF boards?"
- "What's the price of wood glue?"
- "Show me drills in Zurich"

Flow:
1. Extract product keywords from user request
2. Call semantic search API to find matching products
3. Call availability API to check stock
4. Format markdown response with pricing and store locations
"""

from typing import Any

import httpx

from app.api.services.llm_adapter.llm_adapter_interface import LLMAdapterInterface
from app.core.config import settings
from app.core.correlation import get_correlated_logger

from ..gk_catalog_state import GKCatalogState

logger = get_correlated_logger(__name__)


class AvailabilityCheckNode:
    """
    Node for simple product availability queries

    Simpler alternative to full project flow - just checks if product is available
    """

    # Configuration constants
    DISTANCE_THRESHOLD = (
        0.5  # Semantic search distance threshold (lower = better match)
    )
    API_TIMEOUT = 10.0  # Timeout for API calls in seconds

    def __init__(self, llm_adapter: LLMAdapterInterface, correlation_id: str):
        self.llm_adapter = llm_adapter
        self.correlation_id = correlation_id
        self.logger = get_correlated_logger(__name__)

        # Base URL for GK API (use internal service name for Docker network)
        # In production, this would be the actual GK API endpoint
        self.base_url = getattr(settings, "GK_API_BASE_URL", "http://localhost:8000")

    async def execute(self, state: GKCatalogState) -> GKCatalogState:
        """Execute availability check"""
        self.logger.info("🔍 AvailabilityCheckNode START")

        # Use original user input for product search (not planner's interpretation)
        # This ensures semantic search uses the actual user's words
        user_request = state.get("user_request_for_routing") or state["user_request"]

        # Extract product query and optional store filter
        product_query, store_query = self._extract_queries(user_request)

        self.logger.info(
            f"Product query: '{product_query}', Store filter: '{store_query}'"
        )

        # Search for products using semantic search
        products = await self._search_products(product_query)

        # Filter out poor matches (distance > threshold means weak similarity)
        good_matches = [
            p for p in products if p.get("distance", 1.0) < self.DISTANCE_THRESHOLD
        ]

        if not good_matches:
            # No good matches found
            result = self._format_not_found_response(product_query)
            state["availability_result"] = result
            return state

        # Get top product match
        top_product = good_matches[0]
        self.logger.info(
            f"Top match: {top_product['name']} (distance: {top_product.get('distance', 'N/A')})"
        )

        # Get full product details with availability across all stores
        product_detail = await self._get_product_detail(top_product["id"])

        if not product_detail:
            result = self._format_not_found_response(product_query)
            state["availability_result"] = result
            return state

        # Filter by store if requested
        if store_query:
            product_detail["availability"] = [
                store
                for store in product_detail["availability"]
                if store_query.lower() in store["city"].lower()
                or store_query.lower() in store["store_name"].lower()
            ]

        # Format response
        result = self._format_availability_response(product_detail, store_query)
        state["availability_result"] = result

        self.logger.info("✅ AvailabilityCheckNode COMPLETE")
        return state

    def _extract_queries(self, user_request: str) -> tuple[str, str | None]:
        """
        Extract product query and optional store filter from user request

        Returns: (product_query, store_query)
        """
        request_lower = user_request.lower()

        # Extract store/city filter
        store_query = None
        for city in ["zurich", "zürich", "bern", "basel"]:
            if city in request_lower:
                store_query = city
                break

        # Product query is the request with common prefixes removed
        product_query = user_request
        for prefix in [
            "do you have",
            "show me",
            "what's the price of",
            "i need",
            "find",
        ]:
            if request_lower.startswith(prefix):
                # Remove prefix
                product_query = user_request[len(prefix) :].strip()
                break

        # Remove store name from product query if present
        if store_query:
            # Remove variations of "in [city]"
            for pattern in [f"in {store_query}", f"at {store_query}"]:
                product_query = product_query.replace(pattern, "").strip()

        # Remove question marks and trailing "?"
        product_query = product_query.rstrip("?").strip()

        return product_query, store_query

    async def _search_products(
        self, query: str, limit: int = 3
    ) -> list[dict[str, Any]]:
        """
        Call semantic search API to find products

        Returns: List of matching products with similarity scores
        """
        try:
            async with httpx.AsyncClient(timeout=self.API_TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/gk/catalog/products/search_semantic",
                    json={"query": query, "limit": limit},
                )
                response.raise_for_status()
                data = response.json()
                # API returns {query, results, total} - extract results list
                return data.get("results", [])
        except httpx.HTTPError as e:
            self.logger.error(f"Error calling semantic search API: {e}")
            return []

    async def _get_product_detail(self, product_id: str) -> dict[str, Any] | None:
        """
        Get complete product details with availability across all stores

        Returns: Product details with availability list
        """
        try:
            async with httpx.AsyncClient(timeout=self.API_TIMEOUT) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/gk/catalog/products/{product_id}"
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"Error calling product detail API: {e}")
            return None

    def _format_not_found_response(self, product_query: str) -> str:
        """Format response when no products found"""
        return f"""I couldn't find any products matching "{product_query}" in our catalog.

Could you try:
- Using a different search term
- Being more specific about the product
- Checking the spelling"""

    def _format_availability_response(
        self, product_detail: dict[str, Any], store_filter: str | None = None
    ) -> str:
        """
        Format availability response as markdown

        Shows:
        - Product name, price, SKU
        - Availability across stores (or specific store if filtered)
        - Store locations with stock levels and aisle/section
        """
        # Header with product info
        lines = [
            f"✅ **{product_detail['name']}** - CHF {product_detail['price']:.2f}",
            "",
        ]

        # Add description if present
        if product_detail.get("description"):
            lines.append(f"_{product_detail['description']}_")
            lines.append("")

        # Availability info
        availability = product_detail.get("availability", [])

        if not availability:
            lines.append("❌ Currently not available in any stores.")
            return "\n".join(lines)

        # Format store info
        if store_filter:
            lines.append(
                f"Available at **{len(availability)}** store(s) in {store_filter.title()}:"
            )
        else:
            lines.append(f"Available at **{len(availability)}** store(s):")

        lines.append("")

        for store_info in availability:
            store_name = store_info.get("store_name", "Unknown")
            city = store_info.get("city", "")
            stock = store_info.get("stock", 0)
            aisle = store_info.get("aisle")
            section = store_info.get("section")

            # Store header
            lines.append(f"📍 **{store_name}**{f' ({city})' if city else ''}")
            lines.append(f"   - Stock: {stock} units")

            # Location if available
            if aisle or section:
                location_parts = []
                if aisle:
                    location_parts.append(f"Aisle {aisle}")
                if section:
                    location_parts.append(section)
                lines.append(f"   - Location: {', '.join(location_parts)}")

            lines.append("")

        return "\n".join(lines)
