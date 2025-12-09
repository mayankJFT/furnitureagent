"""Furniture Sales Agent using OpenAI Agents SDK."""

from agents import Agent, function_tool
from furniture_catalog import (
    get_all_categories,
    get_items_by_category,
    get_item_by_id,
    search_items,
    get_items_by_price_range,
    format_item_details,
)

# Shopping cart to track items
shopping_cart: list[dict] = []


@function_tool
def browse_categories() -> str:
    """Browse all available furniture categories."""
    categories = get_all_categories()
    return f"Available furniture categories: {', '.join(cat.title() for cat in categories)}"


@function_tool
def browse_category(category: str) -> str:
    """Browse all items in a specific furniture category.

    Args:
        category: The furniture category to browse (e.g., sofas, chairs, tables, beds, storage)
    """
    items = get_items_by_category(category)
    if not items:
        return f"No items found in category '{category}'. Available categories: sofas, chairs, tables, beds, storage"

    result = f"**{category.title()}** ({len(items)} items):\n\n"
    for item in items:
        stock = "In Stock" if item["in_stock"] else "Out of Stock"
        result += f"- **{item['name']}** (ID: {item['id']}) - ${item['price']:.2f} - {stock}\n"
    return result


@function_tool
def get_product_details(product_id: str) -> str:
    """Get detailed information about a specific product.

    Args:
        product_id: The product ID (e.g., SF001, CH002, TB001)
    """
    item = get_item_by_id(product_id)
    if not item:
        return f"Product with ID '{product_id}' not found. Please check the ID and try again."
    return format_item_details(item)


@function_tool
def search_furniture(query: str) -> str:
    """Search for furniture by name, description, material, or color.

    Args:
        query: Search term (e.g., 'leather', 'wood', 'modern', 'gray')
    """
    items = search_items(query)
    if not items:
        return f"No items found matching '{query}'. Try different keywords."

    result = f"**Search results for '{query}'** ({len(items)} items):\n\n"
    for item in items:
        stock = "In Stock" if item["in_stock"] else "Out of Stock"
        result += f"- **{item['name']}** (ID: {item['id']}) - ${item['price']:.2f} - {stock}\n"
    return result


@function_tool
def filter_by_price(min_price: float, max_price: float) -> str:
    """Filter furniture by price range.

    Args:
        min_price: Minimum price in dollars
        max_price: Maximum price in dollars
    """
    items = get_items_by_price_range(min_price, max_price)
    if not items:
        return f"No items found in the price range ${min_price:.2f} - ${max_price:.2f}."

    result = f"**Items between ${min_price:.2f} - ${max_price:.2f}** ({len(items)} items):\n\n"
    for item in items:
        stock = "In Stock" if item["in_stock"] else "Out of Stock"
        result += f"- **{item['name']}** (ID: {item['id']}) - ${item['price']:.2f} - {stock}\n"
    return result


@function_tool
def add_to_cart(product_id: str, quantity: int = 1) -> str:
    """Add a product to the shopping cart.

    Args:
        product_id: The product ID to add
        quantity: Number of items to add (default: 1)
    """
    item = get_item_by_id(product_id)
    if not item:
        return f"Product with ID '{product_id}' not found."

    if not item["in_stock"]:
        return f"Sorry, **{item['name']}** is currently out of stock."

    # Check if item already in cart
    for cart_item in shopping_cart:
        if cart_item["id"] == item["id"]:
            cart_item["quantity"] += quantity
            return f"Updated quantity of **{item['name']}** to {cart_item['quantity']} in your cart."

    shopping_cart.append({
        "id": item["id"],
        "name": item["name"],
        "price": item["price"],
        "quantity": quantity
    })
    return f"Added {quantity}x **{item['name']}** (${item['price']:.2f}) to your cart."


@function_tool
def view_cart() -> str:
    """View the current shopping cart."""
    if not shopping_cart:
        return "Your shopping cart is empty."

    result = "**Your Shopping Cart:**\n\n"
    total = 0
    for item in shopping_cart:
        subtotal = item["price"] * item["quantity"]
        total += subtotal
        result += f"- {item['quantity']}x **{item['name']}** - ${item['price']:.2f} each = ${subtotal:.2f}\n"

    result += f"\n**Total: ${total:.2f}**"
    return result


@function_tool
def remove_from_cart(product_id: str) -> str:
    """Remove a product from the shopping cart.

    Args:
        product_id: The product ID to remove
    """
    product_id = product_id.upper()
    for i, item in enumerate(shopping_cart):
        if item["id"] == product_id:
            removed = shopping_cart.pop(i)
            return f"Removed **{removed['name']}** from your cart."
    return f"Product with ID '{product_id}' is not in your cart."


@function_tool
def clear_cart() -> str:
    """Clear all items from the shopping cart."""
    shopping_cart.clear()
    return "Your shopping cart has been cleared."


@function_tool
def checkout() -> str:
    """Process checkout and complete the order."""
    if not shopping_cart:
        return "Your cart is empty. Add some items before checking out."

    total = sum(item["price"] * item["quantity"] for item in shopping_cart)

    result = "**Order Summary:**\n\n"
    for item in shopping_cart:
        subtotal = item["price"] * item["quantity"]
        result += f"- {item['quantity']}x {item['name']} - ${subtotal:.2f}\n"

    result += f"\n**Total: ${total:.2f}**\n\n"
    result += "Thank you for your order! Your order has been placed successfully. "
    result += "You will receive a confirmation email shortly with delivery details."

    shopping_cart.clear()
    return result


# Create the furniture sales agent
furniture_agent = Agent(
    name="FurnitureSalesAgent",
    instructions="""You are a friendly and knowledgeable furniture sales assistant for "Home Haven Furniture Store".

Your role is to:
1. Help customers browse and discover furniture
2. Provide detailed product information
3. Make personalized recommendations based on customer needs
4. Assist with the shopping cart and checkout process

Guidelines:
- Be warm, professional, and helpful
- Ask clarifying questions to understand customer needs (room size, style preferences, budget)
- Proactively suggest complementary items
- Mention current availability and pricing
- If an item is out of stock, suggest similar alternatives
- Use the tools available to look up products and manage the cart

Available furniture categories: Sofas, Chairs, Tables, Beds, Storage

Remember to:
- Greet customers warmly
- Use product IDs when referencing specific items
- Summarize cart contents when items are added
- Confirm orders before checkout""",
    model="gpt-4o-mini",
    tools=[
        browse_categories,
        browse_category,
        get_product_details,
        search_furniture,
        filter_by_price,
        add_to_cart,
        view_cart,
        remove_from_cart,
        clear_cart,
        checkout,
    ],
)
