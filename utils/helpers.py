import phonenumbers
from datetime import datetime

def extract_country_code(phone_number):
    try:
        parsed = phonenumbers.parse(phone_number, None)
        return phonenumbers.region_code_for_number(parsed)
    except:
        return "Unknown"

def format_datetime(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_price(price):
    return f"${price:.2f}"

def is_owner(user_id, config):
    return user_id in [config.OWNER_ID, config.SECOND_OWNER_ID]
