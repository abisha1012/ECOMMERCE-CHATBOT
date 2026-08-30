from flask import Flask, render_template, request, jsonify

from nlp_model import predict_intent

from database import (
    get_order,
    get_product,
    save_chat,
    get_chat_history,
    clear_chat_history
)

import re


app = Flask(__name__)


# ==================================================
# EXTRACT ORDER ID
# ==================================================

def extract_order_id(message):

    pattern = r"\b(?:ORD|ORDER)[-_]?\d+\b"

    match = re.search(
        pattern,
        message.upper()
    )

    if match:

        order_id = match.group(0)

        order_id = order_id.replace("-", "")
        order_id = order_id.replace("_", "")

        if order_id.startswith("ORDER"):

            order_id = "ORD" + order_id[5:]

        return order_id

    return None


# ==================================================
# FIND PRODUCT NAME
# ==================================================

def find_product_name(message):

    products = [
        "Smart Watch",
        "Wireless Headphones",
        "Smartphone",
        "Laptop",
        "Bluetooth Speaker"
    ]

    message_lower = message.lower()

    for product in products:

        if product.lower() in message_lower:

            return product

    return None


# ==================================================
# CHATBOT RESPONSE
# ==================================================

def chatbot_response(message):

    detected_intent = predict_intent(message)

    order_id = extract_order_id(message)

    product_name = find_product_name(message)


    # ------------------------------------------------
    # GREETING
    # ------------------------------------------------

    if detected_intent == "greeting":

        return (
            "Hello! 👋 Welcome to our online store.<br><br>"
            "I am your AI customer support assistant.<br>"
            "How can I help you today?"
        )


    # ------------------------------------------------
    # PRODUCT
    # ------------------------------------------------

    elif detected_intent == "product":

        if product_name is None:

            return (
                "Please enter a product name.<br><br>"
                "<b>Available Products:</b><br>"
                "• Smart Watch<br>"
                "• Wireless Headphones<br>"
                "• Smartphone<br>"
                "• Laptop<br>"
                "• Bluetooth Speaker"
            )

        product = get_product(product_name)

        if product:

            name, price, stock = product

            if stock > 0:

                availability = "Product is currently available."

            else:

                availability = "Product is currently out of stock."

            return (
                "📦 <b>Product Found!</b><br><br>"
                f"Product Name: {name}<br>"
                f"Price: ₹{price:.0f}<br>"
                f"Available Stock: {stock}<br>"
                f"{availability}"
            )

        return "Sorry, product not found."


    # ------------------------------------------------
    # ORDER TRACKING
    # ------------------------------------------------

    elif detected_intent == "order_tracking":

        if not order_id:

            return (
                "📦 Please enter your Order ID.<br><br>"
                "Example: <b>ORD1001</b>"
            )

        order = get_order(order_id)

        if order:

            customer, product, order_date, delivery_date, status = order

            return (
                "📦 <b>Order Found!</b><br><br>"
                f"Customer: {customer}<br>"
                f"Product: {product}<br>"
                f"Order Date: {order_date}<br>"
                f"Expected Delivery: {delivery_date}<br>"
                f"Current Status: <b>{status}</b>"
            )

        return "❌ Sorry, Order ID not found."


    # ------------------------------------------------
    # DELIVERY
    # ------------------------------------------------

    elif detected_intent == "delivery":

        if not order_id:

            return (
                "🚚 Please enter your Order ID.<br><br>"
                "Example: <b>ORD1001</b>"
            )

        order = get_order(order_id)

        if order:

            customer, product, order_date, delivery_date, status = order

            return (
                "🚚 <b>Delivery Information</b><br><br>"
                f"Product: {product}<br>"
                f"Current Status: <b>{status}</b><br>"
                f"Expected Delivery: {delivery_date}"
            )

        return "❌ Sorry, Order ID not found."


    # ------------------------------------------------
    # RETURN
    # ------------------------------------------------

    elif detected_intent == "return":

        if not order_id:

            return (
                "🔄 Please enter your Order ID "
                "to request a return.<br><br>"
                "Example: <b>ORD1002</b>"
            )

        order = get_order(order_id)

        if not order:

            return "❌ Sorry, Order ID not found."

        customer, product, order_date, delivery_date, status = order

        if status.lower() == "delivered":

            return (
                "🔄 <b>Return Request</b><br><br>"
                f"Product: {product}<br>"
                "✅ This product is eligible for return.<br><br>"
                "Please contact customer support "
                "to start the return process."
            )

        return (
            f"The order is currently <b>{status}</b>.<br>"
            "Return can be requested after delivery."
        )


    # ------------------------------------------------
    # REFUND
    # ------------------------------------------------

    elif detected_intent == "refund":

        if not order_id:

            return (
                "💰 Please enter your Order ID "
                "to request a refund.<br><br>"
                "Example: <b>ORD1002</b>"
            )

        order = get_order(order_id)

        if not order:

            return "❌ Sorry, Order ID not found."

        customer, product, order_date, delivery_date, status = order

        if status.lower() == "delivered":

            return (
                "💰 <b>Refund Request</b><br><br>"
                f"Product: {product}<br>"
                "✅ Your refund request can be raised.<br><br>"
                "The returned product will be verified "
                "before the refund is processed."
            )

        return (
            "This order has not been delivered yet.<br>"
            "Refund cannot be requested at this stage."
        )


    # ------------------------------------------------
    # CANCELLATION
    # ------------------------------------------------

    elif detected_intent == "cancellation":

        if not order_id:

            return (
                "❌ Please enter your Order ID "
                "to cancel the order.<br><br>"
                "Example: <b>ORD1003</b>"
            )

        order = get_order(order_id)

        if not order:

            return "❌ Sorry, Order ID not found."

        customer, product, order_date, delivery_date, status = order

        if status.lower() == "processing":

            return (
                "❌ <b>Order Cancellation</b><br><br>"
                f"Product: {product}<br>"
                "✅ This order can be cancelled."
            )

        return (
            f"This order cannot be cancelled because "
            f"its current status is <b>{status}</b>."
        )


    # ------------------------------------------------
    # PAYMENT
    # ------------------------------------------------

    elif detected_intent == "payment":

        return (
            "💳 <b>Payment Support</b><br><br>"
            "If your payment failed:<br>"
            "1. Check your internet connection.<br>"
            "2. Check your payment details.<br>"
            "3. Try the payment again.<br>"
            "4. Contact customer support if the problem continues."
        )


    # ------------------------------------------------
    # HELP
    # ------------------------------------------------

    elif detected_intent == "help":

        return (
            "🤖 <b>I can help you with:</b><br><br>"
            "📦 Product information<br>"
            "🔍 Order tracking<br>"
            "🚚 Delivery information<br>"
            "🔄 Returns<br>"
            "💰 Refunds<br>"
            "❌ Cancellation<br>"
            "💳 Payment support"
        )


    # ------------------------------------------------
    # GOODBYE
    # ------------------------------------------------

    elif detected_intent == "goodbye":

        return (
            "Thank you for contacting us! 😊<br>"
            "Have a great day!"
        )


    # ------------------------------------------------
    # UNKNOWN
    # ------------------------------------------------

    return (
        "Sorry, I didn't understand your question. 🤔<br><br>"
        "You can ask me about:<br>"
        "📦 Products<br>"
        "🔍 Orders<br>"
        "🚚 Delivery<br>"
        "🔄 Returns<br>"
        "💰 Refunds<br>"
        "❌ Cancellation<br>"
        "💳 Payment"
    )


