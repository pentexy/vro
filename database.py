from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from database import Database
from telethon_client import telethon_manager
from strings.en import *
import asyncio
import re

app = Client("account_bot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)
db = Database()

# Store temporary data
user_sessions = {}

def is_owner(user_id):
    return user_id in [Config.OWNER_ID, Config.SECOND_OWNER_ID]

def get_country_from_phone(phone):
    if phone.startswith('+1'): return "US"
    elif phone.startswith('+44'): return "GB"
    elif phone.startswith('+91'): return "IN"
    elif phone.startswith('+61'): return "AU"
    elif phone.startswith('+49'): return "DE"
    elif phone.startswith('+33'): return "FR"
    elif phone.startswith('+7'): return "RU"
    elif phone.startswith('+86'): return "CN"
    else: return "OTHER"

# Start command with 2x2 grid
@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    
    if is_owner(user_id):
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("➕ Add Account", callback_data="add_account"),
                InlineKeyboardButton("📊 Available", callback_data="available_accounts")
            ],
            [
                InlineKeyboardButton("💰 Sold", callback_data="solded"),
                InlineKeyboardButton("👥 Users", callback_data="users")
            ]
        ])
        await message.reply_text(
            "🤖 <b>Owner Panel</b>\n\nWelcome back!",
            reply_markup=keyboard
        )
    else:
        await message.reply_text(
            "👋 <b>Welcome!</b>\n\n"
            "Get codes from @yourhinata\n"
            "Use: <code>/get CODE</code>"
        )

# Main menu callback
@app.on_callback_query(filters.regex("^main_menu$"))
async def main_menu_callback(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    if is_owner(user_id):
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("➕ Add Account", callback_data="add_account"),
                InlineKeyboardButton("📊 Available", callback_data="available_accounts")
            ],
            [
                InlineKeyboardButton("💰 Sold", callback_data="solded"),
                InlineKeyboardButton("👥 Users", callback_data="users")
            ]
        ])
        try:
            await callback_query.edit_message_text(
                "🤖 <b>Owner Panel</b>\n\nWelcome back!",
                reply_markup=keyboard
            )
        except:
            await callback_query.message.reply_text(
                "🤖 <b>Owner Panel</b>\n\nWelcome back!",
                reply_markup=keyboard
            )
    else:
        try:
            await callback_query.edit_message_text(
                "👋 <b>Welcome!</b>\n\n"
                "Get codes from @yourhinata\n"
                "Use: <code>/get CODE</code>"
            )
        except:
            await callback_query.message.reply_text(
                "👋 <b>Welcome!</b>\n\n"
                "Get codes from @yourhinata\n"
                "Use: <code>/get CODE</code>"
            )

