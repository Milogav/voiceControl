# VoiceControl
Python library to give voice commands to the computer.

## Description and usage
The program is started by running the 'run.py' script in the terminal. E.g. python3 ~/voiceControl/run.py

In the **first 5 seconds** after launching, a simple **calibration** is done to account for the ambient sound intensity, so the user must **be silent** during this step.

The program works by recording audio from the microphone and sending it as a flac file to the google speech recognition API. It then catches the text resulting from the speech recognition. The code for making the requests to the API and catching the result where taken from: https://github.com/Uberi/speech_recognition

The program starts recording audio if the sound intensity surpasses the intensity threshold estimated during the calibration step by a certain margin. The recording stops if the received audio stream has not surpassed this margin for 1 second.

The program has **two operation modes**:

1. **Command mode**: this mode allows to give voice commands to the computer. The available commands are defined in the command table file (csv). In this mode, the recognition result is used to launch the specified commands.
2. **Writing mode**: this mode allows for automatically typing the speech. The speech will be typed in the input field selected by the mouse at that moment.

To **switch** between **modes**, press the **shift key 2 times** consecutively.

To **disable/enable** the application, press the **alt key 2 times** consecutively.

## Adding new commands
New commands and arguments can be added by including more entries in the commands_{lang_code}.table file.
This file contains a table in csv format in which the first row defines the available orders and the first column defines the arguments for the orders.

When speaking a request to the computer, the first word will correspond to the order and the remaing words will correspond to the order's arguments. For example: if one says: "open google chrome", the order would be 'open' and the argument would be 'google chrome'. The program then looks for the entry located at the table(row = 'google chrome',column = 'open') and executes the defined command action at that entry.

To add a new order without entries, add the command action in the corresponding column of the row '#empty#'

## Dependencies:
- pyaudio (for sound recording)
- scipy (for writing wav audio files)
- pandas (handles the command table)
- pynput (for keyboard monitoring and automatic typing)
- numpy
- ffmpeg (for audio conversion)
- google speech recognition web API

Tested over python 3.6 and Ubuntu 18.04

## TODO: 
	- Create a GUI
	- Add more orders and arguments
	- Make 'close' orders to act only on the previously 'open' subprocesses (now using killall command, which causes ALL previouly launched processes sharing the name to be killed too)
	- Add command table files for other languages (currently only spanish)
