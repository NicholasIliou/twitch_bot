"""
config.py

Handles environment variable loading, dotenv, and setup for shared objects.
Exports: APP_ID, APP_SECRET, USER_SCOPE, TARGET_CHANNEL, USERNAME, checker, attendance, current_users
"""
import os
from dotenv import load_dotenv
from load_emotes import EmoteChecker
from attendance import Attendance
from twitchAPI.type import AuthScope

load_dotenv()

APP_ID = os.getenv('APP_ID')
APP_SECRET = os.getenv('APP_SECRET')
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL')
USERNAME = os.getenv('USERNAME')
checker = EmoteChecker(TARGET_CHANNEL)
current_users = set()

attendance = Attendance()

# Shadow chance (float between 0 and 1)
def get_shadow_chance():
	try:
		return float(os.getenv('SHADOW_CHANCE', '0.45'))
	except ValueError:
		return 0.45

SHADOW_CHANCE = get_shadow_chance()