# Add Account Flow - THIS is where OTP/2FA should happen
@app.on_callback_query(filters.regex("^add_account$"))
async def add_account_callback(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    if not is_owner(user_id):
        await callback_query.answer("❌ Unauthorized!", show_alert=True)
        return
    
    user_sessions[user_id] = {"step": "awaiting_phone"}
    
    try:
        await callback_query.edit_message_text(
            "🔐 <b>Add Account</b>\n\n"
            "Send phone number with country code:\n"
            "<code>+919876543210</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="main_menu")]])
        )
    except:
        await callback_query.message.reply_text(
            "🔐 <b>Add Account</b>\n\n"
            "Send phone number with country code:\n"
            "<code>+919876543210</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="main_menu")]])
        )

# Handle user messages - For ADDING accounts (OTP/2FA flow)
@app.on_message(filters.private & filters.text & ~filters.command(["start", "get"]))
async def handle_user_input(client, message):
    user_id = message.from_user.id
    
    # Handle account adding flow (ONLY for owners)
    if user_id in user_sessions and is_owner(user_id):
        session = user_sessions[user_id]
        
        if session["step"] == "awaiting_phone":
            phone = message.text.strip()
            if not re.match(r'^\+\d{10,15}$', phone):
                await message.reply_text("❌ Invalid phone format. Use: +919876543210")
                return
            
            # Send code using Telethon - REAL OTP sent to the account being added
            loading_msg = await message.reply_text("📱 Sending verification code to the account...")
            result = await telethon_manager.send_code_request(phone)
            
            if not result["success"]:
                await loading_msg.edit_text(f"❌ Error: {result['error']}")
                return
            
            session.update({
                "phone": phone,
                "step": "awaiting_code",
                "phone_code_hash": result["phone_code_hash"],
                "client": result["client"]
            })
            
            await loading_msg.edit_text(
                f"✅ Verification code sent to {phone}\n\n"
                "Please enter the 5-digit code received on that account:"
            )
            
        elif session["step"] == "awaiting_code":
            code = message.text.strip()
            if not code.isdigit() or len(code) != 5:
                await message.reply_text("❌ Enter 5-digit verification code")
                return
            
            loading_msg = await message.reply_text("🔐 Verifying code...")
            result = await telethon_manager.sign_in(
                session["client"],
                session["phone"],
                code,
                session["phone_code_hash"]
            )
            
            if result["success"]:
                # Get account info
                account_info = await telethon_manager.get_me(session["client"])
                if account_info["success"]:
                    country = get_country_from_phone(session["phone"])
                    price = Config.PRICES.get(country, Config.PRICES["OTHER"])
                    unique_code = db.generate_unique_code()
                    
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
                    
                    await loading_msg.edit_text(
                        f"✅ <b>Account Added Successfully!</b>\n\n"
                        f"📝 <b>Unique Code:</b> <code>{unique_code}</code>\n"
                        f"🌍 <b>Country:</b> {country}\n"
                        f"📞 <b>Phone:</b> {session['phone']}\n"
                        f"💰 <b>Price:</b> ₹{price}\n\n"
                        f"<b>Users can now use:</b> <code>/get {unique_code}</code>",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])
                    )
                else:
                    await loading_msg.edit_text(f"❌ Error getting account info: {account_info['error']}")
            else:
                if "two-steps" in result["error"].lower():
                    session["step"] = "awaiting_2fa"
                    await loading_msg.edit_text("🔒 This account has 2FA enabled. Please enter the 2FA password:")
                else:
                    await loading_msg.edit_text(f"❌ Login failed: {result['error']}")
            
            # Cleanup
            if session["step"] != "awaiting_2fa":
                await telethon_manager.disconnect_client(session["client"])
                del user_sessions[user_id]
                
        elif session["step"] == "awaiting_2fa":
            password = message.text.strip()
            loading_msg = await message.reply_text("🔒 Verifying 2FA password...")
            
            result = await telethon_manager.sign_in_with_2fa(session["client"], password)
            if result["success"]:
                account_info = await telethon_manager.get_me(session["client"])
                if account_info["success"]:
                    country = get_country_from_phone(session["phone"])
                    price = Config.PRICES.get(country, Config.PRICES["OTHER"])
                    unique_code = db.generate_unique_code()
                    
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
                    
                    await loading_msg.edit_text(
                        f"✅ <b>Account Added Successfully!</b>\n\n"
                        f"📝 <b>Unique Code:</b> <code>{unique_code}</code>\n"
                        f"🌍 <b>Country:</b> {country}\n"
                        f"📞 <b>Phone:</b> {session['phone']}\n"
                        f"💰 <b>Price:</b> ₹{price}\n\n"
                        f"<b>Users can now use:</b> <code>/get {unique_code}</code>",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])
                    )
                else:
                    await loading_msg.edit_text(f"❌ Error getting account info: {account_info['error']}")
            else:
                await loading_msg.edit_text(f"❌ 2FA verification failed: {result['error']}")
            
            await telethon_manager.disconnect_client(session["client"])
            del user_sessions[user_id]
    
    # Handle price setting
    elif user_id in user_sessions and "setting_price_for" in user_sessions[user_id]:
        country = user_sessions[user_id]["setting_price_for"]
        try:
            price = int(message.text.strip())
            if price <= 0:
                await message.reply_text("❌ Price must be positive")
                return
            
            # Update price in database
            db.set_country_price(country, price)
            
            country_name = COUNTRY_NAMES.get(country, country)
            await message.reply_text(
                f"✅ <b>Price Updated!</b>\n\n"
                f"🌍 {country_name}\n"
                f"💰 New Price: ₹{price}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="set_price_menu")]])
            )
            del user_sessions[user_id]
        except ValueError:
            await message.reply_text("❌ Enter valid number")

# Available Accounts
@app.on_callback_query(filters.regex("^available_accounts$"))
async def available_accounts_callback(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    if not is_owner(user_id):
        await callback_query.answer("❌ Unauthorized!", show_alert=True)
        return
    
    accounts = db.get_available_accounts()
    country_stats = db.get_accounts_by_country()
    
    if not accounts:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="available_accounts")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ])
        try:
            await callback_query.edit_message_text(
                "❌ No accounts available",
                reply_markup=keyboard
            )
        except:
            await callback_query.message.reply_text(
                "❌ No accounts available",
                reply_markup=keyboard
            )
        return
    
    text = "📊 <b>Available Accounts</b>\n\n"
    for stat in country_stats:
        country_name = COUNTRY_NAMES.get(stat["_id"], stat["_id"])
        price = db.get_country_price(stat["_id"]) or Config.PRICES.get(stat["_id"], Config.PRICES["OTHER"])
        text += f"📍 <b>{country_name}</b> - {stat['count']} accounts (₹{price})\n"
    
    text += f"\n📈 <b>Total:</b> {len(accounts)} accounts"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="available_accounts")],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
    ])
    
    try:
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except:
        await callback_query.message.reply_text(text, reply_markup=keyboard)

