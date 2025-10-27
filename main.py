from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from database import Database
from telethon_client import telethon_manager
from strings.en import *
import asyncio
import os

app = Client("account_bot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)
db = Database()

# Store temporary data
user_sessions = {}

def is_owner(user_id):
    return user_id in [Config.OWNER_ID, Config.SECOND_OWNER_ID]

# Start command with 2x2 grid
@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    
    if is_owner(user_id):
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(OWNER_PANEL_BUTTONS["add_account"], callback_data="add_account"),
                InlineKeyboardButton(OWNER_PANEL_BUTTONS["available_accounts"], callback_data="available_accounts")
            ],
            [
                InlineKeyboardButton(OWNER_PANEL_BUTTONS["solded"], callback_data="solded"),
                InlineKeyboardButton(OWNER_PANEL_BUTTONS["users"], callback_data="users")
            ]
        ])
        await message.reply_text(OWNER_PANEL_TITLE, reply_markup=keyboard)
    else:
        await message.reply_text(USER_START_MESSAGE)

# Main menu callback
@app.on_callback_query(filters.regex("^main_menu$"))
async def main_menu_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if is_owner(user_id):
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(OWNER_PANEL_BUTTONS["add_account"], callback_data="add_account"),
                InlineKeyboardButton(OWNER_PANEL_BUTTONS["available_accounts"], callback_data="available_accounts")
            ],
            [
                InlineKeyboardButton(OWNER_PANEL_BUTTONS["solded"], callback_data="solded"),
                InlineKeyboardButton(OWNER_PANEL_BUTTONS["users"], callback_data="users")
            ]
        ])
        await callback_query.edit_message_text(OWNER_PANEL_TITLE, reply_markup=keyboard)
    else:
        await callback_query.edit_message_text(USER_START_MESSAGE)

# Add Account Flow
@app.on_callback_query(filters.regex("^add_account$"))
async def add_account_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if not is_owner(user_id):
        await callback_query.answer("Unauthorized!", show_alert=True)
        return
    
    user_sessions[user_id] = {"step": "awaiting_phone"}
    
    await callback_query.edit_message_text(
        ADD_ACCOUNT_START,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_CANCEL, callback_data="main_menu")]])
    )

