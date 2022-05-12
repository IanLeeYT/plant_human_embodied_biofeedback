import serial
import numpy as np
import time
import struct

import sounddevice as sd


class RTA_Compiler:

    def __init__(self, com_port, input_freq, blocksize, buffer_size):
        # Initialize constants
        self.constants = {
            "default_min": 5.0,
            "default_max": 45.0,
            "reg_max": 50,
            "reg_min": 30,
            "reg_map_max": 200
        }

        self.input_freq = input_freq
        self.blocksize = blocksize

        # Buffer
        self.buffer = {
            "data":  np.full(buffer_size, self.constants["default_min"]),
            "len": buffer_size,
            "i": 0,
            "mean": self.constants["default_min"],
            "prev_mean": self.constants["default_min"],
            "var": 0
        }
        # Communication port
        self.com_port = com_port
        self.baud_rate = 9600

    def bound_extremes_array(self, v):
        return max(min(v, self.constants["reg_max"]), self.constants["reg_min"])

    def normalize(self, data):
        # find range of data from inputstream
        # norm = max(min(np.linalg.norm(data) * 35, 255), 30)
        # print(f"Testing: {np.linalg.norm(data)}")
        raw_norm = np.linalg.norm(data) * 10

        self.buffer["prev_mean"] = self.buffer["mean"]

        self.buffer["mean"] = self.buffer["mean"] + raw_norm/self.buffer["len"] - \
            self.buffer["data"][self.buffer["i"]]/self.buffer["len"]

        self.buffer["var"] = ((self.buffer["len"] - 2)*self.buffer["var"] + (raw_norm -
                              self.buffer["mean"]) * (raw_norm - self. buffer["prev_mean"])) / (self.buffer["len"] - 1)

        self.buffer["data"][self.buffer["i"]] = raw_norm
        self.buffer["i"] += 1
        self.buffer["i"] %= self.buffer["len"]

        buffer_max = max(
            self.constants["default_max"], self.buffer["mean"] +
            2 * np.sqrt(self.buffer["var"]))
        buffer_min = min(
            self.constants["default_min"], max(
                0, self.buffer["mean"] - 2 * np.sqrt(self.buffer["var"])))

        # print(round(np.std(self.buffer["data"]), 3), round(
        #     np.sqrt(self.buffer["var"]), 3))

        # buffer_max = self.constants["default_max"]
        # buffer_min = self.constants["default_min"]

        coef = raw_norm / self.buffer["mean"]

        norm = int(coef * (raw_norm - buffer_min) / (buffer_max -
                                                     buffer_min) * self.constants["reg_map_max"])

        norm = self.bound_extremes_array(norm)

        print(norm, f"   {round(raw_norm, 2)}", f"   {int(buffer_max)}   ", round(np.sqrt(self.buffer["var"]), 3), int(buffer_min),  round(
            self.buffer["mean"], 2), round(coef, 2))

        return norm

    def audio_callback(self, indata, frames, time, status):
        norm = self.normalize(indata)
        # norm = self.bound_extremes_array(norm)
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
            print("quit process")
        except Exception as e:
            print(f"unexpected error: {e}")
        self.ser.write(struct.pack('>B', 1))
        self.ser.write(struct.pack('>B', 1))
        self.ser.close()

        #  normalize with sliding window, sum of window is certain value


if __name__ == "__main__":

    com_port = "/dev/cu.usbmodem141101"
    input_freq = 44100
    blocks = 10
    blocksize = input_freq // blocks
    buffer_size = blocks * 2

    test = RTA_Compiler(com_port,
                        input_freq, blocksize, buffer_size)
    test.interactive()
