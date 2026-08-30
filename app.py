import sqlite3
import re

from nlp_model import predict_intent


DATABASE = "ecommerce.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def save_chat_history(user_message, detected_intent, bot_response):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO chat_history
        (user_message, detected_intent, bot_response)
        VALUES (?, ?, ?)
    """, (
        user_message,
        detected_intent,
        bot_response
    ))

    connection.commit()
    connection.close()


def view_chat_history():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            user_message,
            detected_intent,
            bot_response,
            timestamp
        FROM chat_history
        ORDER BY id
    """)

    history = cursor.fetchall()

    connection.close()

    print()
    print("==============================================")
    print("                CHAT HISTORY")
    print("==============================================")

    if not history:
        print("No conversation history found.")

    else:

        for row in history:

            print()
            print("ID:", row[0])
            print("User:", row[1])
            print("Intent:", row[2])
            print("Bot:", row[3])
            print("Time:", row[4])

    print()


def get_product(product_name):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT product_name, price, stock
        FROM products
        WHERE LOWER(product_name) LIKE ?
    """, (
        "%" + product_name.lower() + "%",
    ))

    product = cursor.fetchone()

    connection.close()

    return product


def get_all_products():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT product_name
        FROM products
    """)

    products = cursor.fetchall()

    connection.close()

    return products


