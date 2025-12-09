"""ProVia Doors Sales Agent using OpenAI Agents SDK."""

from agents import Agent, function_tool
from door_catalog import (
    get_catalog_info,
    get_all_categories,
    get_category_details,
    get_entry_door_series,
    get_entry_door_product,
    get_all_entry_doors,
    get_glass_options,
    get_glass_option,
    get_finishes,
    get_hardware_options,
    get_hardware_option,
    get_accessories,
    get_frame_options,
    get_patio_doors,
    get_storm_doors,
    get_impact_shield_info,
    get_warranties,
    get_energy_star_info,
    get_customization_options,
    get_regional_considerations,
    search_products,
    get_compatible_hardware_for_door,
    get_compatible_glass_for_door,
    get_compatible_frames_for_door,
    format_entry_door_summary,
    format_glass_summary,
    format_hardware_summary,
)


@function_tool
def get_company_info() -> str:
    """Get information about ProVia company and the catalog."""
    info = get_catalog_info()
    stats = info.get("stats", {})
    return f"""
**{info.get('name', 'ProVia Doors Catalog')}** - {info.get('year', '')}

{info.get('description', '')}

**Company:** {info.get('company', 'ProVia')} - "{info.get('tagline', '')}"

**Key Stats:**
- Energy Star Certified: {stats.get('energy_star_certified', 'N/A')}
- US Facilities: {stats.get('facilities_us', 'N/A')}
- Associates: {stats.get('associates', 'N/A')}
- In business since: {stats.get('since', 'N/A')}

**Associations:** {', '.join(info.get('associations', []))}
"""


@function_tool
def list_product_categories() -> str:
    """List all available product categories."""
    categories = get_all_categories()
    result = "**Available Product Categories:**\n\n"
    for cat in categories:
        details = get_category_details(cat)
        if details:
            name = details.get("name", cat.replace("_", " ").title())
            result += f"- **{name}** (ID: {cat})\n"
    return result


@function_tool
def get_entry_door_options() -> str:
    """Get all entry door series/options available."""
    series_list = get_entry_door_series()
    doors = get_all_entry_doors()

    result = "**Entry Door Series:**\n\n"
    for series_id in series_list:
        door = doors.get(series_id, {})
        tier = door.get("tier", "N/A")
        desc = door.get("description", "")[:100] + "..." if len(door.get("description", "")) > 100 else door.get("description", "")
        energy = "Energy Star" if door.get("energy_star") else ""
        result += f"**{door.get('series', series_id)}** ({tier}) {energy}\n{desc}\n\n"

    return result


@function_tool
def get_entry_door_details(series: str) -> str:
    """Get detailed information about a specific entry door series.

    Args:
        series: The door series ID (embarq, signet, heritage, or legacy)
    """
    series = series.lower()
    door = get_entry_door_product(series)
    if not door:
        return f"Door series '{series}' not found. Available series: embarq, signet, heritage, legacy"

    return format_entry_door_summary(door, series)


@function_tool
def get_door_styles(series: str) -> str:
    """Get available door styles for a specific series.

    Args:
        series: The door series ID (embarq, signet, heritage, or legacy)
    """
    series = series.lower()
    door = get_entry_door_product(series)
    if not door:
        return f"Door series '{series}' not found."

    styles = door.get("door_styles", [])
    result = f"**Door Styles for {door.get('series', series)}:**\n\n"

    with_glass = [s for s in styles if s.get("glass")]
    without_glass = [s for s in styles if not s.get("glass")]

    result += f"**With Glass ({len(with_glass)} styles):**\n"
    result += ", ".join([s["code"] for s in with_glass[:15]])
    if len(with_glass) > 15:
        result += f"... and {len(with_glass) - 15} more"

    result += f"\n\n**Without Glass ({len(without_glass)} styles):**\n"
    result += ", ".join([s["code"] for s in without_glass])

    return result


@function_tool
def get_door_skin_options(series: str) -> str:
    """Get available skin/texture options for a door series.

    Args:
        series: The door series ID
    """
    series = series.lower()
    door = get_entry_door_product(series)
    if not door:
        return f"Door series '{series}' not found."

    skins = door.get("skin_options", [])
    return f"**Skin Options for {door.get('series', series)}:**\n\n" + ", ".join(skins)


