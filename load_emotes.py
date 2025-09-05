import requests
import random

class EmoteChecker:
    """
    A class to fetch and check 7TV emotes for a specific Twitch channel using the CrippledByte emotes API.

    Attributes:
        target_channel (str): The Twitch channel username to fetch emotes for.
        emote_list (list of str): A list of emote codes (names) fetched for the channel.

    Methods:
        load_emotes():
            Fetches the 7TV emotes for the target channel and populates the emote_list attribute.
            Raises an HTTPError if the request fails.

        is_valid_emote(emote_name: str) -> bool:
            Checks if a given emote name exists in the loaded emote list.
            
            Args:
                emote_name (str): The name/code of the emote to check.
            
            Returns:
                bool: True if the emote exists for the channel, False otherwise.
    """
    def __init__(self, target_channel: str):
        self.target_channel = target_channel
        self.emote_list = []
        self.load_emotes()

    def load_emotes(self):
        url = f"https://emotes.crippled.dev/v1/channel/{self.target_channel}/7tv"
        response = requests.get(url)
        response.raise_for_status()  # raise exception on bad response
        data = response.json()
        self.emote_list = [emote["code"] for emote in data]

    def is_valid_emote(self, emote_name: str) -> bool:
        return emote_name in self.emote_list
    
    def random_emote(self):
        """returns a random emote from the selected emote list"""
        return self.emote_list[random.randint(0,len(self.emote_list))]

    def __str__(self):
        return f"Emote list for channel '{channel}':, {checker.emote_list}"

if __name__ == "__main__":
    # Usage:
    channel = "xqc"
    emote = "OMEGALUL"
    checker = EmoteChecker(channel)

    print(checker)
    print(f"{emote} is available in {channel}'s 7tv emotes:", checker.is_valid_emote(emote))