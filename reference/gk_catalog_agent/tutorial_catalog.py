"""
Tutorial Catalog - Hardcoded shelf tutorials for GK demo

Simple approach:
- 3 predefined shelf types
- Metadata (name, difficulty, cost, materials)
- Tutorial markdown files in same folder
"""

from pathlib import Path
from typing import Any

TUTORIALS = {
    "floating_kitchen_shelves": {
        "name": "Floating Kitchen Shelves",
        "difficulty": "Medium",
        "cost": 60,
        "time": "3-4 hours + finish cure",
        "description": "2× 90cm floating shelves for plates and jars",
        "materials": [
            "12mm sanded plywood sheet",
            "19×64mm select pine (2.4m)",
            "19×38mm pine (4.8m)",
            "32mm wood screws",
            "65-75mm wood screws for studs",
            "Wood glue",
            "Sandpaper (120/180/220 grit)",
            "Stain or paint + clear topcoat",
        ],
        "tutorial_file": "floating_kitchen_shelves.md",
    },
    "bracketed_open_shelving": {
        "name": "Bracketed Open Shelving",
        "difficulty": "Easy",
        "cost": 50,
        "time": "2 hours",
        "description": "Adjustable rail-and-bracket system with solid wood shelves",
        "materials": [
            "2× solid wood boards 1200×250×19-25mm",
            "2× steel wall standards (rails) 1000-1200mm",
            "4-6× adjustable brackets (20-40kg rated)",
            "65-75mm screws for studs",
            "20-25mm wood screws",
            "Wood finish (oil/poly/paint)",
            "Sandpaper",
        ],
        "tutorial_file": "bracketed_open_shelving.md",
    },
    "freestanding_pantry_cabinet": {
        "name": "Freestanding Pantry Cabinet",
        "difficulty": "Advanced",
        "cost": 120,
        "time": "6-8 hours + finish",
        "description": "800×400×1800mm cabinet with adjustable shelves",
        "materials": [
            "19mm plywood (2 full sheets 2440×1220mm)",
            "6mm plywood/hardboard for back panel",
            "Edge banding (optional)",
            "Pocket screws (32-38mm)",
            "Wood screws (30-40mm, 50mm)",
            "Wood glue",
            "Adjustable shelf pins",
            "4× leveling feet (optional)",
            "Paint or clear coat + primer",
        ],
        "tutorial_file": "freestanding_pantry_cabinet.md",
    },
}


def get_shelf_options() -> list[dict[str, Any]]:
    """
    Return formatted shelf options for HITL presentation

    Returns:
        List of options with id, label, and metadata
    """
    return [
        {
            "id": key,
            "label": f"{data['name']} - {data['difficulty']}, ~€{data['cost']}",
            "name": data["name"],
            "difficulty": data["difficulty"],
            "cost": data["cost"],
            "time": data["time"],
            "description": data["description"],
        }
        for key, data in TUTORIALS.items()
    ]


def get_tutorial(shelf_id: str) -> str:
    """
    Load tutorial markdown content

    Args:
        shelf_id: Tutorial ID (e.g., "floating_spice_shelf")

    Returns:
        Full tutorial markdown as string
    """
    if shelf_id not in TUTORIALS:
        raise ValueError(f"Unknown shelf type: {shelf_id}")

    tutorial_file = TUTORIALS[shelf_id]["tutorial_file"]
    tutorial_path = Path(__file__).parent / "tutorials" / tutorial_file

    # Fallback if file doesn't exist yet
    if not tutorial_path.exists():
        return _get_fallback_tutorial(shelf_id)

    with open(tutorial_path, encoding="utf-8") as f:
        return f.read()


def get_materials(shelf_id: str) -> list[str]:
    """
    Get materials list for a shelf type

    Args:
        shelf_id: Tutorial ID

    Returns:
        List of material names/descriptions
    """
    if shelf_id not in TUTORIALS:
        raise ValueError(f"Unknown shelf type: {shelf_id}")

    return TUTORIALS[shelf_id]["materials"]


def get_shelf_metadata(shelf_id: str) -> dict[str, Any]:
    """
    Get all metadata for a shelf type

    Args:
        shelf_id: Tutorial ID

    Returns:
        Dictionary with name, difficulty, cost, etc.
    """
    if shelf_id not in TUTORIALS:
        raise ValueError(f"Unknown shelf type: {shelf_id}")

    return TUTORIALS[shelf_id]


def _get_fallback_tutorial(shelf_id: str) -> str:
    """Fallback tutorial if markdown file doesn't exist yet"""
    metadata = TUTORIALS[shelf_id]

    materials_list = "\n".join([f"- {mat}" for mat in metadata["materials"]])

    return f"""# {metadata["name"]}

**Difficulty:** {metadata["difficulty"]}
**Time:** {metadata["time"]}
**Cost:** ~€{metadata["cost"]}

## Description
{metadata["description"]}

## Materials Needed
{materials_list}

## Tools Required
- Measuring tape
- Pencil
- Safety glasses
- Your existing tools

## Step-by-Step Instructions

### Step 1: Measure and Plan
1. Choose your location
2. Measure the space
3. Mark mounting points

### Step 2: Prepare Materials
1. Lay out all materials
2. Check you have everything
3. Read safety instructions

### Step 3: Cut and Prepare
1. Cut board to size if needed
2. Sand edges smooth
3. Clean surface

### Step 4: Apply Adhesive
1. Apply adhesive evenly
2. Follow product instructions
3. Allow proper cure time

### Step 5: Mount and Secure
1. Position shelf carefully
2. Press firmly
3. Add screws for extra support
4. Use your cordless screwdriver

### Step 6: Finishing
1. Clean excess adhesive
2. Check stability
3. Allow full cure time (24 hours)

## Safety Tips
⚠️ Use in well-ventilated area
⚠️ Wear safety glasses
⚠️ Read all product labels
⚠️ Keep away from children during installation

## Maintenance
- Check mounting every 6 months
- Wipe clean with damp cloth
- Don't overload

---

**Enjoy your new {metadata["name"].lower()}!** 🎉
"""
