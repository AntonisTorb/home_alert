# Home Alert
A home intruder alert system using webcams with Discord integration. It detects, records, and uploads recordings to a Discord server, while also able to accept status and configuration commands from it. 

A test script is provided in order to determine the configuration properties of your webcam(s). 

## Table of Contents
- [How to run](#how-to-run)
- [Configuration](#configuration)
- [env file](#env-file)
- [Discord bot commands](#discord-bot-commands)


## How to run

Instructions for Windows:
- Main application:
    - Make sure you have Python installed on your system.
    - Open a Terminal/Powershell/Command Line window in the directory of the `main.py` file. You can navigate to this directory by executing the command `cd 'the directory path here'`
    - Execute the command `pip install -r requirements.txt` to install all the required packages.
    - Ensure that the parameters in the `config.json` file are appropriate to your setup. Refer to [Configuration](#configuration) for more details.
    - Ensure the details required for the Discord bot are provided in the `.env` file. Refer to [env file](#env-file)
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

Bellow are the settings, default values, as well as an explanation of what each setting does:

- `"detecting": false`: Whether the Detector component(s) will start detecting for movement at the start of the application (can be updated with a Discord bot [command](#discord-bot-commands)).
- `"recording": false`: Whether the Recorder component(s) will start recording at the start of the application (can be updated with a Discord bot [command](#discord-bot-commands)). Recomended to keep `false`, unless you want the application to constantly record and upload to Discord.
- `"debug": true`: The debug mode will show additional information while the Detector is running, assisting you in choosing the best configuration options for it. If set to `true`, it will display a window with the frames detected. The `threshold value` between the current and previous frame will also be displayed in the console if any movement is detected. This value is used for determining when to trigger the alert and the threshold for it can be set with the `alert_threshold` option below.

    Finally, if the alert is triggered, it will display a window with the recorder frames.
- `"max_file_size_mb": 25`: The maximum file size in `megabytes` for each recording file. When changing this keep in mind your upload speed, as well as the relevant Discord limitation (Discord server boost status and maximum filesize for attachments).
- `"detector_frame_width": 640`: The width of the frames captured by the Detector in pixels.
- `"detector_frame_height": 480`: The height of the frames captured by the Detector in pixels.
- `"detector_frame_rate": 10`: The rate at which the Detector captures frames in frames per second.
- `"detector_threshold": 5`: Represents the sensitivity of the Detector and the values should be between `1` and `255`. The lower the value, the higher the sensitivity. You can change this depending on the distance to the main point you are detecting and the amount of movement expected compared to the total detection space.
- `"alert_threshold": 10`: Represents the minimum threshold required to recognise as sufficient movement for an alert. You can set this after using the `debug` mode and observing the threshold values in the console window by performing actions in front of the webcam.
- `"alerts_to_trigger_recording": 5: "green"`: The amount of cumulative values over the `alert_threshold` in order to trigger the alert. You can set this depending on the Detector framerate. Keep in mind that if no movement above the threshhold is detected between frames, the internal counter for this value will decrease over time.
- `"recorder_frame_width": 1280`: The width of the frames captured by the Recorder in pixels.
- `"recorder_frame_height": 720`: The height of the frames captured by the Recorder in pixels.
- `"recorder_frame_rate": 30`: The rate at which the Recorder captures frames in frames per second.

## env file


## How to use

<div align="center"><img src="images/data.jpg" alt="Something_went_wrong.jpg" style="margin: 2em 0;"></div>

## Thank you and enjoy!
