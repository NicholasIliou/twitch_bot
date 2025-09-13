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
from config import TARGET_CHANNEL, USERNAME, checker, attendance, current_users, SHADOW_CHANCE
from toggles import UNDEAD
from authenticate import custom_authenticate

# Monkey Patch ChatMessage to include Message function
async def new_send_message(self, text: str):
    bucket = self.chat._get_message_bucket(self._parsed['command']['channel'][1:])
    await bucket.put()
    await self.chat.send_raw_irc_message(f'PRIVMSG #{self.room.name} :{text}')

from twitchAPI.chat import ChatMessage
if not hasattr(ChatMessage, 'send_message'):
    ChatMessage.send_message = new_send_message

UserAuthenticator.authenticate = custom_authenticate

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
            await asyncio.sleep(10*rnd)
            await msg.send_message(msg.text)
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

async def on_join(event: EventData):
    user = getattr(event, "user", None)
    if user:
        current_users.add(user.name)
    print(f'+1 ({len(current_users)} users)')

async def on_leave(event: EventData):
    user = getattr(event, "user", None)
    if user and user.name in current_users:
        current_users.remove(user.name)
    print(f'-1 ({len(current_users)} users)')

async def greet_chatter(msg: ChatMessage):
    user = msg.user.name
    if msg.first:
        if 'hiFirstTimeChatter' in checker.emote_list:
            rnd = random.random()
            await asyncio.sleep(10 * rnd)
            await msg.reply('hiFirstTimeChatter')
        attendance.on_join(user)
    elif not attendance.is_current(user):
        attendance.on_join(user)
        greetings = [emote for emote in ['hi', 'hii'] if emote in checker.emote_list]
        if greetings:
            chosen = random.choice(greetings)
            await msg.reply(chosen)
        else:
            await msg.reply('hi')
    else:
        attendance.on_join(user)