# ==================================================
# HOME PAGE
# ==================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==================================================
# CHAT API
# ==================================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    data = request.get_json()

    message = data.get(
        "message",
        ""
    ).strip()


    if not message:

        return jsonify({
            "response":
            "Please enter a message."
        })


    # Detect intent ONCE
    detected_intent = predict_intent(
        message
    )


    # Generate response
    response = chatbot_response(
        message
    )


    # Save all three values
    save_chat(
        message,
        response,
        detected_intent
    )


    return jsonify({
        "response": response
    })


# ==================================================
# CHAT HISTORY
# ==================================================

@app.route(
    "/history",
    methods=["GET"]
)
def history():

    chats = get_chat_history()

    history_data = []


    for user_message, bot_response, timestamp in chats:

        history_data.append({

            "user":
                user_message,

            "bot":
                bot_response,

            "time":
                timestamp

        })


    return jsonify(
        history_data
    )


# ==================================================
# CLEAR CHAT HISTORY
# ==================================================

@app.route(
    "/clear-history",
    methods=["POST"]
)
def clear_history():

    clear_chat_history()

    return jsonify({

        "success":
            True

    })


# ==================================================
# START APPLICATION
# ==================================================

if __name__ == "__main__":

    print()

    print("==============================================")
    print("      E-COMMERCE CHATBOT WEB APPLICATION")
    print("==============================================")

    print()

    print("Server starting...")

    print("Open your browser and visit:")

    print(
        "http://127.0.0.1:5000"
    )

    print()

    app.run(
        debug=False
    )