import telegram.ext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import re
import string
import random
from pymongo import MongoClient
import requests

# MongoDB connection URI
uri = "mongodb+srv://aaroha:aaroha@cluster0.a9wygc9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri)
db = client['TeleUsers']
collection = db['TeleAuth']

# Function to generate random end for long url
def end_gen(length):
    letters = string.ascii_lowercase+string.digits+string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

# User authentication functions
def is_auth(uname):
    query = {"_id": uname}
    result = collection.find_one(query)
    return result

def login(uname, api_key):
    if is_auth(uname) is None:
        document = {'_id': uname, 'api_key': api_key}
        collection.insert_one(document)
        return True
    else:
        return False
    
def logout(uname):
    query = {'_id': uname}
    result = collection.find_one(query)
    if result is not None:
        collection.delete_one(query)
        return True
    else:
        return False

# Link generator function
def link_gen(uname, long_link):
    auth_info = is_auth(uname)
    if auth_info is not None:
        api_key = auth_info.get('api_key')
        url = f"https://ez4short.xyz/api?api={api_key}&url={long_link}&format=text"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
        }
        try:
            response = requests.get(url, headers=headers)
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Request failed: {e}"
    else:
        return "You haven't logged in yet. Please login first."

# Telegram bot handlers
def start(update, context):
    keyboard = [
                [InlineKeyboardButton("Sign Up", url="https://ez4short.xyz/auth/signup")],
            ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_reply_text = '''😋This bot will help you to Short Links from your EZ4short.xyz Account.

If you don't have an active EZ4short.xyz Account then Please register your account here EZ4short.xyz/auth/signup
 
2️⃣How to Short Links? 
👉 After Logging in , Send any link which you want to Short. 
👉 You will get your Shortned Link immediately.

3️⃣How to Short Bulk links at a time? 
👉Send All the links which you want to short in below format 👇
https://youtube.co
https://google.com
https://EZ4short.xyz
👉 Boom 💥 ! You will get all link shorten.

⚡️Still Have Doubts?
⚡️Want to Report Any Bug?
😌Send Here @EZ4short_support'''
    update.message.reply_text(message_reply_text, reply_markup=reply_markup)

def api_Login(update, context):
    user_rsp = update.message.text.split(" ")
    user = update.message.from_user
    username = user.username
    if len(user_rsp) == 1:
        update.message.reply_text("Please send login api in format of /login 12590xxxxxxxx")
    elif len(user_rsp) == 2:
        ser_rsp = login(username, user_rsp[1])
        if ser_rsp:
            update.message.reply_text(f"Welcome {username}, Now You Can Short Your Links")
        else:
            update.message.reply_text("You are already logged in.")
    else:
        update.message.reply_text("Please send api in format /login 12590xxxxxxxx")

def help(update, context):
    keyboard = [
                [InlineKeyboardButton("Get Help", url="https://EZ4short.xyz/member/forms/support")],
            ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_reply_text = 'Click on button to get help'
    update.message.reply_text(message_reply_text, reply_markup=reply_markup)

def feature(update, context):
    update.message.reply_text("""💠 Features Of EZ4short.xyz bot 💠

❤️ It's AN AI Based User Friendly Bot ❤️

➡️ Use Can Short Bulk Links Into Your EZ4short.xyz Account With This Bot""")

def handle_message(update, context):
    message = update.message
    r_message = message.text
    user = update.message.from_user
    username = user.username
    if message.photo:
        photo_file_id = message.photo[-1].file_id
        caption = message.caption
        links = re.findall(r'(https?://\S+)', caption)
        filtered_list = [link for link in links if "t.me" not in link]
        short_link = []
        L = 0
        for link in filtered_list:
            short_link.append(link_gen(username, link))
            caption = caption.replace(link, f"{short_link[L]}")
            L += 1
        context.bot.send_photo(chat_id=message.chat_id, photo=photo_file_id, caption=caption)
    elif message.text:
        if "https://" in message.text or "http" in message.text:
            caption = message.text
            links = re.findall(r'(https?://\S+)', caption)
            filtered_list = [link for link in links if "t.me" not in link]
            short_link = []
            L = 0
            for link in filtered_list:
                short_link.append(link_gen(username, link))
                caption = caption.replace(link, f"{short_link[L]} ")
                L += 1
            update.message.reply_text(caption)
        else:
            update.message.reply_text("Please Send me any link or Forward Whole Post")
    else:
        update.message.reply_text("Please Send me any link or Forward Whole Post")

def get_api(update, context):
    keyboard = [
                [InlineKeyboardButton("Get Token", url="EZ4short.xyz/member/tools/api")],
            ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_reply_text = """• First Visit EZ4short.xyz/member/tools/api
• Copy the API TOKEN and come back to Bot.
• Input  /token and Paste The token Copied from EZ4short.xyz/member/tools/api
• Now bot will successfully connected to your  EZ4short.xyz account."""
    update.message.reply_text(message_reply_text, reply_markup=reply_markup)

def api_Logout(update, context):
    user = update.message.from_user
    username = user.username
    resp = logout(username)
    if resp:
        update.message.reply_text("You are Logged Out Successfully")
    else:
        update.message.reply_text("You Haven't Login Yet Please Login First")

def main():
    # Set up the bot and its message handler
    bot_token = "7233518881:AAHQ_NVCds2bH21deSIJPQRnGFQT7CGlHqg"
    bot = telegram.Bot(bot_token)
    updater = telegram.ext.Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Add handlers for commands and messages
    dispatcher.add_handler(telegram.ext.CommandHandler('start', start))
    dispatcher.add_handler(telegram.ext.CommandHandler('help', help))
    dispatcher.add_handler(telegram.ext.CommandHandler('login', api_Login))
    dispatcher.add_handler(telegram.ext.CommandHandler('get_api', get_api))
    dispatcher.add_handler(telegram.ext.CommandHandler('logout', api_Logout))
    dispatcher.add_handler(telegram.ext.CommandHandler('features', feature))
    dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.all, handle_message))

    # Start polling for messages
    updater.start_polling()

    # Keep the bot running until Ctrl-C is pressed
    updater.idle()

if __name__ == "__main__":
    main()
