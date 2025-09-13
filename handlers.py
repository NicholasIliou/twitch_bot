"""
handlers.py

Contains all event and command handler functions for the bot.
Imports shared objects from config and toggles as needed.
Exports: on_ready, on_message, on_sub, test_command, shadow, undead, on_join, on_leave, greet_chatter
"""
import asyncio
import random
from twitchAPI.chat import EventData, ChatMessage, ChatSub, ChatCommand, Chat
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from twitchAPI.type import ChatEvent
from config import TARGET_CHANNEL, USERNAME, checker, attendance, current_users, SHADOW_CHANCE, DELAY_TWEAK
from toggles import UNDEAD
from authenticate import custom_authenticate

# -----------------------------------------------------------------------------------------------------
# Monkey Patch ChatMessage to include Message function
async def new_send_message(self, text: str):
    bucket = self.chat._get_message_bucket(self._parsed['command']['channel'][1:])
    await bucket.put()
    await self.chat.send_raw_irc_message(f'PRIVMSG #{self.room.name} :{text}')

from twitchAPI.chat import ChatMessage
if not hasattr(ChatMessage, 'send_message'):
    ChatMessage.send_message = new_send_message

# Monkey Patch Authentication
UserAuthenticator.authenticate = custom_authenticate
# -----------------------------------------------------------------------------------------------------

async def async_delayed_message(msg: ChatMessage, message_text: str, base_delay: float = 1.0):
    """
    Sends a reply after a delay based on message length and DELAY_TWEAK.
    DELAY_TWEAK controls both the mean and the variance.
    """
    char_count = min(len(msg.text), 4)
    tweak = max(DELAY_TWEAK, 0.0)  # Prevent negative values
    low = 1 - tweak
    high = 1 + tweak
    rnd = random.uniform(low, high)
    delay = (2 + char_count * base_delay) * rnd
    await asyncio.sleep(delay)
    await msg.send_message(message_text)

# Handler for category change via EventSub
async def on_category_change(event, chat, channel):
    # Category-specific emote messages
    CATEGORY_EMOTE_MESSAGES = {
        "Elden Ring": ["eldenTime", "EldenRingTime"],
        "Rocket League": ["RocketLeagueTime"],
        "Noita":["minaSpin", "hamis"]
        # Add more categories and emote lists as needed
    }
    # event['category_name'] or event['category_id'] depending on the event payload
    # twitchAPI eventsub websocket sends event as an object with .category_name
    new_category = getattr(event, 'category_name', None)
    if not new_category:
        return
    emotes = CATEGORY_EMOTE_MESSAGES.get(new_category)
    if emotes:
        # Only send emotes that are in your emote list
        valid_emotes = [e for e in emotes if e in checker.emote_list]
        if valid_emotes:
            message = " ".join(valid_emotes)
            await chat.send_message(channel, message)


async def on_ready(ready_event: EventData):
    print('Bot is ready for work, joining channels')
    await ready_event.chat.join_room(TARGET_CHANNEL)
    if UNDEAD:
        asyncio.create_task(undead(ready_event.chat, TARGET_CHANNEL))

async def on_message(msg: ChatMessage):
    print(f'{msg.user.name}: {msg.text}')

async def on_sub(sub: ChatSub):
    print(f'New subscription in {sub.room.name}:\n' f'  Type: {sub.sub_plan}\n' f'  Message: {sub.sub_message}')

async def test_command(cmd: ChatCommand):
    if len(cmd.parameter) == 0:
        await cmd.reply('you did not tell me what to reply with')
    else:
        await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')

async def shadow(msg: ChatMessage):
    rnd = random.random()
    if msg.user.name != USERNAME and checker.is_valid_emote(msg.text):
        if rnd < SHADOW_CHANCE:
            await async_delayed_message(msg, msg.text)
            print(f"(!) Shadowed: {msg.user.name}: {msg.text}")

async def undead(chat: Chat, channel: str):
    while True:
        print("undead function was called")
        try:
            rnd_time = random.randint(10, 30)
            await asyncio.sleep(rnd_time*60)
            await chat.send_message(channel, checker.random_emote())
        except Exception as e:
            print(f"Undead error: {e}")

async def greet_chatter(msg: ChatMessage):
    user = msg.user.name
    if msg.first:
        if 'hiFirstTimeChatter' in checker.emote_list:
            await async_delayed_message(msg, 'hiFirstTimeChatter')
        attendance.on_join(user)
    elif not attendance.is_current(user):
        attendance.on_join(user)
        greetings = [emote for emote in ['hi', 'hii'] if emote in checker.emote_list]
        if greetings:
            chosen = random.choice(greetings) + f" @{user}"
            await async_delayed_message(msg, chosen)
        else:
            await async_delayed_message(msg, 'hi')
    else:
        attendance.on_join(user)
