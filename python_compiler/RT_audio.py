import serial
import numpy as np
import time
import struct
import re

from sklearn.utils import indexable
import sounddevice as sd


class RT_audio:

    def __init__(self, dtime, transfer_rate, com_port, input_freq, blocksize, buffer_size=20):
        # Initialize parameters
        self.transfer_rate = transfer_rate
        self.dtime = dtime
        self.input_freq = input_freq
        self.blocksize = blocksize
        self.buffer = {
            "data":  np.zeros(buffer_size),
            "len": buffer_size,
            "i": 0,
            "mean": 0
        }
        # communication port
        self.com_port = com_port
        self.baud_rate = 9600

    def normalize(self, data):
        norm = max(min(np.linalg.norm(data) * 35, 255), 30)
        return norm

    def audio_callback(self, indata, frames, time, status):
        norm = self.normalize(indata)
        self.buffer["mean"] = self.buffer["mean"] + norm/self.buffer["len"] - \
            self.buffer["data"][self.buffer["i"]]/self.buffer["len"]
        self.buffer["data"][self.buffer["i"]] = norm
        self.buffer["i"] += 1
        self.buffer["i"] %= self.buffer["len"]
        print(int(norm))
        self.ser.write(struct.pack('>B', int(norm)))

    def interactive(self):
        """
    Interactive user session

    when input non-negative integer, the pressure regulator will run constant digital value
    when input non-negative integer followed by "t" (stands for test), the pressure regulator will run self.test[i]
    when input is "end" or "quit", return
    """
        self.ser = serial.Serial(self.com_port, self.baud_rate)
        time.sleep(2)  # wait for serial connection
        duration = 60
        try:
            while True:
                stream = sd.InputStream(samplerate=self.input_freq,
                                        blocksize=self.blocksize, callback=self.audio_callback)
                with stream:
                    sd.sleep(duration * 1000)
        except KeyboardInterrupt:
            self.ser.write(struct.pack('>B', 1))
            self.ser.write(struct.pack('>B', 1))
            self.ser.close()
            print("Quitting")


        #  normalize with sliding window, sum of window is certain value
if __name__ == "__main__":

    com_port = "/dev/cu.usbmodem141201"
    transfer_rate = 1
    dtime = 0.1
    input_freq = 44100
    blocksize = input_freq // 18

    test = RT_audio(dtime, transfer_rate, com_port, input_freq, blocksize)
    test.interactive()
