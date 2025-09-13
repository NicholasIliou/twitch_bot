"""
toggles.py

Defines feature toggles for the bot. Uses env_true helper for robust, case-insensitive, per-feature toggles.
Exports: UNDEAD, GREET_CHATTER, SHADOW, REPLY_COMMAND
"""
import os

def env_true(var, default):
    return str(os.getenv(var, default)).lower() == 'true'

UNDEAD = env_true('UNDEAD', 'false')
GREET_CHATTER = env_true('GREET_CHATTER', 'true')
SHADOW = env_true('SHADOW', 'true')
REPLY_COMMAND = env_true('REPLY_COMMAND', 'false')