# Sold Accounts
@app.on_callback_query(filters.regex("^solded$"))
async def solded_accounts_callback(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    if not is_owner(user_id):
        await callback_query.answer("❌ Unauthorized!", show_alert=True)
        return
    
    today_stats = db.get_today_sales()
    
    text = (
        "💰 <b>Sold Accounts</b>\n\n"
        f"📅 <b>Today's Stats:</b>\n"
        f"• Accounts Sold: {today_stats['total_sold']}\n"
        f"• Total Profit: ₹{today_stats['total_profit']}\n\n"
        f"<i>More analytics coming soon...</i>"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💵 Set Prices", callback_data="set_price_menu")],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
    ])
    
    try:
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except:
        await callback_query.message.reply_text(text, reply_markup=keyboard)

# Set Price Menu
@app.on_callback_query(filters.regex("^set_price_menu$"))
async def set_price_menu_callback(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    if not is_owner(user_id):
        await callback_query.answer("❌ Unauthorized!", show_alert=True)
        return
    
    price_list = "\n".join([
        f"• {COUNTRY_NAMES[country]}: ₹{db.get_country_price(country) or Config.PRICES.get(country, Config.PRICES['OTHER'])}" 
        for country in ["US", "GB", "IN", "AU", "DE", "FR", "OTHER"]
    ])
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇸 US", callback_data="set_price_US"),
         InlineKeyboardButton("🇬🇧 GB", callback_data="set_price_GB")],
        [InlineKeyboardButton("🇮🇳 IN", callback_data="set_price_IN"),
         InlineKeyboardButton("🇦🇺 AU", callback_data="set_price_AU")],
        [InlineKeyboardButton("🇩🇪 DE", callback_data="set_price_DE"),
         InlineKeyboardButton("🇫🇷 FR", callback_data="set_price_FR")],
        [InlineKeyboardButton("🌍 OTHER", callback_data="set_price_OTHER")],
        [InlineKeyboardButton("⬅️ Back", callback_data="solded")]
    ])
    
    try:
        await callback_query.edit_message_text(
            f"💵 <b>Set Prices (INR)</b>\n\n{price_list}\n\nClick country to set price:",
            reply_markup=keyboard
        )
    except:
        await callback_query.message.reply_text(
            f"💵 <b>Set Prices (INR)</b>\n\n{price_list}\n\nClick country to set price:",
            reply_markup=keyboard
        )

# Handle price setting callbacks
@app.on_callback_query(filters.regex("^set_price_"))
async def set_price_country_callback(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    if not is_owner(user_id):
        await callback_query.answer("❌ Unauthorized!", show_alert=True)
        return
    
    country = callback_query.data.split("_")[2]
    user_sessions[user_id] = {"setting_price_for": country}
    
    country_name = COUNTRY_NAMES.get(country, country)
    current_price = db.get_country_price(country) or Config.PRICES.get(country, Config.PRICES["OTHER"])
    
    try:
        await callback_query.edit_message_text(
            f"💵 <b>Set Price for {country_name}</b>\n\n"
            f"Current Price: ₹{current_price}\n\n"
            f"Send new price (numbers only):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="set_price_menu")]])
        )
    except:
        await callback_query.message.reply_text(
            f"💵 <b>Set Price for {country_name}</b>\n\n"
            f"Current Price: ₹{current_price}\n\n"
            f"Send new price (numbers only):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="set_price_menu")]])
        )

# Users Management
@app.on_callback_query(filters.regex("^users$"))
async def users_callback(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    if not is_owner(user_id):
        await callback_query.answer("❌ Unauthorized!", show_alert=True)
        return
    
    stats = db.get_user_stats()
    
    text = (
        "👥 <b>Users Management</b>\n\n"
        f"📊 <b>Statistics:</b>\n"
        f"• Total Users: {stats['total_users']}\n"
        f"• Active Today: {stats['active_today']}\n"
        f"• Purchases Today: {stats['bought_today']}\n\n"
        f"<i>User list and broadcast features coming soon...</i>"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="users")],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
    ])
    
    try:
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except:
        await callback_query.message.reply_text(text, reply_markup=keyboard)

# Get account command - SIMPLE: just give account details and mark as sold
@app.on_message(filters.command("get"))
async def get_account(client, message):
    if len(message.command) < 2:
        await message.reply_text("❌ Usage: /get CODE")
        return
    
    code = message.command[1]
    account = db.get_account_by_code(code)
    
    if not account:
        await message.reply_text("❌ Invalid code or account not available")
        return
    
    price = account.get("price", Config.PRICES.get(account["country"], Config.PRICES["OTHER"]))
    
    # Mark account as sold immediately when someone uses /get
    db.mark_account_sold(code, message.from_user.id, price)
    
    await message.reply_text(
        f"✅ <b>Account Purchased Successfully!</b>\n\n"
        f"📱 <b>Phone:</b> {account['phone']}\n"
        f"🌍 <b>Country:</b> {account['country']}\n"
        f"💰 <b>Price:</b> ₹{price}\n\n"
        f"Thank you for your purchase! 🎉\n\n"
        f"<i>You can now login to the account using the phone number above.</i>"
    )

if __name__ == "__main__":
    print("🤖 Bot started with proper logic...")
    app.run()
