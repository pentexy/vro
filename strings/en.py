# Owner Panel Texts
OWNER_PANEL_TITLE = """
<b>🤖 Account Manager Bot</b>

<i>Welcome back, Owner!</i>
"""
OWNER_PANEL_BUTTONS = {
    "add_account": "➕ Add Account",
    "available_accounts": "📊 Available Accounts", 
    "solded": "💰 Sold Accounts",
    "users": "👥 Users"
}

# User Panel Texts  
USER_START_MESSAGE = """
<b>👋 Welcome!</b>

<blockquote>Get your unique code from @yourhinata to access accounts</blockquote>

<i>Use /get CODE to access your account</i>
"""

# Add Account Flow
ADD_ACCOUNT_START = """
<b>🔐 Add New Account</b>

Please send the phone number with country code:

<code>Example: +919876543210</code>
"""
INVALID_PHONE_FORMAT = """
<b>❌ Invalid Format</b>

Please send phone number with country code:
<code>+919876543210</code>
"""
ASK_PHONE_CODE = """
<b>📱 Verification Code</b>

Please enter the 5-digit code sent to the account:
"""
INVALID_CODE_FORMAT = """
<b>❌ Invalid Code</b>

Please enter 5-digit verification code:
"""
ASK_2FA = """
<b>🔒 Two-Factor Authentication</b>

Please enter your 2FA password:
"""
LOGIN_SUCCESSFUL = "✅ <b>Login Successful!</b>"
ACCOUNT_CODE_GENERATED = """
✅ <b>Account Added Successfully!</b>

📝 <b>Unique Code:</b> <code>{code}</code>
🌍 <b>Country:</b> {country}
📞 <b>Phone:</b> {phone}
💰 <b>Price:</b> ₹{price}

<blockquote>Users can use: /get {code}</blockquote>
"""

# Available Accounts
AVAILABLE_ACCOUNTS_TITLE = "📊 <b>Available Accounts</b>\n\n"
ACCOUNT_COUNTRY_STATS = "📍 <b>{country}</b> - {count} accounts (₹{price})"
TOTAL_ACCOUNTS = "\n📈 <b>Total Available:</b> {total} accounts"
AVAILABLE_BUTTONS = {
    "refresh": "🔄 Refresh",
    "back": "⬅️ Back"
}
NO_ACCOUNTS_AVAILABLE = "❌ <b>No accounts available</b>"

# Sold Accounts
SOLDED_TITLE = "💰 <b>Sold Accounts</b>\n\n"
SOLDED_TODAY_STATS = """
<b>📅 Today's Statistics:</b>
• Accounts Sold: <b>{sold_today}</b>
• Total Profit: <b>₹{profit_today}</b>
"""
SOLDED_ACCOUNT_ITEM = """
📱 <b>Account {index}:</b>
• Phone: {phone}
• Country: {country} 
• Price: ₹{price}
• Sold At: {sold_time}
"""
SOLDED_BUTTONS = {
    "set_price": "💵 Set Prices",
    "seven_days": "📅 7 Days Stats",
    "back": "⬅️ Back"
}

# Set Price
SET_PRICE_MENU = """
<b>💵 Set Country Prices</b>

Current Prices (INR):
{price_list}

Click on country to set price:
"""
PRICE_SET_SUCCESS = "✅ <b>Price updated!</b>\n\n🌍 <b>{country}</b>\n💰 <b>New Price:</b> ₹{price}"
INVALID_PRICE_FORMAT = "❌ <b>Invalid amount</b>\n\nPlease send only numbers:\n<code>100</code>"

# Users Management
USERS_TITLE = "👥 <b>Users Management</b>\n\n"
USERS_STATS = """
<b>📊 Statistics:</b>
• Total Users: <b>{total_users}</b>
• Active Today: <b>{active_today}</b>
• Bought Today: <b>{bought_today}</b>
"""
USER_BROADCAST_PROMPT = "📢 <b>Broadcast Message</b>\n\nPlease send the message you want to broadcast:"
BROADCAST_SENT = "✅ <b>Broadcast sent!</b>\n\n• Total Users: {total}\n• Successful: {success}\n• Failed: {failed}"

# Get Account Flow
GET_ACCOUNT_USAGE = "<b>Usage:</b> <code>/get CODE</code>"
INVALID_CODE = "❌ <b>Invalid code or account not available</b>"
ACCOUNT_DETAILS = """
<b>📱 Account Details</b>

🌍 <b>Country:</b> {country}
📞 <b>Phone:</b> {phone}
💰 <b>Price:</b> ₹{price}

<i>Please provide OTP when received...</i>
"""
OTP_PROMPT = "🔐 <b>Enter OTP</b>\n\nPlease enter the OTP sent to the account:"
TWOFA_PROMPT = "🔒 <b>Enter 2FA</b>\n\nPlease enter the 2FA password:"
INVALID_OTP = "❌ <b>Invalid OTP</b>\n\nPlease try again:"
TRANSACTION_COMPLETE = """
✅ <b>Transaction Complete!</b>

📱 <b>Account:</b> {phone}
💰 <b>Price:</b> ₹{price}
📅 <b>Time:</b> {time}

Thank you for your purchase! 🎉
"""

# Button Texts
BUTTON_BACK = "⬅️ Back"
BUTTON_REFRESH = "🔄 Refresh"
BUTTON_CANCEL = "❌ Cancel"
BUTTON_CONFIRM = "✅ Confirm"

# Country Codes
COUNTRY_NAMES = {
    "US": "United States",
    "GB": "United Kingdom", 
    "CA": "Canada",
    "AU": "Australia",
    "IN": "India",
    "DE": "Germany",
    "FR": "France",
    "OTHER": "Other Countries"
}
