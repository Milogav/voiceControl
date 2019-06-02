import pyaudio
import wave
import numpy as np
from subprocess import call,DEVNULL,getoutput
from scipy.io import wavfile
import os

def printInPlace(text):
    print('\r'+text+'\t'*5,end='',sep = '')

class audioData:
    def __init__(self,from_dataArray = None, from_filepath = None,channels = 2,rate = 44100,fmt = pyaudio.paInt16):
        self.rate = rate
        self.channels = channels
        self.fmt = fmt
        self.data = from_dataArray
        if from_filepath is not None and os.path.isfile(from_filepath):
            self.read(from_filepath)
    
    def save(self,filepath,bitrate = '322k'):
        auxPath = filepath.split('.')[0] + '.wav'
        wavfile.write(auxPath,self.rate,self.data)
        mp3ConvCommand = ['ffmpeg','-y','-i',auxPath,'-vn','-ar',str(self.rate),'-ac',str(self.channels),'-b:a',bitrate,filepath]
        call(mp3ConvCommand, stderr=DEVNULL, stdout=DEVNULL)
        os.remove(auxPath)

    def read(self,filepath):
        commandSampRate = 'ffprobe -v error -show_entries stream=sample_rate -of default=noprint_wrappers=1:nokey=1 ' + filepath
        self.rate = int(getoutput(commandSampRate))

        auxPath = filepath.split('.')[0] + '.wav'
        wavConvCommand = ['ffmpeg','-i',filepath,'-acodec','pcm_s16le','-ar',str(self.rate),auxPath]
        call(wavConvCommand, stderr=DEVNULL, stdout=DEVNULL)
        _,self.data = wavfile.read(auxPath)
        self.channels = len(self.data.shape)
        os.remove(auxPath)


class audioDevice:

    def __init__(self,rate = 44100,channels = 2,chunkSize = 1024,fmt = pyaudio.paInt16):
        self.rate = rate
        self.channels = channels
        self.chunkSize = chunkSize
        self.fmt = fmt
        self.audio = pyaudio.PyAudio()
        self.noiseIntensityThreshold = self.calibrate()
    
    def getMaxIntensity(self,audio):
        return np.max(np.abs(audio.data))
    
    def calibrate(self):
        print('Calibrating ambient noise threshold (be silent)...')
        recording = self.recordTime(5)
        return self.getMaxIntensity(recording)
    
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

        print('\n\nRecording (%.2f sec.) ...' % recTimeSeconds)
        recAudio = list()
        for t in range(0,int(self.rate / self.chunkSize * recTimeSeconds)):
            elapsed = t * self.chunkSize / self.rate
            remTime = recTimeSeconds - elapsed
            printInPlace('    Remaining time: %.2f sec.' %remTime)
            data = stream.read(self.chunkSize)
            recAudio.append(data)

        print('\nFinished recording...')
        stream.stop_stream()
        stream.close()
        recAudio = self.streamToNumpy(recAudio)
        recording = audioData(from_dataArray = recAudio,channels =  self.channels,rate = self.rate,fmt = self.fmt)
        return recording
    
    def recordOnSound(self,f_thr = 1.25,silenceStopTime = 1):
        silence = True
        stream = self.audio.open(format = self.fmt,
                            channels = self.channels,
                            rate = self.rate,
                            input = True,
                            frames_per_buffer = self.chunkSize)
        recAudio = list()

        while silence:
            data = stream.read(self.chunkSize)
            audioSample = self.streamToNumpy([data])
            maxIn = self.getMaxIntensity(audioSample)
            if maxIn > f_thr * self.noiseIntensityThreshold:
                print('\nSound detected. Recording...')
                silence = False
                recAudio.append(data)
        
        silenceLoopCount = 0
        maxSilentLoops = int(self.rate * silenceStopTime / self.chunkSize)
        while silenceLoopCount < maxSilentLoops:
            data = stream.read(self.chunkSize)
            recAudio.append(data)
            audioSample = self.streamToNumpy([data])
            maxIn = self.getMaxIntensity(audioSample)
            if maxIn < f_thr * self.noiseIntensityThreshold:
                silenceLoopCount += 1
            else:
                silenceLoopCount = 0
        print('No sound detected, stop recording...')

        recAudio = self.streamToNumpy(recAudio)
        recording = audioData(from_dataArray = recAudio,channels =  self.channels,rate = self.rate,fmt = self.fmt)
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

    



AD = audioDevice()

recording = AD.recordOnSound()

# recording = AD.recordTime(recTimeSeconds = 60)
# recording.save('/home/miguel/audio.mp3')

# recLoad = audioData(from_filepath='/home/miguel/audio.mp3')

AD.playAudio(recording)
# waveFile = wave.open('file.mp3', 'wb')
# waveFile.setnchannels(AR.channels)
# waveFile.setsampwidth(AR.audio.get_sample_size(AR.fmt))
# waveFile.setframerate(AR.rate)
# waveFile.writeframes(recAudio)
# waveFile.close()
