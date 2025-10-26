from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import Database
from strings.en import *
import re

db = Database()

# Store temporary session data
temp_sessions = {}

async def add_account_callback(client, callback_query):
    user_id = callback_query.from_user.id
    temp_sessions[user_id] = {"step": "phone"}
    
    await callback_query.edit_message_text(
        ADD_ACCOUNT_START,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_CANCEL, callback_data="cancel_add")]])
    )

async def handle_phone_number(client, message):
    user_id = message.from_user.id
    if user_id not in temp_sessions or temp_sessions[user_id]["step"] != "phone":
        return
    
    phone = message.text.strip()
    if not re.match(r'^\+\d{10,15}$', phone):
        await message.reply_text(INVALID_PHONE_FORMAT)
        return
    
    # Extract country code (simple implementation)
    country_code = phone[1:3]  # First 2 digits after +
    country = "Unknown"
    
    temp_sessions[user_id].update({
        "phone": phone,
        "country": country_code,
        "step": "code"
    })
    
    await message.reply_text(ASK_PHONE_CODE)

async def handle_phone_code(client, message):
    user_id = message.from_user.id
    if user_id not in temp_sessions or temp_sessions[user_id]["step"] != "code":
        return
    
    code = message.text.strip()
    if not re.match(r'^\d{5}$', code):
        await message.reply_text(INVALID_CODE_FORMAT)
        return
    
    temp_sessions[user_id]["step"] = "2fa"
    temp_sessions[user_id]["phone_code"] = code
    
    await message.reply_text(ASK_2FA)

async def handle_2fa(client, message):
    user_id = message.from_user.id
    if user_id not in temp_sessions or temp_sessions[user_id]["step"] != "2fa":
        return
    
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

async def cancel_add(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id in temp_sessions:
        del temp_sessions[user_id]
    
    await callback_query.edit_message_text(CANCELLED)

# Register handlers
add_account_handlers = [
    filters.callback_query("add_account"),
    filters.callback_query("cancel_add"),
    filters.private & filters.text
]
