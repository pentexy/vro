from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from database import Database
from strings.en import *

app = Client("account_bot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)
db = Database()

# Store temporary session data
temp_sessions = {}

# Start command
@app.on_message(filters.command("start"))
async def start_command(client, message):
    if message.from_user.id in [Config.OWNER_ID, Config.SECOND_OWNER_ID]:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(OWNER_PANEL_BUTTONS["add_account"], callback_data="add_account")],
            [InlineKeyboardButton(OWNER_PANEL_BUTTONS["available_accounts"], callback_data="available_accounts")],
            [InlineKeyboardButton(OWNER_PANEL_BUTTONS["solded"], callback_data="solded")],
            [InlineKeyboardButton(OWNER_PANEL_BUTTONS["users"], callback_data="users")]
        ])
        await message.reply_text(OWNER_PANEL_TITLE, reply_markup=keyboard)
    else:
        await message.reply_text(USER_START_MESSAGE)

# Add Account Flow
@app.on_callback_query(filters.regex("^add_account$"))
async def add_account_callback(client, callback_query):
    user_id = callback_query.from_user.id
    temp_sessions[user_id] = {"step": "phone"}
    
    await callback_query.edit_message_text(
        ADD_ACCOUNT_START,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_CANCEL, callback_data="cancel_add")]])
    )

@app.on_callback_query(filters.regex("^cancel_add$"))
async def cancel_add(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id in temp_sessions:
        del temp_sessions[user_id]
    
    await callback_query.edit_message_text(CANCELLED)

# Handle phone number input
@app.on_message(filters.private & filters.text)
async def handle_all_messages(client, message):
    user_id = message.from_user.id
    
    # Check if user is in add account flow
    if user_id in temp_sessions:
        step = temp_sessions[user_id]["step"]
        
        if step == "phone":
            await handle_phone_number(client, message)
        elif step == "code":
            await handle_phone_code(client, message)
        elif step == "2fa":
            await handle_2fa(client, message)
        return
    
    # Handle set price if replying to set price message
    if message.reply_to_message and "Set Price" in message.reply_to_message.text:
        await handle_set_price(client, message)
    
    # Handle broadcast if replying to broadcast message
    if message.reply_to_message and "Broadcast" in message.reply_to_message.text:
        await handle_broadcast(client, message)

async def handle_phone_number(client, message):
    import re
    user_id = message.from_user.id
    
    phone = message.text.strip()
    if not re.match(r'^\+\d{10,15}$', phone):
        await message.reply_text(INVALID_PHONE_FORMAT)
        return
    
    # Extract country code
    country_code = phone[1:3]
    
    temp_sessions[user_id].update({
        "phone": phone,
        "country": country_code,
        "step": "code"
    })
    
    await message.reply_text(ASK_PHONE_CODE)

async def handle_phone_code(client, message):
    import re
    user_id = message.from_user.id
    
    code = message.text.strip()
    if not re.match(r'^\d{5}$', code):
        await message.reply_text(INVALID_CODE_FORMAT)
        return
    
    temp_sessions[user_id]["step"] = "2fa"
    temp_sessions[user_id]["phone_code"] = code
    
    await message.reply_text(ASK_2FA)

async def handle_2fa(client, message):
    user_id = message.from_user.id
    
    twofa = message.text.strip()
    
    # Generate unique code
    unique_code = db.generate_unique_code()
    
    # Save account to database
    account_data = {
        "phone": temp_sessions[user_id]["phone"],
        "country": temp_sessions[user_id]["country"],
        "code": unique_code,
        "added_by": user_id,
        "added_at": message.date,
        "sold": False,
        "price": db.get_country_price(temp_sessions[user_id]["country"])
    }
    
    db.add_account(account_data)
    
    # Clear temporary session
    del temp_sessions[user_id]
    
    await message.reply_text(
        ACCOUNT_CODE_GENERATED.format(
            code=unique_code,
            country=account_data["country"],
            phone=account_data["phone"]
        )
    )

# Available Accounts
@app.on_callback_query(filters.regex("^available_accounts$"))
async def available_accounts_callback(client, callback_query):
    accounts = db.get_available_accounts()
    country_stats = db.get_accounts_by_country()
    
    if not accounts:
        await callback_query.edit_message_text(NO_ACCOUNTS_AVAILABLE)
        return
    
    text = AVAILABLE_ACCOUNTS_TITLE
    for stat in country_stats:
        text += ACCOUNT_COUNTRY_STATS.format(
            country=stat["_id"], 
            count=stat["count"]
        ) + "\n"
    
    text += TOTAL_ACCOUNTS.format(total=len(accounts))
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_REFRESH, callback_data="available_accounts")],
        [InlineKeyboardButton(BUTTON_BACK, callback_data="back_to_main")]
    ])
    
    await callback_query.edit_message_text(text, reply_markup=keyboard)

# Solded Accounts
@app.on_callback_query(filters.regex("^solded$"))
async def solded_accounts_callback(client, callback_query):
    today_stats = db.get_today_sales()
    
    text = SOLDED_TITLE + SOLDED_TODAY_STATS.format(
        sold_today=today_stats["total_sold"],
        profit_today=today_stats["total_profit"]
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(SOLDED_BUTTONS["set_price"], callback_data="set_price")],
        [InlineKeyboardButton(SOLDED_BUTTONS["seven_days"], callback_data="seven_days")],
        [InlineKeyboardButton(BUTTON_BACK, callback_data="back_to_main")]
    ])
    
    await callback_query.edit_message_text(text, reply_markup=keyboard)

# Set Price
@app.on_callback_query(filters.regex("^set_price$"))
async def set_price_callback(client, callback_query):
    await callback_query.edit_message_text(
        SET_PRICE_PROMPT,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_BACK, callback_data="solded")]])
    )

async def handle_set_price(client, message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply_text(INVALID_PRICE_FORMAT)
            return
        
        country = parts[0].upper()
        price = float(parts[1])
        
        db.set_country_price(country, price)
        
        await message.reply_text(
            PRICE_SET_SUCCESS.format(country=country, price=price),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_BACK, callback_data="solded")]])
        )
    except ValueError:
        await message.reply_text(INVALID_PRICE_FORMAT)

# Users Management
@app.on_callback_query(filters.regex("^users$"))
async def users_callback(client, callback_query):
    stats = db.get_user_stats()
    users = db.get_all_users()
    
    text = USERS_TITLE + USERS_STATS.format(
        total_users=stats["total_users"],
        active_today=stats["active_today"],
        bought_today=stats["bought_today"]
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton(BUTTON_REFRESH, callback_data="users")],
        [InlineKeyboardButton(BUTTON_BACK, callback_data="back_to_main")]
    ])
    
    await callback_query.edit_message_text(text, reply_markup=keyboard)

# Broadcast
@app.on_callback_query(filters.regex("^broadcast$"))
async def broadcast_callback(client, callback_query):
    await callback_query.edit_message_text(
        USER_BROADCAST_PROMPT,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_CANCEL, callback_data="users")]])
    )

async def handle_broadcast(client, message):
    users = db.get_all_users()
    success = 0
    failed = 0
    
    for user in users:
        try:
            await client.send_message(user["user_id"], message.text)
            success += 1
        except:
            failed += 1
    
    await message.reply_text(
        BROADCAST_SENT.format(total=len(users), success=success, failed=failed),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_BACK, callback_data="users")]])
    )

# Back to main
@app.on_callback_query(filters.regex("^back_to_main$"))
async def back_to_main(client, callback_query):
    await start_command(client, callback_query.message)

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
