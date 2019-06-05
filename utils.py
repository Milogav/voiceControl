from subprocess import call,DEVNULL,getoutput
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import re 
import numpy as np
from scipy.io import wavfile
import os
from copy import deepcopy

def printInPlace(text):
    print('\r'+text+'\t'*5,end='',sep = '')

def toText(audio,language = 'es-ES'):
        ##### audio = audioData instance, audio data array must be of type np.int16
        ##### language = string specifying the language in a format accepted by the google speech recognition API
        
        flacPath = 'audioSample.flac'
        sample = deepcopy(audio)
        
        sample.toMono()
        sample.write(flacPath)
        with open(flacPath,'rb') as f:
            flacBytes = f.read()
        
        ############# CODE LINES FROM: https://github.com/Uberi/speech_recognition/blob/master/speech_recognition/__init__.py
        key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"   ###### google speech recognition API key
        url = "http://www.google.com/speech-api/v2/recognize?{}".format(urlencode({
            "client": "chromium",
            "lang": language,
            "key": key,
            "pFilter": 0
        }))
        request = Request(url, data=flacBytes, headers={"Content-Type": 'audio/x-flac; rate=%d' % audio.rate})
    
        os.remove(flacPath)

        try:
            response = urlopen(request, timeout=5)
        except HTTPError as e:
            print('Recognition request failed!!!')
        except URLError as e:
            print('Recognition connection failed!!!')
        response_text = response.read().decode("utf-8")

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

