# Home Alert
A home intruder alert system using webcams with Discord integration. It detects, records, and uploads recordings to a specified channel in a Discord server, notifying the Admin of the server if the alert has been triggered.

The application has 3 main components:
- The Detector, that captures frames from the webcam(s), comparing them to the previous frame in order to determine if there was sufficient difference between them, activating the alert.
- The Recorder, that captures frames from the webcam(s) and creates timestamped video files if the alert has been triggered by the Detector. The video files have file names with the following format: `camera id-timestamp.mp4`.
- The Discord bot, that provides status updates and notifications, uploads any available recordings and provides configuration options in the form of bot commands.

A test script is also provided in order to determine the configuration properties of your webcam(s).

Please check out the following if you want to learn more about the application and it's configuration options.

## Table of Contents
- [How to run](#how-to-run)
- [Configuration](#configuration)
- [.env file](#env-file)
- [Discord bot commands](#discord-bot-commands)


## How to run

### Instructions for Windows:
- Main application:
    - Make sure you have Python installed on your system.
    - Open a Terminal/Powershell/Command Line window in the directory of the `main.py` file. You can navigate to this directory by executing the command `cd 'the directory path here'`
    - Execute the command `pip install -r requirements.txt` to install all the required packages.
    - Ensure that the parameters in the `config.json` file are appropriate to your setup. Refer to [Configuration](#configuration) for more details.
    - Ensure the details required for the Discord bot are provided in a `.env` file in the same directory as the `main.py` file. Refer to [env file](#env-file) for more details.
    - Execute the command `python main.py -c cameras` replacing `cameras` with the amount of webcams used to start the app. Alternatively, follow the next 2 steps:
        - Open the `main.py` file and in the `main` function specify the amount of webcams in the `cameras` variable.
        - Execute the command `python main.py` to start the app.

- Camera test script:
    - Ensure all requirements are installed as instructed above.
    - Open a Terminal/Powershell/Command Line window in the directory of the `camera_test/test.py` file is located as instructed above.
    - Open the `test.py` file in a file editor or IDE of your choice and modify the following fields to your preferences:
        - `min_framerate`: The minimum framerate to check.
        - `max_framerate`: The maximum framerate to check.
        - `step`: The step at which the framerates will be tested between minimum and maximum.
        - `sizes`: The frame sizes in pixels (`width`, `height`).
    - Execute the command `python test.py` to execute the test script. The results will be printed on the console, as well as in a `log` file with the following filename format: `camera_id-timestamp.log`

## Configuration

You can find several settings in the `config.json` file. The file structure is the following: A dictionary that has the `camera id` as the `key` and the actual `configuration settings` dictionary as `value`. The `camera id` is just a value starting from 0 and ascending depending on the amount of webcams you have connected.

Bellow are the settings, default values, as well as an explanation of what each setting represents:

- `"detecting": false`: Whether the Detector component(s) will start detecting for movement at the start of the application (can be updated with a Discord bot [command](#discord-bot-commands)).
- `"recording": false`: Whether the Recorder component(s) will start recording at the start of the application (can be updated with a Discord bot [command](#discord-bot-commands)). Recommended to keep `false`, unless you want the application to constantly record and upload to Discord.
- `"debug": true`: The debug mode will show additional information while the Detector is running, assisting you in choosing the best configuration options for it. If set to `true`, it will display a window with the frames detected. The `threshold value` between the current and previous frame will also be displayed in the console if any movement is detected. This value is used for determining when to trigger the alert and the threshold for it can be set with the `alert_threshold` option below.

    Finally, if the alert is triggered, it will display a window with the recorder frames.
- `"max_file_size_mb": 25`: The maximum file size in `megabytes` for each recording file. When changing this keep in mind your upload speed, as well as the relevant Discord limitation (Discord server boost status and maximum file size for attachments).
- `"detector_frame_width": 640`: The width of the frames captured by the Detector in pixels.
- `"detector_frame_height": 480`: The height of the frames captured by the Detector in pixels.
- `"detector_frame_rate": 10`: The rate at which the Detector captures frames in frames per second.
- `"detector_threshold": 5`: Represents the scaling of the difference between frames captured by the detector. The values should be between `1` and `255`, and any difference higher than the provided amount wil be scaled to 255. You can change this depending on the distance to the main point you are detecting and the amount of movement expected compared to the total detection space.
- `"alert_threshold": 10`: Represents the sensitivity of the detector, and it is the minimum mean threshold required to recognize as sufficient movement for an alert. The lower the value the higher the sensitivity. You can set this after using the `debug` mode and observing the threshold values in the console window by performing actions in front of the webcam.
- `"alerts_to_trigger_recording": 5: "green"`: The amount of cumulative values over the `alert_threshold` in order to trigger the alert. You can set this depending on the Detector framerate. Keep in mind that if no movement above the threshhold is detected between frames, the internal counter for this value will decrease over time.
- `"recorder_frame_width": 1280`: The width of the frames captured by the Recorder in pixels.
- `"recorder_frame_height": 720`: The height of the frames captured by the Recorder in pixels.
- `"recorder_frame_rate": 30`: The rate at which the Recorder captures frames in frames per second.

If the `config.json` file is missing or is corrupted, a new one will be created with default values (check `home_alert/configuration.py` file) for just one camera.

## .env file

The `.env` file is required for the Discord bot, as it contains the discord token and the Discord server(Guild) and channel IDs. It should look like the following:

    # .env
    TOKEN=`your token here`
    GUILD_ID='server ID'
    STATUS_CONTROL_CHANNEL_ID=`status-control channel ID`
    CAM_0_REC_CHANNEL_ID='camera recording channel ID'

If you have multiple webcams, you will have to add the other channels on another line as: 

`CAM_i_REC_CHANNEL_ID='camera recording channel ID'`

where `i` is the webcam index.

In order to get a token you will have to visit the [Discord developer portal](https://discord.com/developers/applications) and create an application. The bot should have the following permissions: `Read Messages/View Channels`, `Send Messages`, `Manage Messages`, `Attach Files` and `Read Message History`. It also needs to have the `Message Content Intent` enabled.

As for the server and channel IDs, you can get them from the Discord URL after you visit the [Discord Web Client](https://discord.com/app). Once you have the relevant channel selected, the URL should have the following format:

`https://discord.com/channels/server ID/channel ID`

## Discord bot commands

At any point when the application is running, you can use the `!help` command in the `status-control` channel to get a list of all the available commands. Here are all of them:

- `!status`: Returns the status of each Detector and Recorder component.
- `!close`: Close application.
- `!detect`: Start detecting with all cameras.
- `!stopdetecting`: Stop detecting with all cameras.
- `!stoprecording`: Stop recording and start detecting with all cameras.
- `!checklog lines`: Replace `lines` with the amount of lines you need from the end of the `log file`.
- `!clear`: Deletes all messages in the `status-control` Discord channel.


## Thank you and enjoy!