@function_tool
def get_glass_options_list() -> str:
    """Get all available glass options."""
    glass_opts = get_glass_options()
    result = "**Glass Options:**\n\n"

    for glass_id, glass in glass_opts.items():
        name = glass.get("name", glass_id)
        desc = glass.get("description", "")[:80] + "..." if len(glass.get("description", "")) > 80 else glass.get("description", "")
        result += f"**{name}** (ID: {glass_id})\n{desc}\n\n"

    return result


@function_tool
def get_glass_details(glass_id: str) -> str:
    """Get detailed information about a specific glass option.

    Args:
        glass_id: The glass option ID (e.g., comfortech_glazing, decorative_glass, privacy_glass)
    """
    glass = get_glass_option(glass_id.lower())
    if not glass:
        return f"Glass option '{glass_id}' not found. Use get_glass_options_list() to see available options."

    return format_glass_summary(glass, glass_id)


@function_tool
def get_decorative_glass_styles() -> str:
    """Get all decorative glass pattern styles available."""
    glass = get_glass_option("decorative_glass")
    if not glass:
        return "Decorative glass information not available."

    styles = glass.get("styles", [])
    result = "**Decorative Glass Styles:**\n\n"

    for style in styles:
        name = style.get("name", "")
        privacy = style.get("privacy", "N/A")
        caming = ", ".join(style.get("caming", []))
        new_tag = " NEW!" if style.get("new") else ""
        result += f"- **{name}**{new_tag} - Privacy: {privacy}/10, Caming: {caming}\n"

    return result


@function_tool
def get_hardware_options_list() -> str:
    """Get all available hardware options."""
    hardware = get_hardware_options()
    result = "**Hardware Options:**\n\n"

    for hw_id, hw in hardware.items():
        name = hw.get("name", hw_id)
        desc = hw.get("description", "")[:80] + "..." if len(hw.get("description", "")) > 80 else hw.get("description", "")
        result += f"**{name}** (ID: {hw_id})\n{desc}\n\n"

    return result


@function_tool
def get_hardware_details(hardware_id: str) -> str:
    """Get detailed information about a specific hardware option.

    Args:
        hardware_id: The hardware ID (e.g., trilennium_multipoint, emtek_mortise, schlage_electronic)
    """
    hw = get_hardware_option(hardware_id.lower())
    if not hw:
        return f"Hardware option '{hardware_id}' not found. Use get_hardware_options_list() to see available options."

    return format_hardware_summary(hw, hardware_id)


@function_tool
def get_finish_options() -> str:
    """Get all available finish options (stain, paint, glazed)."""
    finishes = get_finishes()
    result = "**Finish Options:**\n\n"

    for finish_id, finish in finishes.items():
        name = finish.get("name", finish_id)
        desc = finish.get("description", "")
        result += f"**{name}**\n{desc}\n\n"

        # Show colors if available
        if "colors" in finish:
            result += f"Colors: {', '.join(finish['colors'][:8])}"
            if len(finish.get('colors', [])) > 8:
                result += f"... and {len(finish['colors']) - 8} more"
            result += "\n"

        if "standard_colors" in finish:
            result += f"Standard Colors: {', '.join(finish['standard_colors'][:8])}"
            if len(finish.get('standard_colors', [])) > 8:
                result += f"... and more"
            result += "\n"

        result += "\n"

    return result


@function_tool
def get_storm_door_options() -> str:
    """Get all storm door series and options."""
    storm = get_storm_doors()
    result = "**Storm Door Series:**\n\n"

    for storm_id, door in storm.items():
        if storm_id not in ["overview", "storm_door_hardware"]:
            name = door.get("name", storm_id)
            tier = door.get("tier", "")
            desc = door.get("description", "")
            result += f"**{name}** ({tier})\n{desc}\n\n"

    return result


@function_tool
def get_patio_door_options() -> str:
    """Get patio door options."""
    patio = get_patio_doors()
    result = "**Patio Door Options:**\n\n"

    for patio_id, door in patio.items():
        name = door.get("name", patio_id)
        desc = door.get("description", "")
        result += f"**{name}**\n{desc}\n\n"

        if "configurations" in door:
            result += f"Configurations: {', '.join(door['configurations'])}\n"

        result += "\n"

    return result


@function_tool
def get_frame_options_list() -> str:
    """Get all frame options available."""
    frames = get_frame_options()
    result = "**Frame Options:**\n\n"

    for frame_id, frame in frames.items():
        name = frame.get("name", frame_id)
        desc = frame.get("description", "")
        warranty = frame.get("warranty", "N/A")
        result += f"**{name}**\n{desc}\nWarranty: {warranty}\n\n"

    return result


