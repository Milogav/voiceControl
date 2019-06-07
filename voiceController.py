from pyaudio import paInt16
from audioDevice import audioDevice
import json
from subprocess import Popen
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import re 
import os
import numpy as np
import pandas as pd
from pynput import keyboard

commandMode = True
shiftStrokes = 0
def on_press(key):

    global shiftStrokes
    global commandMode
    if key == keyboard.Key.shift:
        shiftStrokes += 1
    else:
        shiftStrokes = 0
    
    if shiftStrokes == 3:
        commandMode = not(commandMode)
        if commandMode:
            print('Switched to command mode\n')
        else:
            print('Switched to writing mode\n')
        shiftStrokes = 0

class voiceController(audioDevice):

    def __init__(self,commandTablePath,language = 'es-ES'):
        ##### commandsJsonFile = string specifying the path to the json file defining the available commands
        ##### language = string specifying the language in a format accepted by the google speech recognition API

        audioDevice.__init__(self,rate = 44100,channels = 1,fmt = paInt16)
        self.calibrate()
        self.commandTable = pd.read_csv(commandTablePath,index_col=0)
        self.language = language
    
    def start(self):
        listener = keyboard.Listener(on_press=on_press)
        listener.start() ###### start keyboard listener in a separate thread
        ####### Switch between 'command' and' writing' modes by pressing the shift key 3 consecutive times
        keyboardController = keyboard.Controller() ####### object to control the keyboard, used in 'writing' mode
        while True:
            recording = self.recordOnSound()
            speech = self.speechToText(recording).lower().strip()
            if commandMode == True:
                words = speech.split(' ')
                order = words[0]
                if len(words) > 1:
                    args = ' '.join(words[1::])
                else:
                    args = '#empty#'

                try:
                    cmd = self.commandTable.loc[args,order]
                    p = Popen(cmd,shell = True)    
                except KeyError:
                    print('Command error: "%s" command not available' % speech)
                    continue
                except Exception as e:
                    print(e)

            else:
                if not(speech == '*error*'):
                    keyboardController.type(speech + ' ')
    
    def speechToText(self,audio):
        ##### audio = audioData instance, audio data array must be of type np.int16 and mono channel
       
        flacPath = 'tmpAudioSample.flac'
        
        audio.write(flacPath)
        with open(flacPath,'rb') as f:
            flacBytes = f.read()
        
        os.remove(flacPath)
        
        ############################################    CODE LINES FROM: https://github.com/Uberi/speech_recognition/blob/master/speech_recognition/__init__.py
        
        key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"   ###### google speech recognition API key
        url = "http://www.google.com/speech-api/v2/recognize?{}".format(urlencode({
            "client": "chromium",
            "lang": self.language,
            "key": key,
            "pFilter": 0
        }))
        request = Request(url, data=flacBytes, headers={"Content-Type": 'audio/x-flac; rate=%d' % audio.rate})
    
        try:
            response = urlopen(request, timeout=5)
        except HTTPError:
            print('Recognition request failed!!!')
        except URLError:
            print('Recognition connection failed!!!')
        response_text = response.read().decode("utf-8")

        ########################################################################################################################

        ##### parse response text
        speech = ''
        results = re.findall('transcript":"(.*)","',response_text)
        confidences = re.findall('confidence":(.*)}',response_text)

        if not results:
            speech = '*error*'
        elif confidences is None or len(results) < 2:
            speech = results[0]
        else:
            confidences = [float(x) for x in confidences]
            bestIdx = np.argmax(confidences)
            speech = results[bestIdx]

        return speech
