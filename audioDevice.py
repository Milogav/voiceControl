import pyaudio
import numpy as np
from utils import printInPlace,getMaxIntensity
from audioData import audioData
from time import time

class audioDevice:

    def __init__(self,rate = 44100,channels = 2,chunkSize = 1024,fmt = pyaudio.paInt16):
        self.rate = rate
        self.channels = channels
        self.chunkSize = chunkSize
        self.fmt = fmt
        self.audio = pyaudio.PyAudio()
        self.noiseIntensityThreshold = None

    def calibrate(self):
        print('Calibrating ambient noise threshold (be silent)...')
        recording = self.recordTime(5)
        self.noiseIntensityThreshold = getMaxIntensity(recording.data)
    
    def streamToNumpy(self,audioChunks):
        recAudio = b''.join(audioChunks)
        recAudio = np.fromstring(recAudio,dtype = np.int16)
        if self.channels == 2:
            recAudio = np.stack((recAudio[::2],recAudio[1::2]),axis=1)
        return recAudio

    def recordTime(self,recTimeSeconds):

        stream = self.audio.open(format = self.fmt,
                            channels = self.channels,
                            rate = self.rate,
                            input = True,
                            frames_per_buffer = self.chunkSize)

        print('')
        recAudio = list()
        for t in range(0,int(self.rate / self.chunkSize * recTimeSeconds)):
            elapsed = t * self.chunkSize / self.rate
            remTime = recTimeSeconds - elapsed
            printInPlace('Recording (%.2f sec.) -- Remaining time: %.2f sec.' % (recTimeSeconds,remTime))
            data = stream.read(self.chunkSize)
            recAudio.append(data)

        print('\nFinished recording...')
        stream.stop_stream()
        stream.close()
        recAudio = self.streamToNumpy(recAudio)
        recording = audioData(source = recAudio,rate = self.rate)
        return recording
    
    def recordOnSound(self,f_thr = 3,silenceStopTime = 1,timeOut = np.inf):
        ###### f_thr = intensity threhold factor. Starts recording if the sound intensity is higher than f_thr * calibIntenistyThr
        ###### silenceStopTime = seconds of silence required to stop the recording after activation
        ###### timeOut = max seconds to wait for starting a recording.

        if self.noiseIntensityThreshold is None:
            self.calibrate()
        
        silenceLoopCount = 0
        maxSilentLoops = int(self.rate * silenceStopTime / self.chunkSize)

        silence = True
        stream = self.audio.open(format = self.fmt,
                            channels = self.channels,
                            rate = self.rate,
                            input = True,
                            frames_per_buffer = self.chunkSize)
        recAudio = list()
        startTime = time()
        while silence:
            data = stream.read(self.chunkSize)
            audioSample = self.streamToNumpy([data])
            maxIn = getMaxIntensity(audioSample)
            if maxIn > f_thr * self.noiseIntensityThreshold:
                print('\nSound detected. Recording...')
                silence = False
                recAudio.append(data)
            elif time() - startTime > timeOut:
                print('TIMEOUT REACHED, aborting the recording...')
                recAudio = [data]
                silenceLoopCount = np.inf #### this skips the next while loop
                break
        
        while silenceLoopCount < maxSilentLoops:
            data = stream.read(self.chunkSize)
            recAudio.append(data)
            audioSample = self.streamToNumpy([data])
            maxIn = getMaxIntensity(audioSample)
            if maxIn < f_thr * self.noiseIntensityThreshold:
                silenceLoopCount += 1
            else:
                silenceLoopCount = 0
        print('No sound detected, stopping the recording...')

        stream.stop_stream()
        stream.close()

        recAudio = self.streamToNumpy(recAudio)
        recording = audioData(source = recAudio,rate = self.rate)
        return recording       

    
    def playAudio(self,audioData):

        stream = self.audio.open(format = audioData.fmt,
                            channels = audioData.channels,
                            rate = audioData.rate,
                            output = True)

        data = audioData.data.tostring()
        stream.write(data)
        stream.stop_stream()
        stream.close()
    
    def release(self):
        self.audio.terminate()
