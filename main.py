"""
main.py

Entrypoint for the Twitch bot. Loads configuration, toggles, and handlers, and starts the bot.
"""
import asyncio
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import ChatEvent
from twitchAPI.chat import Chat
from config import APP_ID, APP_SECRET, USER_SCOPE, TARGET_CHANNEL, USERNAME
from toggles import UNDEAD, GREET_CHATTER, SHADOW, REPLY_COMMAND
from handlers import on_ready, on_message, on_sub, test_command, shadow, undead, greet_chatter, on_category_change

from twitchAPI.eventsub.websocket import EventSubWebsocket


async def run():
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    chat = await Chat(twitch)
    chat.set_prefix("!")

    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)
    # chat.register_event(ChatEvent.SUB, on_sub)

    if REPLY_COMMAND:
        chat.register_command('reply', test_command)
    if GREET_CHATTER:
        chat.register_event(ChatEvent.MESSAGE, greet_chatter)
    if SHADOW:
        chat.register_event(ChatEvent.MESSAGE, shadow)

    # Dynamically fetch broadcaster ID from username
    async for user_info in twitch.get_users(logins=[USERNAME]):
        break  # Get the first result and stop
    broadcaster_id = user_info.id if user_info else None

    # Set up EventSub WebSocket for category change
    eventsub = None
    if broadcaster_id:
        eventsub = EventSubWebsocket(twitch)
        eventsub.start()  # NOT awaited

        # Subscribe to channel update (category change) events
        await eventsub.listen_channel_update(broadcaster_id, on_category_change)

    chat.start()
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("Shutting down gracefully...")
    finally:
        chat.stop()
        if eventsub is not None:
            await eventsub.stop()
        await twitch.close()
    print("Shutdown completed.")

if __name__ == "__main__":
    asyncio.run(run())