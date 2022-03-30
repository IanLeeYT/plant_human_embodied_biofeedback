import numpy as np
import audio_interpreter
import matplotlib.pyplot as plt
import time
import struct
from pygame import mixer
import serial
import os
import sys
import sounddevice as sd


def plot_general(y, x=[], sampling_freq=1, title="Plot"):
    """
general format for plotting frequency based data.
"""
    if not isinstance(y, (np.ndarray, list)):
        print("fail to generate plot")
        return
    _, axis = plt.subplots(1, 1)
    axis.set_title(title)
    if len(x) == 0:
        len_y = len(y)
        x = np.linspace(0, len_y / sampling_freq, len_y)
    axis.plot(x, y)
    axis.set_xlabel("Time (s)")
    plt.show()
    plt.close()


class Compiler:

    def __init__(self, dtime, transfer_rate, com_port, freq):

        self.audio_catalog = dict()
        self.transfer_rate = transfer_rate
        self.dtime = dtime
        self.freq = freq
        self.pmx = 70
        self.baseline = 40
        self.local_peaks = 60
        self.pmin = 0
        # communication port
        self.com_port = com_port
        self.baud_rate = 9600
        # sd.default.samplerate = fs
        # data, fs = sf.read(filename, dtype='float32')
        # sd.play(data, fs)
        # self.raw_data = None
        mixer.init()  # initialize pygame.mixer for audio

    # discriminative main function
    def regval_interactive(self):
        """
    opens a user session where user can input the path to an audio file for pneumatic actuation or input end/quit to end session.

    breaks down audio file in time blocks of [dt] seconds and contruct the breathing function
    based on the localized maximums. 

    establishes a connection with an Arduino system via [port]

    rate of communication is [transfer_rate] Hz

    reg_val response values:
      min - max

    precondition: [transfer_rate] >= [dt]
    """
        # change directory to where the script exists
        os.chdir(os.path.abspath(os.curdir))
        cont = True
        while cont:
            try:
                user = input("Please enter the path to audio file: ").strip()
                if user == "end" or user == "quit":
                    print("Thank You")
                    cont = False
                else:
                    file_name = audio_interpreter.audio_path_breakdown(user)[0]
                    if file_name not in self.audio_catalog:
                        print("...Loading...\n")
                        arr = audio_interpreter.audio_to_array(user, self.freq)
                        max_arr = self.max_array(arr)
                        reg_arr = self.reg_calibrate_array(max_arr)
                        reg_arr = self.bound_outliers(reg_arr)
                        norm_reg_arr = self.normalizexy_array(reg_arr)
                        norm_reg_arr = self.bound_extremes_array(norm_reg_arr)
                        norm_reg_arr = self.dynamic_amplification(norm_reg_arr)
                        plot_general(norm_reg_arr)
                        self.audio_catalog[file_name] = self.int_array(
                            norm_reg_arr)
                        print("cached")
                    else:
                        print("retrieve from cach\n")
                    self.set_sound("audio/" + user)
                    self.send_serial(file_name)
                    print("Finished")
            except Exception as err:
                print(f"Invalid.: {err}\nTry again\n")

    def firefly():
        pass

    def max_array(self, arr):
        """
    return an array where elements are the maximum of data in 
    [arr] consecutive local buckets of time intervals [dt] seconds 
    """
        freq_dt = int(self.freq * self.dtime)
        max_arr = np.zeros(len(arr) // freq_dt)
        for i in range(len(arr) // freq_dt):
            max_arr[i] = np.max(np.abs(arr[i * freq_dt:(i + 1) * freq_dt]))
        return max_arr[1:]  # compensate for regulator time delay

    def reg_calibrate_array(self, arr):
        """
    adjust length of [arr] via averaging buckets of elements. Grouping size is [transfer_rate]/[dt]

    Precondition: [transfer_rate] >= [dt]
    """
        grouping = int(self.transfer_rate / self.dtime)
        reg_arr = np.nanmean(
            np.pad(arr.astype(float),
                   (0, (grouping - arr.size % grouping) % grouping),
                   constant_values=np.NaN).reshape(-1, grouping),
            axis=1)
        return reg_arr

    def bound_outliers(self, arr, n_sd=2.5):
        """
    remove elements in [arr] that are [n_sd] standard deviations away
    """
        mean = np.mean(arr)
        std = np.std(arr)
        max_arr = mean + n_sd * std
        min_arr = mean - n_sd * std
        return np.clip(arr, min_arr, max_arr)

    def normalizexy_array(self, arr):
        """
    normalize array: positive maximum is [pmx] * max_feed_factor and positive minimum is 0

    Precondition: [arr] is a positive array
    """
        max_feed_factor = 2.0
        max_feed = self.pmx * max_feed_factor
        maxv = np.max(arr)
        minv = np.min(np.abs(arr))
        norm_arr = (arr - minv) * max_feed / maxv
        return norm_arr

    def bound_extremes_array(self, arr):
        return np.clip(arr, self.pmin, self.pmx, out=arr)

    def dynamic_amplification(self, arr):
        """
    Extract peaks and amplify audio signal change over a threshold. 
    Incorporate baseline activity to [arr]
    Expand short peaks

    precondition: 255 >= [pmx] >= 0
    """
        frame_len = 2
        threshold = self.pmx / 3
        baseline = np.resize(
            np.array([self.baseline, self.baseline, self.baseline, self.baseline, self.baseline, 0, 0, 0, 0, 0]), len(arr))
        arr_res = np.copy(arr)
        for i in range(1, len(arr)):
            if self.local_peaks > arr[i] > threshold and arr[i] > arr[
                    i - 1] and arr[i] > arr[min(i + 1,
                                                len(arr) - 1)]:
                arr_res[i] = self.local_peaks
            if arr[i] == self.pmx and max(arr[i - frame_len:i]) < self.pmx:
                arr[i] = self.pmx * 2
            arr_res[i] = max(arr_res[i], baseline[i])
        return arr_res

    def int_array(self, arr):
        """
      convert [arr] to integer array
      """
        return arr.astype(int)

    def set_sound(self, file_path):
        mixer.music.load(file_path)

    # communicate with arduino board to control regulator pressure
    def send_serial(self, file_name):
        """
      send serial data to arduino
      """
        ser = serial.Serial(self.com_port, self.baud_rate)
        time.sleep(2)  # wait for serial connection
        sending = True
        try:
            while sending:
                data = self.audio_catalog[file_name]
                mixer.music.play()
                for d in data:
                    print(d)
                    ser.write(struct.pack('>B', d))
                    time.sleep(self.transfer_rate)
        except KeyboardInterrupt:
            print("Back to Main")
        ser.write(struct.pack('>B', 1))
        ser.write(struct.pack('>B', 1))
        mixer.music.stop()
        ser.close()


if __name__ == "__main__":

    com_port = "/dev/cu.usbmodem142301"
    transfer_rate = 0.5
    dtime = 0.1
    freq = 22050

    compiler = Compiler(dtime, transfer_rate, com_port, freq)

    compiler.regval_interactive()
