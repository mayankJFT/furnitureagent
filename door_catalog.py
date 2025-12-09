"""ProVia Doors catalog data loaded from test.json."""

import json
from pathlib import Path

# Load the catalog from test.json
CATALOG_PATH = Path(__file__).parent / "test.json"

with open(CATALOG_PATH, "r") as f:
    PROVIA_CATALOG = json.load(f)


def get_catalog_info() -> dict:
    """Get general catalog information."""
    return PROVIA_CATALOG.get("catalog_info", {})


def get_all_categories() -> list[str]:
    """Get all product categories."""
    categories = PROVIA_CATALOG.get("categories", {})
    return list(categories.keys())


def get_category_details(category_id: str) -> dict | None:
    """Get details about a specific category."""
    categories = PROVIA_CATALOG.get("categories", {})
    return categories.get(category_id)


def get_entry_door_series() -> list[str]:
    """Get all entry door series."""
    return PROVIA_CATALOG.get("categories", {}).get("entry_doors", {}).get("series", [])


def get_entry_door_product(series_id: str) -> dict | None:
    """Get details about a specific entry door series."""
    products = PROVIA_CATALOG.get("products", {}).get("entry_doors", {})
    return products.get(series_id)


def get_all_entry_doors() -> dict:
    """Get all entry door products."""
    return PROVIA_CATALOG.get("products", {}).get("entry_doors", {})


def get_glass_options() -> dict:
    """Get all glass options."""
    return PROVIA_CATALOG.get("products", {}).get("glass_options", {})


def get_glass_option(glass_id: str) -> dict | None:
    """Get a specific glass option."""
    glass_options = get_glass_options()
    return glass_options.get(glass_id)


def get_finishes() -> dict:
    """Get all finish options."""
    return PROVIA_CATALOG.get("products", {}).get("finishes", {})


def get_hardware_options() -> dict:
    """Get all hardware options."""
    return PROVIA_CATALOG.get("products", {}).get("hardware", {})


def get_hardware_option(hardware_id: str) -> dict | None:
    """Get a specific hardware option."""
    hardware = get_hardware_options()
    return hardware.get(hardware_id)


def get_accessories() -> dict:
    """Get all accessories."""
    return PROVIA_CATALOG.get("products", {}).get("accessories", {})


def get_frame_options() -> dict:
    """Get all frame options."""
    return PROVIA_CATALOG.get("products", {}).get("frame_options", {})


def get_patio_doors() -> dict:
    """Get patio door products."""
    return PROVIA_CATALOG.get("products", {}).get("patio_doors", {})


def get_storm_doors() -> dict:
    """Get storm door products."""
    return PROVIA_CATALOG.get("products", {}).get("storm_doors", {})


def get_impact_shield_info() -> dict:
    """Get Impact Shield product information."""
    return PROVIA_CATALOG.get("products", {}).get("impact_shield", {})


def get_warranties() -> dict:
    """Get warranty information."""
    return PROVIA_CATALOG.get("warranties", {})


def get_energy_star_info() -> dict:
    """Get Energy Star certification information."""
    return PROVIA_CATALOG.get("energy_star", {})


def get_customization_options() -> dict:
    """Get customization options."""
    return PROVIA_CATALOG.get("customization", {})


def get_regional_considerations() -> dict:
    """Get regional considerations."""
    return PROVIA_CATALOG.get("regional_considerations", {})


def get_relationships() -> dict:
    """Get product relationships (compatibility info)."""
    return PROVIA_CATALOG.get("relationships", {})