@function_tool
def check_compatibility(door_series: str) -> str:
    """Check what hardware, glass, and frames are compatible with a door series.

    Args:
        door_series: The door series ID (embarq, signet, heritage, or legacy)
    """
    door_series = door_series.lower()
    door = get_entry_door_product(door_series)
    if not door:
        return f"Door series '{door_series}' not found."

    result = f"**Compatibility for {door.get('series', door_series)}:**\n\n"

    # Hardware
    hardware = get_compatible_hardware_for_door(door_series)
    result += "**Compatible Hardware:**\n"
    result += ", ".join(hardware) if hardware else "All hardware types"
    result += "\n\n"

    # Glass
    glass = get_compatible_glass_for_door(door_series)
    result += "**Glass Options:**\n"
    if glass:
        result += f"- Glazing: {', '.join(glass.get('glazing', []))}\n"
        result += f"- Decorative: {glass.get('decorative', 'N/A')}\n"
        result += f"- Dialogue Glass: {'Yes' if glass.get('dialogue') else 'No'}\n"
        result += f"- Internal Blinds: {'Yes' if glass.get('internal_blinds') else 'No'}\n"
    result += "\n"

    # Frames
    frames = get_compatible_frames_for_door(door_series)
    result += "**Compatible Frames:**\n"
    result += ", ".join(frames) if frames else "Standard frames"

    return result


@function_tool
def get_warranty_info(product_type: str = "all") -> str:
    """Get warranty information for products.

    Args:
        product_type: Type of product (entry_doors, glass, hardware, storm_doors, patio_doors, or all)
    """
    warranties = get_warranties()

    if product_type.lower() == "all":
        result = "**ProVia Warranty Information:**\n\n"
        for category, items in warranties.items():
            result += f"**{category.replace('_', ' ').title()}:**\n"
            if isinstance(items, dict):
                for item, warranty in items.items():
                    result += f"- {item.replace('_', ' ').title()}: {warranty}\n"
            else:
                result += f"- {items}\n"
            result += "\n"
        return result
    else:
        category_warranties = warranties.get(product_type.lower())
        if not category_warranties:
            return f"No warranty info found for '{product_type}'"

        result = f"**{product_type.replace('_', ' ').title()} Warranties:**\n\n"
        if isinstance(category_warranties, dict):
            for item, warranty in category_warranties.items():
                result += f"- {item.replace('_', ' ').title()}: {warranty}\n"
        else:
            result += f"- {category_warranties}\n"
        return result


@function_tool
def get_energy_star_details() -> str:
    """Get Energy Star certification details."""
    energy = get_energy_star_info()

    result = f"""**Energy Star Certification:**

ProVia has **{energy.get('certification_rate', '90%+')}** of products Energy Star certified.

**By Door Series:**
- Embarq: {'All certified' if energy.get('embarq', {}).get('all_certified') else 'Most certified'}
- Signet: {'Most certified' if energy.get('signet', {}).get('most_certified') else 'Check specific models'}
- Heritage: {'Most certified' if energy.get('heritage', {}).get('most_certified') else 'Check specific models'}
- Legacy: {'Most certified' if energy.get('legacy', {}).get('most_certified') else 'Check specific models'}

**Vinyl Sliding Patio Doors:** {'All certified' if energy.get('vinyl_sliding_patio', {}).get('all_certified') else 'Check models'}
**Doors Without Glass:** {'All certified' if energy.get('doors_without_glass', {}).get('all_certified') else 'Check models'}

**Products NOT Energy Star Certified:**
{', '.join(energy.get('not_energy_star', []))}
"""
    return result


@function_tool
def search_provia_products(query: str) -> str:
    """Search for ProVia products by keyword.

    Args:
        query: Search term (e.g., 'fiberglass', 'steel', 'premium', 'security')
    """
    results = search_products(query)

    if not results:
        return f"No products found matching '{query}'. Try different keywords like: fiberglass, steel, premium, decorative, electronic, security"

    response = f"**Search Results for '{query}':** ({len(results)} found)\n\n"

    for item in results[:10]:
        response += f"**{item.get('name', item['id'])}** ({item['type'].replace('_', ' ').title()})\n"
        if item.get('tier'):
            response += f"Tier: {item['tier']}\n"
        response += f"{item.get('description', '')[:100]}...\n\n"

    if len(results) > 10:
        response += f"...and {len(results) - 10} more results"

    return response