# Handle phone number input
@app.on_message(filters.private & filters.text & ~filters.command(["start", "get"]))
async def handle_user_input(client, message):
    user_id = message.from_user.id
    
    if user_id in user_sessions:
        session = user_sessions[user_id]
        
        if session["step"] == "awaiting_phone":
            # Validate phone number
            phone = message.text.strip()
            if not phone.startswith('+') or len(phone) < 10:
                await message.reply_text(INVALID_PHONE_FORMAT)
                return
            
            # Send code using Telethon
            loading_msg = await message.reply_text("📱 <b>Sending verification code...</b>")
            
            result = await telethon_manager.send_code_request(phone)
            
            if not result["success"]:
                await loading_msg.delete()
                await message.reply_text(f"❌ <b>Error:</b> {result['error']}")
                return
            
            session.update({
                "phone": phone,
                "step": "awaiting_code",
                "phone_code_hash": result["phone_code_hash"],
                "client": result["client"],
                "session_name": result["session_name"]
            })
            
            await loading_msg.delete()
            await message.reply_text(
                f"✅ <b>Code sent to {phone}</b>\n\n{ASK_PHONE_CODE}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_CANCEL, callback_data="main_menu")]])
            )
            
        elif session["step"] == "awaiting_code":
            code = message.text.strip()
            
            if not code.isdigit() or len(code) != 5:
                await message.reply_text(INVALID_CODE_FORMAT)
                return
            
            loading_msg = await message.reply_text("🔐 <b>Verifying code...</b>")
            
            # Sign in with code
            result = await telethon_manager.sign_in(
                session["client"],
                session["phone"],
                code,
                session["phone_code_hash"]
            )
            
            if result["success"]:
                await loading_msg.delete()
                session["step"] = "completed"
                
                # Get account info
                account_info = await telethon_manager.get_me(session["client"])
                
                if account_info["success"]:
                    # Determine country
                    country = "OTHER"
                    if session["phone"].startswith('+1'): country = "US"
                    elif session["phone"].startswith('+44'): country = "GB"
                    elif session["phone"].startswith('+91'): country = "IN"
                    elif session["phone"].startswith('+61'): country = "AU"
                    elif session["phone"].startswith('+49'): country = "DE"
                    elif session["phone"].startswith('+33'): country = "FR"
                    
                    price = Config.PRICES.get(country, Config.PRICES["OTHER"])
                    
                    # Generate unique code
                    unique_code = db.generate_unique_code()
                    
                    # Save account to database
                    account_data = {
                        "phone": session["phone"],
                        "country": country,
                        "code": unique_code,
                        "added_by": user_id,
                        "added_at": message.date,
                        "sold": False,
                        "price": price,
                        "user_id": account_info["user_id"],
                        "first_name": account_info.get("first_name", ""),
                        "username": account_info.get("username", "")
                    }
                    
                    db.add_account(account_data)
                    
                    await message.reply_text(
                        ACCOUNT_CODE_GENERATED.format(
                            code=unique_code,
                            country=country,
                            phone=session["phone"],
                            price=price
                        ),
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])
                    )
                else:
                    await message.reply_text(f"❌ <b>Error getting account info:</b> {account_info['error']}")
                
                # Cleanup
                await telethon_manager.disconnect_client(session["client"])
                del user_sessions[user_id]
                
            else:
                await loading_msg.delete()
                if "two-steps" in result["error"].lower():
                    session["step"] = "awaiting_2fa"
                    await message.reply_text(
                        ASK_2FA,
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_CANCEL, callback_data="main_menu")]])
                    )
                else:
                    await message.reply_text(f"❌ <b>Error:</b> {result['error']}")
                    
        elif session["step"] == "awaiting_2fa":
            password = message.text.strip()
            
            loading_msg = await message.reply_text("🔒 <b>Verifying 2FA...</b>")
            
            result = await telethon_manager.sign_in_with_2fa(session["client"], password)
            
            if result["success"]:
                await loading_msg.delete()
                session["step"] = "completed"
                
                # Get account info
                account_info = await telethon_manager.get_me(session["client"])
                
                if account_info["success"]:
                    # Determine country
                    country = "OTHER"
                    if session["phone"].startswith('+1'): country = "US"
                    elif session["phone"].startswith('+44'): country = "GB"
                    elif session["phone"].startswith('+91'): country = "IN"
                    elif session["phone"].startswith('+61'): country = "AU"
                    elif session["phone"].startswith('+49'): country = "DE"
                    elif session["phone"].startswith('+33'): country = "FR"
                    
                    price = Config.PRICES.get(country, Config.PRICES["OTHER"])
                    
                    # Generate unique code
                    unique_code = db.generate_unique_code()
                    
                    # Save account to database
                    account_data = {
                        "phone": session["phone"],
                        "country": country,
                        "code": unique_code,
                        "added_by": user_id,
                        "added_at": message.date,
                        "sold": False,
                        "price": price,
                        "user_id": account_info["user_id"],
                        "first_name": account_info.get("first_name", ""),
                        "username": account_info.get("username", "")
                    }
                    
                    db.add_account(account_data)
                    
                    await message.reply_text(
                        ACCOUNT_CODE_GENERATED.format(
                            code=unique_code,
                            country=country,
                            phone=session["phone"],
                            price=price
                        ),
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])
                    )
                else:
                    await message.reply_text(f"❌ <b>Error getting account info:</b> {account_info['error']}")
                
                # Cleanup
                await telethon_manager.disconnect_client(session["client"])
                del user_sessions[user_id]
            else:
                await loading_msg.delete()
                await message.reply_text(f"❌ <b>2FA Error:</b> {result['error']}")

# Available Accounts with Refresh
@app.on_callback_query(filters.regex("^available_accounts$"))
async def available_accounts_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if not is_owner(user_id):
        await callback_query.answer("Unauthorized!", show_alert=True)
        return
    
    accounts = db.get_available_accounts()
    country_stats = db.get_accounts_by_country()
    
    if not accounts:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(BUTTON_REFRESH, callback_data="available_accounts")],
            [InlineKeyboardButton(BUTTON_BACK, callback_data="main_menu")]
        ])
        await callback_query.edit_message_text(NO_ACCOUNTS_AVAILABLE, reply_markup=keyboard)
        return
    
    text = AVAILABLE_ACCOUNTS_TITLE
    for stat in country_stats:
        country_name = COUNTRY_NAMES.get(stat["_id"], stat["_id"])
        price = Config.PRICES.get(stat["_id"], Config.PRICES["OTHER"])
        text += ACCOUNT_COUNTRY_STATS.format(
            country=country_name,
            count=stat["count"],
            price=price
        ) + "\n"
    
    text += TOTAL_ACCOUNTS.format(total=len(accounts))
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_REFRESH, callback_data="available_accounts")],
        [InlineKeyboardButton(BUTTON_BACK, callback_data="main_menu")]
    ])
    
    await callback_query.edit_message_text(text, reply_markup=keyboard)

