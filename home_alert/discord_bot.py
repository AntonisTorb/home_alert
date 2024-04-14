import os
import logging
from pathlib import Path

import discord
from discord.ext import tasks
from dotenv import load_dotenv

class DiscordBot:

    def __init__(self, recording_dir_path: Path) -> None:
        '''DiscordBot Class that represents the Discord bot component of the application.'''

        self.recording_dir_path = recording_dir_path
        self.logger = logging.getLogger(__name__)

        self.intents = discord.Intents.default()
        self.intents.messages = True
        self.intents.message_content = True
        self.client = discord.Client(intents=self.intents)
        
        self.kill = False

        load_dotenv()
        self.token = os.getenv("TOKEN")
        


    def check_files(self) -> None:
        # Check for new recording files, send as attachment and move to 'Completed' directory.
        pass


    async def killswitch_check(self):
        if self.kill:
            await self.client.close()


    def run_bot(self) -> None:
        '''Runs the discord bot component.'''
        
        @tasks.loop(seconds=1)
        async def tasks_loop():
            self.check_files()
            await self.killswitch_check()

        @self.client.event
        async def on_connect():
            self.logger.info("Discord bot online.")

        @self.client.event
        async def on_message(message: discord.Message):

            if message.author == self.client.user:
                return
            
            print(message)
            print(message.content)
            
            if not message.content.startswith("!"):
                return
            
            if message.content == "!close":
                self.kill = True

        @self.client.event
        async def on_ready():
            await tasks_loop.start()
            
        self.client.run(self.token)
        self.logger.info("Discord bot offline.")