@function_tool
def get_regional_requirements(region: str) -> str:
    """Get regional requirements and considerations.

    Args:
        region: Region type (impact_shield, certified_wind_load, high_altitude, coastal, northern_climate)
    """
    regions = get_regional_considerations()
    region_info = regions.get(region.lower())

    if not region_info:
        available = list(regions.keys())
        return f"Region '{region}' not found. Available: {', '.join(available)}"

    result = f"**{region.replace('_', ' ').title()} Requirements:**\n\n"

    for key, value in region_info.items():
        if isinstance(value, list):
            result += f"**{key.replace('_', ' ').title()}:**\n"
            for item in value:
                result += f"- {item}\n"
        else:
            result += f"**{key.replace('_', ' ').title()}:** {value}\n"
        result += "\n"

    return result


@function_tool
def get_customization_info() -> str:
    """Get information about customization options available."""
    custom = get_customization_options()

    result = "**Customization Options:**\n\n"

    # Sizing
    sizing = custom.get("sizing", {})
    result += "**Custom Sizing:**\n"
    for series, options in sizing.items():
        widths = "Yes" if options.get("custom_widths") else "No"
        heights = "Yes" if options.get("custom_heights") else "No"
        increment = options.get("increment", "N/A")
        result += f"- {series.title()}: Widths: {widths}, Heights: {heights}, Increment: {increment}\n"

    result += "\n**Dual Finish:**\n"
    dual = custom.get("dual_finish", {})
    result += f"Available on: {', '.join(dual.get('available_on', []))}\n"
    result += f"Note: {dual.get('note', 'N/A')}\n"

    result += "\n**Custom Colors:**\n"
    colors = custom.get("custom_colors", {})
    result += f"Paint: {'Available' if colors.get('paint') else 'No'}\n"
    result += f"Stain: {colors.get('stain', 'N/A')}\n"
    result += f"Lead Time: {colors.get('lead_time', 'N/A')}\n"

    return result


# Create the ProVia sales agent
provia_agent = Agent(
    name="ProViaDoorsSalesAgent",
    instructions="""You are a knowledgeable and friendly sales consultant for ProVia Doors - "The Professional Way".

ProVia is a family-owned, faith-based company that has been producing Professional-Class doors since 1977. Over 90% of our products are Energy Star certified.

Your role is to:
1. Help customers understand and choose the right door products for their needs
2. Explain product features, benefits, and differences between series
3. Guide customers through options: entry doors, storm doors, patio doors, glass, hardware, finishes
4. Provide information about warranties, Energy Star certification, and regional requirements
5. Check compatibility between door series and hardware/glass/frame options

**Entry Door Series (from Premium to Value):**
- **Embarq** - Premium 2.5" thick fiberglass, highest efficiency, Quad Glass System
- **Signet** - Premium fiberglass with dovetailed construction, most customizable
- **Heritage** - Mid-range fiberglass with enhanced woodgrain texture
- **Legacy** - Value 20-gauge steel, 49% more steel than standard

**Key Talking Points:**
- ComforTech Warm Edge Glazing System for superior thermal performance
- DuraFuse finishing system for premium doors
- FrameSaver composite bottom that never rots
- Wide variety of decorative glass patterns
- Multiple hardware options from multi-point to electronic locks

**Guidelines:**
- Be warm, professional, and consultative
- Ask clarifying questions about customer needs (style, climate, budget, security)
- Proactively mention Energy Star certification and warranty coverage
- For coastal/hurricane areas, mention Impact Shield products
- Always use the tools to provide accurate product information
- Keep responses conversational but informative for voice interaction""",
    model="gpt-4o-mini",
    tools=[
        get_company_info,
        list_product_categories,
        get_entry_door_options,
        get_entry_door_details,
        get_door_styles,
        get_door_skin_options,
        get_glass_options_list,
        get_glass_details,
        get_decorative_glass_styles,
        get_hardware_options_list,
        get_hardware_details,
        get_finish_options,
        get_storm_door_options,
        get_patio_door_options,
        get_frame_options_list,
        check_compatibility,
        get_warranty_info,
        get_energy_star_details,
        search_provia_products,
        get_regional_requirements,
        get_customization_info,
    ],
)
