from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
import os
from dotenv import load_dotenv
load_dotenv()
import asyncio
from load_emotes import EmoteChecker
import random
from authenticate import custom_authenticate


APP_ID = os.getenv('APP_ID') # APP_ID should be stored as string
APP_SECRET = os.getenv('APP_SECRET')
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL')
USERNAME = os.getenv('USERNAME')
checker = EmoteChecker(TARGET_CHANNEL)

# Monkey Patch ChatMessage to include Message function
async def new_send_message(self, text: str):
    """Send a normal message to the chat room"""
    bucket = self.chat._get_message_bucket(self._parsed['command']['channel'][1:])
    await bucket.put()
    await self.chat.send_raw_irc_message(f'PRIVMSG #{self.room.name} :{text}')

if not hasattr(ChatMessage, 'send_message'):
    ChatMessage.send_message = new_send_message

# Monkey patch the `authenticate` method
UserAuthenticator.authenticate = custom_authenticate

# this will be called when the event READY is triggered, which will be on bot start
async def on_ready(ready_event: EventData):
    print('Bot is ready for work, joining channels')
    # join our target channel, if you want to join multiple, either call join for each individually
    # or even better pass a list of channels as the argument
    await ready_event.chat.join_room(TARGET_CHANNEL)
    # you can do other bot initialization things in here


# this will be called whenever a message in a channel was send by either the bot OR another user
async def on_message(msg: ChatMessage):
    print(f'{msg.user.name}: {msg.text}')


# this will be called whenever someone subscribes to a channel
async def on_sub(sub: ChatSub):
    print(f'New subscription in {sub.room.name}:\\n'
          f'  Type: {sub.sub_plan}\\n'
          f'  Message: {sub.sub_message}')


# this will be called whenever the !reply command is issued
async def test_command(cmd: ChatCommand):
    if len(cmd.parameter) == 0:
        await cmd.reply('you did not tell me what to reply with')
    else:
        await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')

async def shadow(msg: ChatMessage):
    rnd = random.random()
    if msg.user.name != USERNAME and checker.is_valid_emote(msg.text):
        if rnd < (0.45):
            await asyncio.sleep(3*rnd)
            #await msg.reply(f"{msg.text}")
            await msg.send_message(msg.text)
            print(f"(!) Shadowed: {msg.user.name}: {msg.text}")

# this is where we set up the bot
async def run():
    # set up twitch api instance and add user authentication with some scopes
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    # create chat instance
    chat = await Chat(twitch)

    chat.set_prefix("!")

    # register the handlers for the events you want
    chat.register_event(ChatEvent.MESSAGE, shadow)
    # listen to when the bot is done starting up and ready to join channels
    chat.register_event(ChatEvent.READY, on_ready)
    # listen to chat messages
    chat.register_event(ChatEvent.MESSAGE, on_message)
    # listen to channel subscriptions
    # chat.register_event(ChatEvent.SUB, on_sub)
    # there are more events, you can view them all in this documentation: https://pytwitchapi.dev/en/stable/modules/twitchAPI.twitch.html

    # you can directly register commands and their handlers, this will register the !reply command
    chat.register_command('reply', test_command)


    # we are done with our setup, lets start this bot up!
    chat.start()

    # lets run till we press enter in the console
    try:
        input('press ENTER to stop\\n')
    finally:
        # now we can close the chat bot and the twitch api client
        chat.stop()
        await twitch.close()


# lets run our setup
asyncio.run(run())