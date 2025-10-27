from telethon import TelegramClient
from telethon.sessions import StringSession
from config import Config
import asyncio
import os

class TelethonManager:
    def __init__(self):
        self.sessions_dir = "sessions"
        os.makedirs(self.sessions_dir, exist_ok=True)
    
    async def create_client(self, session_name):
        session_path = os.path.join(self.sessions_dir, f"{session_name}.session")
        client = TelegramClient(
            session_path,
            Config.API_ID,
            Config.API_HASH
        )
        return client
    
    async def send_code_request(self, phone_number):
        """Send code to phone number"""
        try:
            session_name = f"temp_{phone_number}"
            client = await self.create_client(session_name)
            
            await client.connect()
            result = await client.send_code_request(phone_number)
            
            return {
                "success": True,
                "phone_code_hash": result.phone_code_hash,
                "client": client,
                "session_name": session_name
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def sign_in(self, client, phone_number, phone_code, phone_code_hash):
        """Sign in with code"""
        try:
            await client.sign_in(
                phone_number,
                phone_code,
                phone_code_hash=phone_code_hash
            )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def sign_in_with_2fa(self, client, password):
        """Sign in with 2FA"""
        try:
            await client.sign_in(password=password)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_me(self, client):
        """Get account info"""
        try:
            me = await client.get_me()
            return {
                "success": True,
                "user_id": me.id,
                "first_name": me.first_name,
                "username": me.username,
                "phone": me.phone
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def disconnect_client(self, client):
        """Disconnect client"""
        try:
            await client.disconnect()
        except:
            pass

telethon_manager = TelethonManager()