def search_products(query: str) -> list[dict]:
    """Search for products by keyword."""
    query = query.lower()
    results = []

    # Search entry doors
    entry_doors = get_all_entry_doors()
    for series_id, door in entry_doors.items():
        if (query in door.get("series", "").lower() or
            query in door.get("description", "").lower() or
            query in door.get("tier", "").lower() or
            query in series_id.lower()):
            results.append({
                "type": "entry_door",
                "id": series_id,
                "name": door.get("series"),
                "description": door.get("description"),
                "tier": door.get("tier")
            })

    # Search glass options
    glass_options = get_glass_options()
    for glass_id, glass in glass_options.items():
        if (query in glass.get("name", "").lower() or
            query in glass.get("description", "").lower() or
            query in glass_id.lower()):
            results.append({
                "type": "glass",
                "id": glass_id,
                "name": glass.get("name"),
                "description": glass.get("description")
            })

    # Search hardware
    hardware = get_hardware_options()
    for hw_id, hw in hardware.items():
        if (query in hw.get("name", "").lower() or
            query in hw.get("description", "").lower() or
            query in hw_id.lower()):
            results.append({
                "type": "hardware",
                "id": hw_id,
                "name": hw.get("name"),
                "description": hw.get("description")
            })

    # Search storm doors
    storm_doors = get_storm_doors()
    for storm_id, storm in storm_doors.items():
        if storm_id != "overview" and storm_id != "storm_door_hardware":
            if (query in storm.get("name", "").lower() or
                query in storm.get("description", "").lower() or
                query in storm_id.lower()):
                results.append({
                    "type": "storm_door",
                    "id": storm_id,
                    "name": storm.get("name"),
                    "description": storm.get("description"),
                    "tier": storm.get("tier")
                })

    return results


def get_compatible_hardware_for_door(door_series: str) -> list[str]:
    """Get compatible hardware for a door series."""
    relationships = get_relationships()
    door_hardware = relationships.get("entry_door_to_hardware", {})
    door_info = door_hardware.get(door_series, {})

    compatible = []
    if "optional" in door_info:
        compatible.extend(door_info["optional"])
    if "required" in door_info:
        compatible.extend([f"{hw} (required)" for hw in door_info["required"]])
    if "required_8ft" in door_info:
        compatible.extend([f"{hw} (required for 8ft)" for hw in door_info["required_8ft"]])

    return compatible


def get_compatible_glass_for_door(door_series: str) -> dict:
    """Get compatible glass options for a door series."""
    relationships = get_relationships()
    door_glass = relationships.get("entry_door_to_glass", {})
    return door_glass.get(door_series, {})


def get_compatible_frames_for_door(door_series: str) -> list[str]:
    """Get compatible frame options for a door series."""
    relationships = get_relationships()
    door_frame = relationships.get("entry_door_to_frame", {})
    return door_frame.get(door_series, {}).get("compatible", [])


def format_entry_door_summary(door: dict, series_id: str) -> str:
    """Format entry door details as a readable string."""
    energy_star = "Yes" if door.get("energy_star") else "No"

    result = f"""
**{door.get('series', series_id)}** ({door.get('tier', 'N/A')} Tier)

{door.get('description', 'No description available.')}

- **Energy Star Certified:** {energy_star}
- **U-Factor:** {door.get('u_factor', 'N/A')}
- **Warranty:** Finish - {door.get('warranty', {}).get('finish', 'N/A')}
- **Thickness:** {door.get('thickness', 'Standard')}

**Available Skins:** {', '.join(door.get('skin_options', ['N/A']))}

**Door Styles Available:** {len(door.get('door_styles', []))} styles
**Sidelite Options:** {len(door.get('sidelites', []))} options
"""
    return result


def format_glass_summary(glass: dict, glass_id: str) -> str:
    """Format glass option details as a readable string."""
    result = f"""
**{glass.get('name', glass_id)}**

{glass.get('description', 'No description available.')}

- **Warranty:** {glass.get('warranty', 'N/A')}
"""

    if "standard_options" in glass:
        result += "\n**Glass Packages:**\n"
        for opt in glass["standard_options"]:
            result += f"- {opt['code']}: {opt['type']} pane, {opt.get('gas', 'N/A')} gas, R-value {opt.get('r_value', 'N/A')}\n"

    if "styles" in glass:
        result += f"\n**Available Styles:** {len(glass['styles'])} decorative patterns\n"

    return result


def format_hardware_summary(hardware: dict, hw_id: str) -> str:
    """Format hardware option details as a readable string."""
    result = f"""
**{hardware.get('name', hw_id)}**

{hardware.get('description', 'No description available.')}

- **Warranty:** {hardware.get('warranty', 'N/A')}
"""

    if "finishes" in hardware:
        result += f"\n**Available Finishes:** {', '.join(hardware['finishes'])}\n"

    if "styles" in hardware:
        result += f"\n**Styles:** {', '.join(hardware['styles'])}\n"

    return result
