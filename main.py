from telethon import TelegramClient, events
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
import asyncio
import mysql.connector
import re

# Define your credentials (API ID and Hash from my.telegram.org)
api_id = '20757150'
api_hash = '90ed6eb59d787067fbee20fe4644a3ea'
phone_number = '8801829170104'  # Your phone number in international format
bot_token = "7263697174:AAGBI-R1TzcqxZFVUkS5OaREmKSodUIFhYw"

# Admin username or chat ID to send the message
admin_username = 'QuotexPartnerBot'  # Replace with the actual username or chat ID

# Initialize the Telethon client
client = TelegramClient('bot_backend_session', api_id, api_hash)

# Dictionary to keep track of user requests
user_requests = {}

# Database connection details
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': '',  # Replace with your MySQL password
    'database': 'quotex'
}

# Function to check if a user is already verified in the database
def check_user_in_database(username):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM history WHERE trader_id = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result[0] > 0  # Returns True if the user exists, otherwise False
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

# Function to add a new user to the database
def add_user_to_database(username):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "INSERT INTO history (trader_id) VALUES (%s)"
        cursor.execute(query, (username,))
        connection.commit()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Function to send a message from the main account to the admin
async def send_message_to_admin(user_id, message):
    # Send message to the admin
    await client.send_message(admin_username, message)
    
    # Save the user_id to track the request
    user_requests[admin_username] = user_id

# Function to handle admin's reply and send it back to the user
@client.on(events.NewMessage(from_users=admin_username))
async def handle_admin_reply(event):
    # Get the admin's reply
    admin_reply = event.message.message
    print(f"Admin's reply: {admin_reply}")  # Log admin's reply for debugging

    # Retrieve the original user ID from the dictionary
    original_user_id = user_requests.get(admin_username)
    cutOut = admin_reply[:8]
    print(cutOut)

    newAdminReply = admin_reply  # Default to the original reply
    if cutOut == "Trader w":
        newAdminReply = ("আপনার আকাউন্ট টি আমাদের লিংক থেকে খোলা নেই \n"
                         "দয়া করে নিচে দেয়া লিংক থেকে আকাউন্ট খুলে, ২০ ডলার দিপোসিট করে UID দি, "
                         "তাহলে VIP গ্রুপ এর লিংক দেয়া হবে\n"
                         "https://market-qx.pro/sign-up?lid=378356")
    else:
        # Regular expression to extract the Deposits Sum line
        deposits_sum_line_pattern = r"Deposits Sum:.*"
        deposits_sum_line_match = re.search(deposits_sum_line_pattern, admin_reply)

        # Extract the line
        deposits_sum_line = deposits_sum_line_match.group(0) if deposits_sum_line_match else "Not found"

        deposit = int(deposits_sum_line[16:-3])

        if deposit >= 20:
            newAdminReply = "VIP গ্রুপ এর লিংক:\nhttps://t.me/+qdo-gcMvmhthYjQ1\nTrading Master AAR ফ্যামিলির সঙ্গে যুক্ত থাকার জন্য ধন্যবাদ🌹"

            def get_first_n_words(s, n):
                # Split the string into words
                words = s.split()

                # Get the first n words
                first_n_words = words[:n]

                # Join the first n words back into a string
                return ' '.join(first_n_words)

            result = get_first_n_words(admin_reply, n=3)

            modUserForDb = result[9:]
            add_user_to_database(modUserForDb)
        else:
            newAdminReply = "আমাদের VIP গ্রুপে ঢুকতে হলে সর্বনিম্ন আপনার ২০ ডিপোজিট করা থাকতে হবে\nদয়া করে ডিপোজিট করে আমাকে এবার UID টা পাঠান আমি VIP গ্রুপ এর লিংক দিয়ে দিচ্ছি। "
    
    if original_user_id:
        # Send the admin's reply back to the original user via bot
        await application.bot.send_message(chat_id=original_user_id, text=newAdminReply)

# Function to handle user messages for the bot
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user_id = update.message.chat_id  # Get the user's chat ID
    username = user_message.strip()

    # Check if the user is already verified in the database
    if check_user_in_database(username):
        await update.message.reply_text('আপনার এই Quotex আকাউন্ট দারা ইতিমধ্যে আমাদের VIP গ্রুপে একটি টেলেগ্রাম আকাউন্ট যুক্ত রয়েছে। ')
    else:
        # Forward the user's message (username) to the admin
        await send_message_to_admin(user_id, f"{username}")

# Command handler to send a welcome message with a persistent keyboard
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = []  # No buttons
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        '🌹 Send Your Trader ID:\n[Bangla] আপনার আইডি চেক করতে অথবা VIP ব্যাচের লিংক পেতে Quotex Trader ID দিন।\n🚫 মনে রাখবেন ট্রেডার আইডি দেওয়ার সময় কোনো লিখা এড থাকবে না।শুধুমাত্র আইডিটাই পাঠাবেন। যেমন: 4685825',
        reply_markup=reply_markup
    )

if __name__ == '__main__':
    
    # Start the Telethon client
    client.start(phone=phone_number)

    # Initialize the bot
    application = ApplicationBuilder().token(bot_token).build()

    # Register the message handler for the bot
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))

    # Run the bot and the Telethon client
    client.loop.run_until_complete(application.run_polling())
    client.run_until_disconnected()