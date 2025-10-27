from pymongo import MongoClient
from config import Config
import random
import string
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DATABASE_NAME]
        self.accounts = self.db.accounts
        self.users = self.db.users
        self.sales = self.db.sales
        self.prices = self.db.prices
        print("✅ Database connected successfully")

    def generate_unique_code(self):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            if not self.accounts.find_one({"code": code}):
                return code

    def add_account(self, account_data):
        return self.accounts.insert_one(account_data)

    def get_available_accounts(self):
        return list(self.accounts.find({"sold": False}))

    def get_account_by_code(self, code):
        return self.accounts.find_one({"code": code, "sold": False})

    def get_accounts_by_country(self):
        pipeline = [
            {"$match": {"sold": False}},
            {"$group": {"_id": "$country", "count": {"$sum": 1}}}
        ]
        return list(self.accounts.aggregate(pipeline))

    def mark_account_sold(self, code, buyer_id, price):
        account = self.accounts.find_one({"code": code})
        if account:
            sale_data = {
                "account_id": account["_id"],
                "buyer_id": buyer_id,
                "price": price,
                "sold_at": datetime.now(),
                "country": account["country"]
            }
            self.sales.insert_one(sale_data)
            return self.accounts.update_one(
                {"code": code}, 
                {"$set": {"sold": True, "sold_to": buyer_id, "sold_at": datetime.now()}}
            )
        return None

    def get_today_sales(self):
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        pipeline = [
            {"$match": {"sold_at": {"$gte": today}}},
            {"$group": {
                "_id": None,
                "total_sold": {"$sum": 1},
                "total_profit": {"$sum": "$price"}
            }}
        ]
        result = list(self.sales.aggregate(pipeline))
        return result[0] if result else {"total_sold": 0, "total_profit": 0}

    def add_user(self, user_data):
        return self.users.update_one(
            {"user_id": user_data["user_id"]},
            {"$set": user_data},
            upsert=True
        )

    def get_all_users(self):
        return list(self.users.find())

    def get_user_stats(self):
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        total_users = self.users.count_documents({})
        active_today = self.sales.count_documents({"sold_at": {"$gte": today}})
        return {
            "total_users": total_users,
            "active_today": active_today,
            "bought_today": active_today
        }

    def set_country_price(self, country, price):
        return self.prices.update_one(
            {"country": country},
            {"$set": {"price": price}},
            upsert=True
        )

    def get_country_price(self, country):
        price_data = self.prices.find_one({"country": country})
        return price_data["price"] if price_data else None
