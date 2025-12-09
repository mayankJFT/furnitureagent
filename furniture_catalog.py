"""Furniture catalog data and helper functions."""

FURNITURE_CATALOG = {
    "sofas": [
        {
            "id": "SF001",
            "name": "Modern Leather Sofa",
            "price": 1299.99,
            "color": "Black",
            "material": "Genuine Leather",
            "dimensions": "84\"W x 36\"D x 34\"H",
            "in_stock": True,
            "description": "Sleek modern design with premium leather upholstery and chrome legs."
        },
        {
            "id": "SF002",
            "name": "Cozy Sectional Sofa",
            "price": 1899.99,
            "color": "Gray",
            "material": "Fabric",
            "dimensions": "112\"W x 85\"D x 33\"H",
            "in_stock": True,
            "description": "L-shaped sectional perfect for family rooms with reversible chaise."
        },
        {
            "id": "SF003",
            "name": "Mid-Century Velvet Sofa",
            "price": 999.99,
            "color": "Emerald Green",
            "material": "Velvet",
            "dimensions": "72\"W x 32\"D x 30\"H",
            "in_stock": False,
            "description": "Retro-inspired design with tufted back and tapered wooden legs."
        },
    ],
    "chairs": [
        {
            "id": "CH001",
            "name": "Executive Office Chair",
            "price": 449.99,
            "color": "Brown",
            "material": "Bonded Leather",
            "dimensions": "27\"W x 30\"D x 45\"H",
            "in_stock": True,
            "description": "Ergonomic design with lumbar support and adjustable height."
        },
        {
            "id": "CH002",
            "name": "Accent Armchair",
            "price": 349.99,
            "color": "Navy Blue",
            "material": "Linen",
            "dimensions": "28\"W x 30\"D x 32\"H",
            "in_stock": True,
            "description": "Classic wingback design perfect for reading corners."
        },
        {
            "id": "CH003",
            "name": "Dining Chair Set (4)",
            "price": 599.99,
            "color": "Walnut",
            "material": "Solid Wood",
            "dimensions": "18\"W x 20\"D x 36\"H",
            "in_stock": True,
            "description": "Set of 4 elegant wooden dining chairs with cushioned seats."
        },
    ],
    "tables": [
        {
            "id": "TB001",
            "name": "Farmhouse Dining Table",
            "price": 899.99,
            "color": "Rustic Brown",
            "material": "Reclaimed Wood",
            "dimensions": "72\"L x 38\"W x 30\"H",
            "in_stock": True,
            "description": "Seats 6-8 people. Handcrafted from reclaimed barn wood."
        },
        {
            "id": "TB002",
            "name": "Glass Coffee Table",
            "price": 299.99,
            "color": "Clear/Chrome",
            "material": "Tempered Glass",
            "dimensions": "48\"L x 24\"W x 18\"H",
            "in_stock": True,
            "description": "Modern minimalist design with tempered glass top and chrome frame."
        },
        {
            "id": "TB003",
            "name": "Standing Desk",
            "price": 549.99,
            "color": "White/Oak",
            "material": "Laminate/Steel",
            "dimensions": "60\"W x 30\"D x 28-48\"H",
            "in_stock": True,
            "description": "Electric height-adjustable desk with memory presets."
        },
    ],
    "beds": [
        {
            "id": "BD001",
            "name": "King Platform Bed",
            "price": 799.99,
            "color": "Espresso",
            "material": "Solid Wood",
            "dimensions": "King Size",
            "in_stock": True,
            "description": "Low-profile platform bed with built-in slat support. No box spring needed."
        },
        {
            "id": "BD002",
            "name": "Upholstered Queen Bed",
            "price": 649.99,
            "color": "Beige",
            "material": "Fabric/Wood",
            "dimensions": "Queen Size",
            "in_stock": True,
            "description": "Elegant tufted headboard with sturdy wooden frame."
        },
        {
            "id": "BD003",
            "name": "Canopy Bed Frame",
            "price": 1199.99,
            "color": "Matte Black",
            "material": "Metal",
            "dimensions": "Queen Size",
            "in_stock": False,
            "description": "Modern industrial canopy bed with clean lines."
        },
    ],
    "storage": [
        {
            "id": "ST001",
            "name": "6-Drawer Dresser",
            "price": 549.99,
            "color": "White",
            "material": "MDF/Solid Wood",
            "dimensions": "60\"W x 18\"D x 32\"H",
            "in_stock": True,
            "description": "Spacious dresser with soft-close drawers and modern hardware."
        },
        {
            "id": "ST002",
            "name": "Bookshelf",
            "price": 249.99,
            "color": "Natural Oak",
            "material": "Engineered Wood",
            "dimensions": "36\"W x 12\"D x 72\"H",
            "in_stock": True,
            "description": "5-shelf bookcase perfect for books and display items."
        },
        {
            "id": "ST003",
            "name": "TV Entertainment Center",
            "price": 699.99,
            "color": "Gray Wash",
            "material": "Wood/Glass",
            "dimensions": "65\"W x 16\"D x 24\"H",
            "in_stock": True,
            "description": "Fits TVs up to 70\". Includes cable management and storage cabinets."
        },
    ],
}


def get_all_categories() -> list[str]:
    """Get all furniture categories."""
    return list(FURNITURE_CATALOG.keys())


def get_items_by_category(category: str) -> list[dict]:
    """Get all items in a category."""
    category = category.lower()
    if category in FURNITURE_CATALOG:
        return FURNITURE_CATALOG[category]
    return []


def get_item_by_id(item_id: str) -> dict | None:
    """Get a specific item by its ID."""
    item_id = item_id.upper()
    for category in FURNITURE_CATALOG.values():
        for item in category:
            if item["id"] == item_id:
                return item
    return None


def search_items(query: str) -> list[dict]:
    """Search items by name, description, material, or color."""
    query = query.lower()
    results = []
    for category in FURNITURE_CATALOG.values():
        for item in category:
            if (query in item["name"].lower() or
                query in item["description"].lower() or
                query in item["material"].lower() or
                query in item["color"].lower()):
                results.append(item)
    return results


def get_items_by_price_range(min_price: float, max_price: float) -> list[dict]:
    """Get items within a price range."""
    results = []
    for category in FURNITURE_CATALOG.values():
        for item in category:
            if min_price <= item["price"] <= max_price:
                results.append(item)
    return results


def format_item_details(item: dict) -> str:
    """Format item details as a readable string."""
    stock_status = "In Stock" if item["in_stock"] else "Out of Stock"
    return f"""
**{item['name']}** (ID: {item['id']})
- Price: ${item['price']:.2f}
- Color: {item['color']}
- Material: {item['material']}
- Dimensions: {item['dimensions']}
- Status: {stock_status}
- Description: {item['description']}
"""
