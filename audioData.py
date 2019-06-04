import pyaudio
import numpy as np
from subprocess import call,DEVNULL,getoutput
from scipy.io import wavfile
import os

class audioData:
    ##### class to store audio data and metadata; and read and write audio files using ffmpeg

    def __init__(self,source,rate):
        #### 'source' can be either a path to an audio file or a numpy array storing the audio data with shape [n_samples x channels] or [n_samples] if mono
        #### rate = integer, sampling rate in Hz

        self.rate = rate
        if isinstance(source, str) and os.path.isfile(source):
            self.read(source)
        elif isinstance(source,np.ndarray):
            self.data = source
        self.dtype = self.data.dtype
        
        shape = self.data.shape
        if len(shape) == 2:
            self.channels = shape[1]
        else:
            self.channels = 1

    def write(self,filepath,bitrate = '322k'):

        ### save the audio data stored in 'self.data' to the 'filepath' with the selected bitrate (str,322k by default) and output format (both must be ffmpeg compatible)
        auxPath = filepath.split('.')[0] + '.wav'
        wavfile.write(auxPath,self.rate,self.data)
        mp3ConvCommand = ['ffmpeg','-y','-i',auxPath,'-vn','-ac',str(self.channels),'-b:a',bitrate,filepath]
        call(mp3ConvCommand, stderr=DEVNULL, stdout=DEVNULL)
        os.remove(auxPath)

    def read(self,filepath):
        #### reads the input audio file and stores the data in 'self.data' as a numpy array  [ n x channels ]
        commandSampRate = 'ffprobe -v error -show_entries stream=sample_rate -of default=noprint_wrappers=1:nokey=1 ' + filepath
        self.rate = int(getoutput(commandSampRate))

        auxPath = filepath.split('.')[0] + '.wav'
        wavConvCommand = ['ffmpeg','-i',filepath,'-acodec','pcm_s16le','-ar',str(self.rate),auxPath]
        call(wavConvCommand, stderr=DEVNULL, stdout=DEVNULL)
        _,self.data = wavfile.read(auxPath)
        self.channels = len(self.data.shape)
        os.remove(auxPath)
    
    def toMono(self):
        if self.channels > 1:
            ##### converts the audio data to mono
            self.data = self.data.astype(float)
            self.data = np.mean(self.data,axis=1)
            self.data = self.data.astype(self.dtype)
            self.channels = 1
    
    def toStereo(self):
        ##### converts the audio data from mono to stereo
        if self.channels == 1:
            self.data = np.stack((self.data,self.data),axis=1)
            self.channels = 2