# Sold Accounts
@app.on_callback_query(filters.regex("^solded$"))
async def solded_accounts_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if not is_owner(user_id):
        await callback_query.answer("Unauthorized!", show_alert=True)
        return
    
    today_stats = db.get_today_sales()
    
    text = SOLDED_TITLE + SOLDED_TODAY_STATS.format(
        sold_today=today_stats["total_sold"],
        profit_today=today_stats["total_profit"]
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(SOLDED_BUTTONS["set_price"], callback_data="set_price_menu")],
        [InlineKeyboardButton(SOLDED_BUTTONS["seven_days"], callback_data="seven_days")],
        [InlineKeyboardButton(BUTTON_BACK, callback_data="main_menu")]
    ])
    
    await callback_query.edit_message_text(text, reply_markup=keyboard)

# Set Price Menu
@app.on_callback_query(filters.regex("^set_price_menu$"))
async def set_price_menu_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if not is_owner(user_id):
        await callback_query.answer("Unauthorized!", show_alert=True)
        return
    
    price_list = "\n".join([f"• {COUNTRY_NAMES[country]}: ₹{price}" 
                           for country, price in Config.PRICES.items()])
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇸 US", callback_data="set_price_US"),
        InlineKeyboardButton("🇬🇧 GB", callback_data="set_price_GB")],
        [InlineKeyboardButton("🇮🇳 IN", callback_data="set_price_IN"),
        InlineKeyboardButton("🇦🇺 AU", callback_data="set_price_AU")],
        [InlineKeyboardButton("🇩🇪 DE", callback_data="set_price_DE"),
        InlineKeyboardButton("🇫🇷 FR", callback_data="set_price_FR")],
        [InlineKeyboardButton("🌍 OTHER", callback_data="set_price_OTHER")],
        [InlineKeyboardButton(BUTTON_BACK, callback_data="solded")]
    ])
    
    await callback_query.edit_message_text(
        SET_PRICE_MENU.format(price_list=price_list),
        reply_markup=keyboard
    )

# Handle individual country price setting
@app.on_callback_query(filters.regex("^set_price_"))
async def set_price_country_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if not is_owner(user_id):
        await callback_query.answer("Unauthorized!", show_alert=True)
        return
    
    country = callback_query.data.split("_")[2]
    user_sessions[user_id] = {"setting_price_for": country}
    
    country_name = COUNTRY_NAMES.get(country, country)
    current_price = Config.PRICES.get(country, Config.PRICES["OTHER"])
    
    await callback_query.edit_message_text(
        f"💵 <b>Set Price for {country_name}</b>\n\n"
        f"Current Price: ₹{current_price}\n\n"
        f"Please send the new price in INR:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_BACK, callback_data="set_price_menu")]])
    )

# Users Management
@app.on_callback_query(filters.regex("^users$"))
async def users_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if not is_owner(user_id):
        await callback_query.answer("Unauthorized!", show_alert=True)
        return
    
    stats = db.get_user_stats()
    
    text = USERS_TITLE + USERS_STATS.format(
        total_users=stats["total_users"],
        active_today=stats["active_today"],
        bought_today=stats["bought_today"]
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton(BUTTON_REFRESH, callback_data="users")],
        [InlineKeyboardButton(BUTTON_BACK, callback_data="main_menu")]
    ])
    
    await callback_query.edit_message_text(text, reply_markup=keyboard)

# Get account command for users
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
    
    price = account.get("price", Config.PRICES.get(account["country"], Config.PRICES["OTHER"]))
    
    await message.reply_text(
        ACCOUNT_DETAILS.format(
            country=account["country"],
            phone=account["phone"],
            price=price
        )
    )

if __name__ == "__main__":
    print("🤖 Bot started with real Telethon login...")
    app.run()