def get_order(order_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            customer_name,
            product_name,
            order_date,
            delivery_date,
            status
        FROM orders
        WHERE UPPER(order_id) = ?
    """, (
        order_id.upper(),
    ))

    order = cursor.fetchone()

    connection.close()

    return order


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


def extract_product_name(message):

    products = get_all_products()

    message_lower = message.lower()

    for product in products:

        product_name = product[0]

        if product_name.lower() in message_lower:
            return product_name

    return None


def greeting():

    response = "Hello! How can I help you?"

    print("Bot:", response)

    return response


def product_enquiry(product_name=None):

    if product_name is None:

        product_name = input(
            "Bot: Please enter the product name: "
        ).strip()

    product = get_product(product_name)

    if product:

        name, price, stock = product

        print()
        print("Bot: Product found!")
        print("Bot: Product Name:", name)
        print("Bot: Price: Rs.", price)
        print("Bot: Available Stock:", stock)

        if stock > 0:

            response = (
                f"Product found: {name}. "
                f"Price: Rs.{price}. "
                f"Available stock: {stock}."
            )

        else:

            response = f"{name} is currently out of stock."

        print("Bot:", response)

        return response

    response = "Sorry, product not found."

    print("Bot:", response)

    return response


def order_tracking(order_id=None):

    if order_id is None:

        order_id = input(
            "Bot: Please enter your Order ID: "
        ).strip()

    order_id = order_id.upper().strip()

    order = get_order(order_id)

    if order:

        customer, product, order_date, delivery_date, status = order

        print()
        print("Bot: Order found!")
        print("Bot: Customer:", customer)
        print("Bot: Product:", product)
        print("Bot: Order Date:", order_date)
        print("Bot: Expected Delivery:", delivery_date)
        print("Bot: Current Status:", status)

        return (
            f"Order found. "
            f"Customer: {customer}. "
            f"Product: {product}. "
            f"Order Date: {order_date}. "
            f"Expected Delivery: {delivery_date}. "
            f"Current Status: {status}."
        )

    response = "Sorry, Order ID not found."

    print("Bot:", response)

    return response


def delivery_information(order_id=None):

    if order_id is None:

        order_id = input(
            "Bot: Please enter your Order ID: "
        ).strip()

    order = get_order(order_id)

    if order:

        customer, product, order_date, delivery_date, status = order

        print()
        print("Bot: Delivery Information")
        print("Bot: Product:", product)
        print("Bot: Current Status:", status)
        print("Bot: Expected Delivery:", delivery_date)

        return (
            f"Product: {product}. "
            f"Current Status: {status}. "
            f"Expected Delivery: {delivery_date}."
        )

    response = "Sorry, Order ID not found."

    print("Bot:", response)

    return response


def return_product(order_id=None):

    if order_id is None:

        order_id = input(
            "Bot: Please enter your Order ID: "
        ).strip()

    order = get_order(order_id)

    if order:

        customer, product, order_date, delivery_date, status = order

        print()
        print("Bot: Order found!")
        print("Bot: Product:", product)
        print("Bot: Current Status:", status)

        if status.lower() == "delivered":

            response = (
                "This product is eligible for return. "
                "Please contact customer support to start the return."
            )

        else:

            response = (
                "This order has not been delivered yet. "
                "Return can be requested after delivery."
            )

        print("Bot:", response)

        return response

    response = "Sorry, Order ID not found."

    print("Bot:", response)

    return response


def refund_information(order_id=None):

    if order_id is None:

        order_id = input(
            "Bot: Please enter your Order ID: "
        ).strip()

    order = get_order(order_id)

    if order:

        customer, product, order_date, delivery_date, status = order

        print()
        print("Bot: Order found!")
        print("Bot: Product:", product)
        print("Bot: Current Status:", status)

        if status.lower() == "delivered":

            response = (
                "Refund request can be raised. "
                "The returned product will be verified. "
                "After verification, the refund will be processed."
            )

        else:

            response = (
                "This order has not been delivered yet. "
                "Refund cannot be requested at this stage."
            )

        print("Bot:", response)

        return response

    response = "Sorry, Order ID not found."

    print("Bot:", response)

    return response


def cancel_order(order_id=None):

    if order_id is None:

        order_id = input(
            "Bot: Please enter your Order ID: "
        ).strip()

    order = get_order(order_id)

    if order:

        customer, product, order_date, delivery_date, status = order

        print()
        print("Bot: Order found!")
        print("Bot: Product:", product)
        print("Bot: Current Status:", status)

        if status.lower() == "processing":

            response = "Your order can be cancelled."

        else:

            response = (
                "This order cannot be cancelled. "
                f"Current status: {status}."
            )

        print("Bot:", response)

        return response

    response = "Sorry, Order ID not found."

    print("Bot:", response)

    return response


def payment_support():

    print()
    print("Bot: Payment Support")
    print("Bot: 1. Check your internet connection.")
    print("Bot: 2. Check your payment details.")
    print("Bot: 3. Try the payment again.")
    print("Bot: 4. Contact customer support if needed.")

    response = (
        "Payment support provided. "
        "Please check your payment details and try again."
    )

    return response


def show_help():

    print()
    print("Bot: I can help you with:")
    print("1. Products")
    print("2. Product price")
    print("3. Product availability")
    print("4. Order tracking")
    print("5. Delivery")
    print("6. Returns")
    print("7. Refunds")
    print("8. Cancellation")
    print("9. Payment")
    print("10. Chat history")

    print()
    print("Bot: Example questions:")
    print("Bot: What is the price of Smart Watch?")
    print("Bot: Where is my order ORD1001?")
    print("Bot: When will ORD1001 arrive?")
    print("Bot: I want a refund for ORD1002")
    print("Bot: I want to return ORD1002")
    print("Bot: Cancel ORD1003")
    print("Bot: My payment failed")
    print("Bot: history")

    return "Help menu displayed."


last_order_id = None
last_product_name = None


print()
print("================================================")
print("       E-COMMERCE CUSTOMER SUPPORT CHATBOT")
print("================================================")
print()
print("Bot: Hello! 👋 Welcome to our online store.")
print("Bot: I am your AI customer support assistant.")
print("Bot: Type 'help' to see what I can do.")
print("Bot: Type 'history' to see chat history.")
print("Bot: Type 'bye' to exit.")
print()


while True:

    try:

        user = input("You: ").strip()

    except KeyboardInterrupt:

        print()
        print("Bot: Chatbot stopped.")
        break

    if not user:

        print("Bot: Please enter a message.")
        continue

    detected_order_id = extract_order_id(user)

    if detected_order_id:
        last_order_id = detected_order_id

    detected_product_name = extract_product_name(user)

    if detected_product_name:
        last_product_name = detected_product_name

    if user.lower() in ["bye", "exit", "quit"]:

        intent = "goodbye"

        response = "Thank you for contacting us. Goodbye!"

        print("Bot:", response)

        save_chat_history(
            user,
            intent,
            response
        )

        break

    intent = predict_intent(user)

    print("Detected Intent:", intent)

    if intent == "greeting":

        response = greeting()

    elif intent == "product":

        response = product_enquiry(
            last_product_name
        )

    elif intent == "order_tracking":

        response = order_tracking(
            last_order_id
        )

    elif intent == "delivery":

        response = delivery_information(
            last_order_id
        )

    elif intent == "return":

        response = return_product(
            last_order_id
        )

    elif intent == "refund":

        response = refund_information(
            last_order_id
        )

    elif intent == "cancellation":

        response = cancel_order(
            last_order_id
        )

    elif intent == "payment":

        response = payment_support()

        print("Bot:", response)

    elif intent == "help":

        response = show_help()

    elif intent == "history":

        view_chat_history()

        response = "Chat history displayed."

    elif intent == "goodbye":

        response = "Thank you for contacting us. Goodbye!"

        print("Bot:", response)

        save_chat_history(
            user,
            intent,
            response
        )

        break

    else:

        response = (
            "Sorry, I didn't understand your question. "
            "Please type 'help' to see available options."
        )

        print("Bot:", response)

    if intent != "history":

        save_chat_history(
            user,
            intent,
            response
        )