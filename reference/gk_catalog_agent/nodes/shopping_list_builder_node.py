"""
Shopping List Builder Node - Format final output as markdown

Flow:
1. Take enriched products from state
2. Format as markdown shopping list with locations
3. Include tutorial steps
4. Return formatted message
"""

from app.api.services.llm_adapter.llm_adapter_interface import LLMAdapterInterface
from app.core.correlation import get_correlated_logger

from ..gk_catalog_state import GKCatalogState

logger = get_correlated_logger(__name__)


class ShoppingListBuilderNode:
    """
    Node 4: Shopping List Builder
    - Formats products and tutorial as markdown
    - Creates final user-facing message
    """

    def __init__(self, llm_adapter: LLMAdapterInterface, correlation_id: str):
        self.llm_adapter = llm_adapter
        self.correlation_id = correlation_id
        self.logger = get_correlated_logger(__name__)

    async def execute(self, state: GKCatalogState) -> GKCatalogState:
        """Build shopping list markdown"""

        self.logger.info("📝 ShoppingListBuilderNode START")

        products = state.get("products_needed", [])
        shelf_name = state.get("shelf_name", "your shelf")
        estimated_cost = state.get("estimated_cost", 0)
        tutorial = state.get("tutorial", "")

        # Build shopping list
        shopping_list_md = self._format_shopping_list(
            products, shelf_name, estimated_cost
        )

        # Append tutorial (truncated for UI)
        tutorial_preview = self._truncate_tutorial(tutorial)

        final_message = f"{shopping_list_md}\n\n{tutorial_preview}"

        state["shopping_list"] = final_message

        self.logger.info(f"✅ Shopping list built: {len(final_message)} chars")

        return state

    def _format_shopping_list(self, products, shelf_name, estimated_cost):
        """Format products as markdown shopping list"""

        if not products:
            return "No additional items needed! ✅"

        # Header
        lines = [
            f"# 🛒 Shopping List for {shelf_name}",
            "",
            f"**Estimated Total:** ~€{estimated_cost:.2f}",
            f"**Items to Buy:** {len(products)}",
            "",
            "## Items",
            "",
        ]

        # Group by category
        by_category = {}
        for product in products:
            category = product.category or "General"
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(product)

        # Format each category
        for category, prods in sorted(by_category.items()):
            lines.append(f"### {category}")
            lines.append("")

            for product in prods:
                # Product line with location
                location_emoji = "📍"
                location_text = (
                    f"Aisle {product.aisle}" if product.aisle else "Check store"
                )

                lines.append(
                    f"**{product.name}** - €{product.price:.2f}  "
                    f"{location_emoji} {location_text} ({product.section or 'N/A'})"
                )

                # Features (if any)
                if product.features:
                    features_text = " • ".join(product.features[:3])
                    lines.append(f"  _{features_text}_")

                # Stock info
                stock_emoji = "✅" if product.quantity > 5 else "⚠️"
                lines.append(f"  {stock_emoji} {product.quantity} in stock")
                lines.append("")

        # Shopping route
        lines.append("## 🗺️ Shopping Route")
        lines.append("")
        lines.append("Follow this order for fastest shopping:")

        # Sort by aisle
        sorted_products = sorted(products, key=lambda p: p.aisle or "ZZZ")
        for i, product in enumerate(sorted_products, 1):
            location = f"Aisle {product.aisle}" if product.aisle else "Check store"
            lines.append(f"{i}. {location} → **{product.name}**")

        return "\n".join(lines)

    def _truncate_tutorial(self, tutorial: str) -> str:
        """Truncate tutorial for UI (first 500 chars)"""

        if not tutorial:
            return ""

        lines = ["---", "", "## 📖 Tutorial Preview", ""]

        # Take first 500 chars + complete sentence
        if len(tutorial) > 500:
            truncated = tutorial[:500]
            # Find last period
            last_period = truncated.rfind(".")
            if last_period > 0:
                truncated = truncated[: last_period + 1]
            lines.append(truncated + "\n\n_[Tutorial continues...]_")
        else:
            lines.append(tutorial)

        return "\n".join(lines)
