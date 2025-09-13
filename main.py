
"""
main.py

Entrypoint for the Twitch bot. Loads configuration, toggles, and handlers, and starts the bot.
"""
import asyncio
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import ChatEvent
from twitchAPI.chat import Chat
from config import APP_ID, APP_SECRET, USER_SCOPE
from toggles import UNDEAD, GREET_CHATTER, SHADOW, REPLY_COMMAND
from handlers import on_ready, on_message, on_sub, test_command, shadow, undead, on_join, on_leave, greet_chatter

async def run():
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    chat = await Chat(twitch)
    chat.set_prefix("!")

    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, shadow)
    chat.register_event(ChatEvent.MESSAGE, on_message)
    chat.register_event(ChatEvent.JOINED, on_join)
    chat.register_event(ChatEvent.USER_LEFT, on_leave)
    # chat.register_event(ChatEvent.SUB, on_sub)

    if REPLY_COMMAND:
        chat.register_command('reply', test_command)
    if GREET_CHATTER:
        chat.register_event(ChatEvent.MESSAGE, greet_chatter)
    if SHADOW:
        chat.register_event(ChatEvent.MESSAGE, shadow)

    chat.start()
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        chat.stop()
        await twitch.close()

if __name__ == "__main__":
    asyncio.run(run())