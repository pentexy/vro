from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from strings.en import *

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

# Export the filter
start_handler = filters.command("start")
