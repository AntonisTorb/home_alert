from collections import deque
import logging
import os
from pathlib import Path
import asyncio

import discord
from discord.ext import tasks
from dotenv import load_dotenv

from .configuration import Config
from .utils import DISCORD_HELP

class DiscordBot:

    def __init__(self, recording_dir_path: Path, cameras: int, configs: list[Config], recordings_queue: deque[str]) -> None:
        '''DiscordBot Class that represents the Discord bot component of the application.'''

        self.recording_dir_path: Path = recording_dir_path
        self.cameras: int = cameras
        self.configs: list[Config] = configs
        self.recordings_queue: deque[str] = recordings_queue

        self.notified_alarm: list[bool] = [False for _ in self.configs]

        self.logger: logging.Logger = logging.getLogger(__name__)

        self.intents:discord.Intents = discord.Intents.default()
        self.intents.messages = True
        self.intents.message_content = True
        self.client: discord.Client = discord.Client(intents=self.intents)
        self.ping_role: discord.Role|None = None
        
        self.kill: bool = False

        try:
            load_dotenv()
            self.token: str|None = os.getenv("TOKEN")
            self.guild_id = int(os.getenv("GUILD_ID"))

            self.status_control_channel_id: int = int(os.getenv("STATUS_CONTROL_CHANNEL_ID"))
            self.status_control_channel: discord.TextChannel|None = None

            self.cam_rec_channel_ids: list[int] = [int(os.getenv(f'CAM_{cam}_REC_CHANNEL_ID')) for cam in range(self.cameras)]
            self.cam_rec_channels: list[discord.TextChannel]|None = None
        except Exception as e:
            self.logger.exception(e)
            self.kill = True


    async def check_files(self) -> None:

        for index, config in enumerate(self.configs):
            if config.recording:
                if self.ping_role is  None:
                    guild: discord.Guild = self.client.get_guild(self.guild_id)
                    self.ping_role = discord.utils.get(guild.roles, name="Admin")
                if not self.notified_alarm[index]:
                    await self.status_control_channel.send(f'{self.ping_role.mention} Alarm triggered for camera {config.cam}!')
                    self.notified_alarm[index] = True
        # Actually check for files and upload them.


    async def killswitch_check(self):

        if self.kill:
            await self.status_control_channel.send("Closing application, see you later!")
            await self.client.close()


    async def status_report(self) -> None:

        message: str = ""
        for config in self.configs:
            message = f'{message}Camera {config.cam}:\r- Detecting: {config.detecting}\r- Recording: {config.recording}\r'
        await self.status_control_channel.send(message[:-1])


    async def start_detecting(self) -> None:

        for config in self.configs:
            if config.detecting:
                await self.status_control_channel.send(f'Camera {config.cam} already detecting.')
            else:
                config.detecting = True
                await self.status_control_channel.send(f'Camera {config.cam} now detecting.')


    async def stop_recording(self) -> None:

        for config in self.configs:
            if config.recording:
                config.recording = False
                config.detecting = True
                await self.status_control_channel.send(f'Recording stopped for camera {config.cam}, now detecting.')
            self.notified_alarm: list[bool] = [False for _ in self.configs]


    def run_bot(self) -> None:
        '''Runs the discord bot component.'''
        
        @tasks.loop(seconds=1)
        async def tasks_loop():

            # await self.check_files()
            # await self.killswitch_check()
            await asyncio.gather(self.check_files(), self.killswitch_check())

        @self.client.event
        async def on_connect():

            while self.status_control_channel is None and not self.kill:
                self.status_control_channel = self.client.get_channel(self.status_control_channel_id)
                if self.status_control_channel is None:
                    print("Could not get status control channel. Retrying...")
                    self.logger.error("Could not get status control channel. Retrying...")
                await asyncio.sleep(1)

            while (self.cam_rec_channels is None or None in self.cam_rec_channels) and not self.kill:
                self.cam_rec_channels = [self.client.get_channel(channel_id) for channel_id in self.cam_rec_channel_ids]
                if self.cam_rec_channels is None or None in self.cam_rec_channels:
                    print("Could not get status camera recording channels. Retrying...")
                    self.logger.error("Could not get status camera recording channels. Retrying...")
                await asyncio.sleep(1)
            
            if self.kill:  # If the above loops hang and the application is terminated with KeyboardInterrupt from main thread.
                return
            
            self.logger.info("Status control channel and camera recording channels received.")
            self.logger.info("Discord bot online.")
            await self.status_control_channel.send("Bot Connected! Awaiting commands. Type !help if you're confused!")

        @self.client.event
        async def on_message(message: discord.Message):

            if message.channel != self.status_control_channel:
                return
            if message.author == self.client.user or not message.content.startswith("!"):
                return
            
            print(message)
            print(message.content)
            
            if message.content.lower() == "!help":
                await self.status_control_channel.send(DISCORD_HELP)
                return
            if message.content.lower() == "!status":
                await self.status_report()
                return
            if message.content.lower() == "!close":
                self.kill = True
                return
            if message.content.lower() == "!detect":
                await self.start_detecting()
                return
            if message.content.lower() == "!stoprecording":
                await self.stop_recording()
                return

        @self.client.event
        async def on_ready():

            await tasks_loop.start()
            
        self.client.run(self.token)
        self.logger.info("Discord bot offline.")
