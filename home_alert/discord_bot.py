import asyncio
from collections import deque
from functools import wraps
import logging
import os
from pathlib import Path

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

        self.logger: logging.Logger = logging.getLogger(__name__)
        self.kill: bool = False

        try:
            self.uploaded_rec_path: Path = recording_dir_path / "uploaded"
            self.uploaded_rec_path.mkdir(exist_ok=True)

            self.notified_alert: list[bool] = [False for _ in self.configs]

            self.intents: discord.Intents = discord.Intents.default()
            self.intents.messages = True
            self.intents.message_content = True
            self.client: discord.Client = discord.Client(intents=self.intents)
            self.ping_role: discord.Role|None = None

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


    async def get_channels(self) -> None:
        '''Asynchronous getting required channels once client is ready.'''
    
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

            
    async def clear_channel(self) -> None:
        '''Asynchronous deleting all messages in the `status-control` Discord channel.'''

        msg_counter: int = 0
        while True:
            messages: list[discord.Message] = [message async for message in self.status_control_channel.history()]
            msg_counter += len(messages)
            if messages:
                await self.status_control_channel.delete_messages(messages)
            else:
                await self.status_control_channel.send(f'{msg_counter} message(s) deleted.')
                break

    
    async def check_notification_send(self) -> None:
        '''Asynchronous checking if the alert has been activated sending Discord notification if not sent.'''

        for index, config in enumerate(self.configs):
            if config.recording:
                if self.ping_role is  None:
                    guild: discord.Guild = self.client.get_guild(self.guild_id)
                    self.ping_role = discord.utils.get(guild.roles, name="Admin")
                if not self.notified_alert[index]:
                    await self.status_control_channel.send(f'{self.ping_role.mention} Alert triggered for camera {config.cam}!')
                    self.notified_alert[index] = True


    async def check_files_upload(self) -> None:
        '''Asynchronous checking if files are available to upload, attaching them and sending message to appropriate Discord channel,
        and moving them to `uploaded` directory once finished.
        '''

        if self.recordings_queue:
            file_path: Path = self.recording_dir_path / self.recordings_queue.popleft()
            filename: str = file_path.name
            camera, timestamp = filename.split(".")[0].split("-")
            file_to_attach: discord.File = discord.File(file_path)
            await self.cam_rec_channels[int(camera)].send(content=f'<t:{timestamp}:f>' , file=file_to_attach)
            file_path.rename(self.uploaded_rec_path / filename)


    async def killswitch_check(self) -> None:
        '''Asynchronous checking whether the close command has been sent. Closes the connection if True.'''

        if self.kill:
            if self.status_control_channel is not None:
                await self.status_control_channel.send("Closing application, see you later!")
            await self.client.close()


    async def status_report(self) -> None:
        '''Sends message to the status-control channel notifying of the status of the Detector and Recorder component(s).'''

        message: str = "# Status\r"
        for config in self.configs:
            message = f'''{message}## Camera {config.cam}:\r`Detecting: {config.detecting}`\r
`Recording: {config.recording}`\r`Detector threshold: {config.detector_threshold}`\r
`Alert threshold: {config.alert_threshold}`\r'''
            
        await self.status_control_channel.send(message[:-1])


    async def start_detecting(self) -> None:
        '''Signals the Detector component(s) to start detecting. 
        Sends message to the status-control channel notifying of the above.
        '''

        for config in self.configs:
            if config.detecting:
                await self.status_control_channel.send(f'Camera {config.cam} already detecting.')
            else:
                config.detecting = True
                await self.status_control_channel.send(f'Camera {config.cam} now detecting.')


    async def stop_detecting(self) -> None:
        '''Signals the Detector component(s) to stop detecting. 
        Sends message to the status-control channel notifying of the above.
        '''

        for config in self.configs:
            if not config.detecting:
                await self.status_control_channel.send(f'Camera {config.cam} already not detecting.')
            else:
                config.detecting = False
                await self.status_control_channel.send(f'Camera {config.cam} now not detecting.')


    async def stop_recording(self) -> None:
        '''Signals the Recorder and Detector component(s) to stop recording and start detecting.
        Resets the alert notificatioin booleans to False.
        Sends message to the status-control channel notifying of the above.
        '''

        for config in self.configs:
            if config.recording:
                config.recording = False
                config.detecting = True
                await self.status_control_channel.send(f'Recording stopped for camera {config.cam}, now detecting.')
            self.notified_alert: list[bool] = [False for _ in self.configs]
 

    async def set_detector_threshold(self, message_content: str) -> None:
        '''Updates the detector threshold value for the specified camera.
        Camera and new value specified in `message_content`.
        '''

        if len((message_parts := message_content.split(" "))) != 3:
            self.status_control_channel.send("Command not recognized, type `!help` for a list of commands.")
            return
        
        cam = int(message_parts[1])
        detector_threshold = int(message_parts[2])
        
        self.configs[cam].detector_threshold = detector_threshold

        await self.status_control_channel.send(f'Detector threshold for camera {cam} set to {detector_threshold}.')


    async def set_alert_threshold(self, message_content: str) -> None:
        '''Updates the alert threshold value for the specified camera.
        Camera and new value specified in `message_content`.
        '''

        if len((message_parts := message_content.split(" "))) != 3:
            self.status_control_channel.send("Command not recognized, type `!help` for a list of commands.")
            return
        
        cam = int(message_parts[1])
        alert_threshold = int(message_parts[2])
        
        self.configs[cam].alert_threshold = alert_threshold

        await self.status_control_channel.send(f'Detector threshold for camera {cam} set to {alert_threshold}.')


    async def check_log(self, message_content: str) -> None:
        '''Sends message to the status-control channel with the last lines of the log file.
        Amount of lines is specified by the user in `message_content`.'''

        if len((message_parts := message_content.split(" "))) != 2:
            self.status_control_channel.send("Command not recognized, type `!help` for a list of commands.")
            return
        
        lines = int(message_parts[1])
        
        log_handler: logging.FileHandler = self.logger.parent.handlers[0]
        with open(log_handler.baseFilename) as f:
            log_content: list[str] = f.readlines()
            log_to_return: str = "".join(log_content[-lines:])
        await self.status_control_channel.send(f'```{log_to_return}```')


    def run_bot(self) -> None:
        '''Runs the discord bot component.'''

        def exception_handler_async(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    await func(*args, **kwargs)
                except Exception as e:
                    self.logger.exception(e)
                    if self.status_control_channel is not None:
                        message = f'Error: {type(e).__name__}, {str(e)}\rFor more information please check the log file.'
                        await self.status_control_channel.send(message)
            return wrapper
        
        @tasks.loop(seconds=1)
        @exception_handler_async
        async def tasks_loop() -> None:

            await asyncio.gather(self.check_files_upload(), self.check_notification_send(), self.killswitch_check())


        @self.client.event
        @exception_handler_async
        async def on_message(message: discord.Message) -> None:

            if message.channel != self.status_control_channel:
                return
            if message.author == self.client.user or not message.content.startswith("!"):
                return
            
            # print(message)
            # print(message.content)
            
            if message.content.lower() == "!help":
                await self.status_control_channel.send(DISCORD_HELP)
            elif message.content.lower() == "!status":
                await self.status_report()
            elif message.content.lower() == "!close":
                self.kill = True
            elif message.content.lower() == "!detect":
                await self.start_detecting()
            elif message.content.lower() == "!stopdetecting":
                await self.stop_detecting()
            elif message.content.lower() == "!stoprecording":
                await self.stop_recording()
            elif message.content.lower().startswith("!setdetectorthreshold"):
                await self.set_detector_threshold(message.content.lower())
            elif message.content.lower().startswith("!setalertthreshold"):
                await self.set_alert_threshold(message.content.lower())
            elif message.content.lower().startswith("!checklog"):
                await self.check_log(message.content.lower())
            elif message.content.lower() == "!clear":
                await self.clear_channel()
            else:
                await self.status_control_channel.send("Command not recognized, type `!help` for a list of commands.")

        @self.client.event
        @exception_handler_async
        async def on_ready() -> None:

            await self.get_channels()
            self.logger.info("Discord bot online.")
            await self.status_control_channel.send("Home alert is online! Type `!help` for a list of available commands.")
            await tasks_loop.start()

        try:
            self.client.run(self.token)
        except Exception as e:
            self.logger.exception(e)
        self.logger.info("Discord bot offline.")
