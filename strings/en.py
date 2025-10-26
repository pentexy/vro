# Owner Panel Texts
OWNER_PANEL_TITLE = "🤖 <b>Owner Panel</b>"
OWNER_PANEL_BUTTONS = {
    "add_account": "➕ Add Account",
    "available_accounts": "📊 Available Accounts", 
    "solded": "💰 Solded",
    "users": "👥 Users"
}

# User Panel Texts  
USER_START_MESSAGE = """
<b>Welcome! 👋</b>

<blockquote>Get code from @yourhinata to use me</blockquote>
"""

# Add Account Flow
ADD_ACCOUNT_START = "🔐 <b>Add Account Flow</b>\n\nPlease send the phone number with country code:"
INVALID_PHONE_FORMAT = "❌ <b>Invalid phone format.</b>\n\nPlease send phone number with country code (e.g., +1234567890):"
ASK_PHONE_CODE = "📱 <b>Phone Code Sent</b>\n\nPlease enter the verification code:"
INVALID_CODE_FORMAT = "❌ <b>Invalid code format.</b>\n\nPlease enter 5-digit verification code:"
ASK_2FA = "🔒 <b>2FA Required</b>\n\nPlease enter your 2FA password:"
LOGIN_SUCCESSFUL = "✅ <b>Login Successful!</b>\n\nAccount added successfully."
ACCOUNT_CODE_GENERATED = """
✅ <b>Account Added Successfully!</b>

📝 <b>Unique Code:</b> <code>{code}</code>
🌍 <b>Country:</b> {country}
📞 <b>Phone:</b> {phone}

<blockquote>Users can use: /get {code}</blockquote>
"""

# Available Accounts
AVAILABLE_ACCOUNTS_TITLE = "📊 <b>Available Accounts</b>\n\n"
ACCOUNT_COUNTRY_STATS = "🌍 <b>{country}</b>: {count} accounts"
TOTAL_ACCOUNTS = "\n📈 <b>Total Available:</b> {total}"
AVAILABLE_BUTTONS = {
    "refresh": "🔄 Refresh",
    "back": "⬅️ Back"
}
NO_ACCOUNTS_AVAILABLE = "❌ <b>No accounts available</b>"

# Sold Accounts
SOLDED_TITLE = "💰 <b>Solded Accounts</b>\n\n"
SOLDED_TODAY_STATS = """
📊 <b>Today's Stats:</b>
• Accounts Sold: {sold_today}
• Total Profit: ${profit_today}
"""
SOLDED_ACCOUNT_ITEM = """
📱 <b>Account {index}:</b>
• Phone: {phone}
• Country: {country} 
• Price: ${price}
• Sold At: {sold_time}
"""
SOLDED_BUTTONS = {
    "set_price": "💵 Set Price",
    "seven_days": "7 Days",
    "back": "⬅️ Back"
}

# Set Price
SET_PRICE_PROMPT = "💵 <b>Set Price</b>\n\nPlease send country and price in format:\n<code>CountryCode Price</code>\n\nExample: <code>US 10.50</code>"
PRICE_SET_SUCCESS = "✅ <b>Price set successfully!</b>\n\n🌍 <b>Country:</b> {country}\n💰 <b>Price:</b> ${price}"
INVALID_PRICE_FORMAT = "❌ <b>Invalid format.</b>\n\nUse: <code>CountryCode Price</code>\nExample: <code>US 10.50</code>"

# Users Management
USERS_TITLE = "👥 <b>Users Management</b>\n\n"
USERS_STATS = """
📊 <b>Statistics:</b>
• Total Users: {total_users}
• Active Today: {active_today}
• Bought Today: {bought_today}
"""
USER_BROADCAST_PROMPT = "📢 <b>Broadcast Message</b>\n\nPlease send the message you want to broadcast:"
BROADCAST_SENT = "✅ <b>Broadcast sent successfully!</b>\n\n• Total Users: {total}\n• Successful: {success}\n• Failed: {failed}"
USER_DETAILS = """
👤 <b>User Details:</b>

🆔 <b>User ID:</b> <code>{user_id}</code>
📛 <b>Name:</b> {name}
📅 <b>Joined:</b> {join_date}
💰 <b>Total Spent:</b> ${total_spent}
📱 <b>Accounts Bought:</b> {accounts_bought}
"""

# Get Account Flow
GET_ACCOUNT_USAGE = "<b>Usage:</b> <code>/get CODE</code>"
INVALID_CODE = "❌ <b>Invalid code or account not available</b>"
ACCOUNT_DETAILS = """
📱 <b>Account Details:</b>

🌍 <b>Country:</b> {country}
📞 <b>Phone:</b> {phone}

<i>Please provide OTP when received...</i>
"""
OTP_PROMPT = "🔐 <b>OTP Required</b>\n\nPlease enter the OTP sent to the account:"
TWOFA_PROMPT = "🔒 <b>2FA Required</b>\n\nPlease enter the 2FA password:"
INVALID_OTP = "❌ <b>Invalid OTP</b>\n\nPlease try again:"
INVALID_2FA = "❌ <b>Invalid 2FA</b>\n\nPlease try again:"
TRANSACTION_COMPLETE = """
✅ <b>Transaction Complete!</b>

📱 <b>Account:</b> {phone}
💰 <b>Price:</b> ${price}
📅 <b>Time:</b> {time}

Thank you for your purchase! 🎉
"""

# Error Messages
LOGIN_ERROR = "❌ <b>Login failed:</b> {error}"
SESSION_ERROR = "❌ <b>Session error:</b> {error}"
UNAUTHORIZED_ACCESS = "❌ <b>Unauthorized Access</b>\n\nYou are not authorized to use this feature."
DATABASE_ERROR = "❌ <b>Database error occurred</b>"
UNKNOWN_ERROR = "❌ <b>An unexpected error occurred</b>"

# Button Texts
BUTTON_BACK = "⬅️ Back"
BUTTON_REFRESH = "🔄 Refresh"
BUTTON_CANCEL = "❌ Cancel"
BUTTON_CONFIRM = "✅ Confirm"
BUTTON_NEXT = "➡️ Next"
BUTTON_PREVIOUS = "⬅️ Previous"

# Status Messages
PROCESSING = "⏳ <b>Processing...</b>"
CANCELLED = "❌ <b>Cancelled</b>"
SUCCESS = "✅ <b>Success</b>"
FAILED = "❌ <b>Failed</b>"
LOADING = "🔄 <b>Loading...</b>"

# Date Formats
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"

# Country Codes (Common ones)
COUNTRY_CODES = {
    "US": "United States",
    "GB": "United Kingdom", 
    "CA": "Canada",
    "AU": "Australia",
    "DE": "Germany",
    "FR": "France",
    "IT": "Italy",
    "ES": "Spain",
    "IN": "India",
    "BR": "Brazil",
    "RU": "Russia",
    "JP": "Japan",
    "KR": "South Korea",
    "CN": "China",
    "SG": "Singapore",
    "AE": "UAE",
    "SA": "Saudi Arabia"
}
