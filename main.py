from pyrogram import Client, filters
from config import Config
from database import Database
from handlers import start_handler, add_account_handlers, accounts_handlers, admin_handlers
from handlers.start import start_command
from handlers.add_account import (
    add_account_callback, handle_phone_number, handle_phone_code, 
    handle_2fa, cancel_add
)
from handlers.accounts import (
    available_accounts_callback, solded_accounts_callback,
    set_price_callback, handle_set_price, back_to_main
)
from handlers.admin import users_callback, broadcast_callback, handle_broadcast
from strings.en import *

app = Client("account_bot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)
db = Database()

# Start command
@app.on_message(start_handler)
async def start_wrapper(client, message):
    await start_command(client, message)

# Add account handlers
@app.on_callback_query(filters.callback_query("add_account"))
async def add_account_wrapper(client, callback_query):
    await add_account_callback(client, callback_query)

@app.on_callback_query(filters.callback_query("cancel_add"))
async def cancel_add_wrapper(client, callback_query):
    await cancel_add(client, callback_query)

@app.on_message(filters.private & filters.text)
async def handle_all_messages(client, message):
    from handlers.add_account import temp_sessions
    
    user_id = message.from_user.id
    if user_id in temp_sessions:
        step = temp_sessions[user_id]["step"]
        if step == "phone":
            await handle_phone_number(client, message)
        elif step == "code":
            await handle_phone_code(client, message)
        elif step == "2fa":
            await handle_2fa(client, message)
        return
    
    # Handle set price
    if message.reply_to_message and "Set Price" in message.reply_to_message.text:
        await handle_set_price(client, message)
    
    # Handle broadcast
    if message.reply_to_message and "Broadcast" in message.reply_to_message.text:
        await handle_broadcast(client, message)

# Accounts handlers
@app.on_callback_query(filters.callback_query("available_accounts"))
async def available_accounts_wrapper(client, callback_query):
    await available_accounts_callback(client, callback_query)

@app.on_callback_query(filters.callback_query("solded"))
async def solded_accounts_wrapper(client, callback_query):
    await solded_accounts_callback(client, callback_query)

@app.on_callback_query(filters.callback_query("set_price"))
async def set_price_wrapper(client, callback_query):
    await set_price_callback(client, callback_query)

@app.on_callback_query(filters.callback_query("back_to_main"))
async def back_to_main_wrapper(client, callback_query):
    await back_to_main(client, callback_query)

# Admin handlers
@app.on_callback_query(filters.callback_query("users"))
async def users_wrapper(client, callback_query):
    await users_callback(client, callback_query)

@app.on_callback_query(filters.callback_query("broadcast"))
async def broadcast_wrapper(client, callback_query):
    await broadcast_callback(client, callback_query)

# Get account command
@app.on_message(filters.command("get"))
async def get_account(client, message):
    if len(message.command) < 2:
        await message.reply_text(GET_ACCOUNT_USAGE)
        return
    
    code = message.command[1]
    account = db.get_account_by_code(code)
    
    if not account:
        await message.reply_text(INVALID_CODE)
        return
    
    price = db.get_country_price(account["country"])
    
    await message.reply_text(
        ACCOUNT_DETAILS.format(
            country=account["country"],
            phone=account["phone"]
        )
    )

if __name__ == "__main__":
    print("Bot started...")
    app.run()
