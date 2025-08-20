import webbrowser
import subprocess
import sys
from typing import Optional

###

import json
import os.path
from pathlib import PurePath

import aiohttp

#from .twitch import Twitch
#from .helper import build_url, build_scope, get_uuid, TWITCH_AUTH_BASE_URL, fields_to_enum
#from .type import AuthScope, InvalidRefreshTokenException, UnauthorizedException, TwitchAPIException
import webbrowser
#from aiohttp import web
import asyncio
#from threading import Thread
#from concurrent.futures import CancelledError
#from logging import getLogger, Logger
from typing import List, Union, Optional, Callable, Awaitable, Tuple

###

import urllib.parse
from enum import Enum


def build_url(url: str, params: dict, remove_none: bool = False, split_lists: bool = False, enum_value: bool = True) -> str:
    """Build a valid url string

    :param url: base URL
    :param params: dictionary of URL parameter
    :param remove_none: if set all params that have a None value get removed |default| :code:`False`
    :param split_lists: if set all params that are a list will be split over multiple url parameter with the same name |default| :code:`False`
    :param enum_value: if true, automatically get value string from Enum values |default| :code:`True`
    :return: URL
    """

    def get_val(val):
        if not enum_value:
            return str(val)
        if isinstance(val, Enum):
            return str(val.value)
        return str(val)

    def add_param(res, k, v):
        if len(res) > 0:
            res += "&"
        res += str(k)
        if v is not None:
            res += "=" + urllib.parse.quote(get_val(v))
        return res

    result = ""
    for key, value in params.items():
        if value is None and remove_none:
            continue
        if split_lists and isinstance(value, list):
            for va in value:
                result = add_param(result, key, va)
        else:
            result = add_param(result, key, value)
    return url + (("?" + result) if len(result) > 0 else "")

def open_browser_in_incognito(auth_url: str, browser_name: Optional[str] = None):
    if browser_name is None:
        browser_name = "chrome"  # Default to chrome if no browser specified.
    
    try:
        if browser_name.lower() == "chrome":
            subprocess.run(["C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", "--incognito", auth_url], check=True)
        elif browser_name.lower() == "firefox":
            subprocess.run(["firefox", "-private", auth_url], check=True)
        else:
            webbrowser.open(auth_url)
    except FileNotFoundError:
        print(f"Error: {browser_name} is not installed or not found in PATH.")
    except Exception as e:
        print(f"An error occurred while opening the browser: {str(e)}")


async def custom_authenticate(self,
                       callback_func: Optional[Callable[[str, str], None]] = None,
                       user_token: Optional[str] = None,
                       browser_name: Optional[str] = None,
                       browser_new: int = 2,
                       use_browser: bool = True,
                       auth_url_callback: Optional[Callable[[str], Awaitable[None]]] = None):
    """Start the user authentication flow, with support for incognito mode."""
    self._callback_func = callback_func
    self._can_close = False
    self._user_token = None
    self._is_closed = False

    if user_token is None:
        self._start()
        # wait for the server to start up
        while not self._server_running:
            await asyncio.sleep(0.01)
        if use_browser:
            # open in browser, using our custom function to support incognito mode
            open_browser_in_incognito(self._build_auth_url(), browser_name)
        else:
            if auth_url_callback is not None:
                await auth_url_callback(self._build_auth_url())
            else:
                self.logger.info(f"To authenticate open: {self._build_auth_url()}")
        while self._user_token is None:
            await asyncio.sleep(0.01)
    else:
        self._user_token = user_token
        self._is_closed = True

    param = {
        'client_id': self._client_id,
        'client_secret': self._twitch.app_secret,
        'code': self._user_token,
        'grant_type': 'authorization_code',
        'redirect_uri': self.url
    }
    url = build_url(self.auth_base_url + 'token', param)
    async with aiohttp.ClientSession(timeout=self._twitch.session_timeout) as session:
        async with session.post(url) as response:
            data: dict = await response.json()
    if callback_func is None:
        self.stop()
        while not self._is_closed:
            await asyncio.sleep(0.1)
        #if data.get('access_token') is None:
        #    raise TwitchAPIException(f'Authentication failed:\n{str(data)}')
        return data['access_token'], data['refresh_token']
    elif user_token is not None and self._callback_func is not None:
        self._callback_func(data['access_token'], data['refresh_token'])
