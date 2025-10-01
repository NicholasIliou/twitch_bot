# Organic Twitch Bot

Custom non-disruptive Twitch Bot that aims to add fun / helpful features in a less robotic way.

## Features

- Periodically send random Emote
- Shadow other user's Emotes
- Use Commands without prefixes like "!"
- Authentication is not persistent so you can easily log in with an account that is not currently broadcasting or logged in
- Tally User Count (not 100% accurate)

## Setup (Local)

1. Clone the repository and enter the project directory:
   ```sh
   git clone <repo-url>
   cd <repo-name>
   ```
2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Copy [.env.example](.env.example) to `.env` and fill in your Twitch credentials:
   ```sh
   cp .env.example .env
   # or manually create .env
   ```
5. Run the bot:
   ```sh
   python main.py
   ```

## Setup (Docker)

1. Build the Docker image:
   ```sh
   docker build -t twitch-bot .
   ```
2. Run the container (make sure to provide your .env file):
   ```sh
   docker run --env-file .env twitch-bot
   ```

## Notes
- Make sure to change [.env](.env) to contain your Twitch APP_ID, APP_SECRET, TARGET_CHANNEL, etc.
- If you are unsure which Setup to use: For development, use the virtual environment. For regular use, try Docker.