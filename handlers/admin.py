from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import Database
from strings.en import *

db = Database()

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

admin_handlers = [
    filters.callback_query("users"),
    filters.callback_query("broadcast"),
    filters.private & filters.text
]
