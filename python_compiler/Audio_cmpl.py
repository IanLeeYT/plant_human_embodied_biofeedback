import numpy as np
import audio_interpreter
import matplotlib.pyplot as plt
import time
import struct
from pygame import mixer
import serial
import os
from tkinter.filedialog import askopenfilename


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


class Audio_Compiler:

    def __init__(self, dtime, transfer_rate, com_port, freq):
        # Initialize constants
        self.constants = {
            "reg_max": 50,
            "reg_min": 30,
            "reg_baseline": 32,
            "reg_map_max": 200,
            "window_size": 6
        }

        self.transfer_rate = transfer_rate
        self.dtime = dtime
        self.freq = freq

        mixer.init()  # initialize audio port

        self.audio_catalog = dict()  # cache

        # Communication port
        self.com_port = com_port
        self.baud_rate = 9600
        # sd.default.samplerate = fs
        # data, fs = sf.read(filename, dtype='float32')
        # sd.play(data, fs)
        # self.raw_data = None

    # discriminative main function

    def interactive(self):
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
                user = input("Enter to continue or quit: ").strip()
                if user == "end" or user == "quit":
                    print("Thank You")
                    cont = False
                else:
                    user = askopenfilename()
                    file_name = audio_interpreter.audio_path_breakdown(user)[0]
                    if file_name not in self.audio_catalog:
                        print("...Loading...\n")
                        arr = audio_interpreter.audio_to_array(user, self.freq)
                        plot_general(arr, sampling_freq=self.freq)
                        amp_arr = self.max_array(arr)
                        plot_general(amp_arr, sampling_freq=1/self.dtime)
                        reg_arr = self.calibrate_array(amp_arr)
                        plot_general(reg_arr, sampling_freq=1 /
                                     self.transfer_rate)
                        reg_arr = self.bound_outliers(reg_arr)
                        # print(reg_arr)
                        plot_general(reg_arr, sampling_freq=1 /
                                     self.transfer_rate)
                        norm_reg_arr = self.normalizexy_array(reg_arr)
                        # print(norm_reg_arr)
                        plot_general(
                            norm_reg_arr, sampling_freq=1/self.transfer_rate)
                        norm_reg_arr = self.dynamic_amplification(norm_reg_arr)
                        # print(norm_reg_arr)
                        plot_general(
                            norm_reg_arr, sampling_freq=1/self.transfer_rate)
                        norm_reg_arr = self.baseline_arr(norm_reg_arr)
                        # print(norm_reg_arr)
                        plot_general(
                            norm_reg_arr, sampling_freq=1/self.transfer_rate)
                        norm_reg_arr = self.bound_extremes_array(norm_reg_arr)
                        # print(norm_reg_arr)
                        plot_general(
                            norm_reg_arr, sampling_freq=1/self.transfer_rate)
                        self.audio_catalog[file_name] = self.int_array(
                            norm_reg_arr)
                        print("cached")
                    else:
                        print("retrieved from cach\n")
                    self.set_sound(user)
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
        # compensate for regulator time delay
        return max_arr[int(1/self.transfer_rate):]

    def var_array(self, arr):
        """
    return an array where elements are the maximum of data in
    [arr] consecutive local buckets of time intervals [dt] seconds
    """
        freq_dt = int(self.freq * self.dtime)
        var_arr = np.zeros(len(arr) // freq_dt)
        for i in range(len(arr) // freq_dt):
            var_arr[i] = np.var(arr[i * freq_dt:(i + 1) * freq_dt])
        return var_arr[1:]  # compensate for regulator time delay

    def calibrate_array(self, arr):
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
    normalize array: positive maximum is [reg_map_max] and positive minimum is 0

    Precondition: [arr] is a positive array
    """
        maxv = np.max(arr)
        minv = np.min(np.abs(arr))
        norm_arr = (arr - minv) * self.constants["reg_map_max"] / maxv
        return norm_arr

    def bound_extremes_array(self, arr):
        return np.clip(arr, self.constants["reg_min"], self.constants["reg_max"], out=arr)

    def smooth_array(self, arr, strength):
        pass

    def dynamic_amplification(self, arr):
        """
    Extract peaks and amplify audio signal change over a threshold.

    precondition: 255 >= [pmx] >= 0
    """
        means = np.lib.stride_tricks.sliding_window_view(
            arr, self.constants["window_size"])
        means = np.concatenate(
            (arr[:self.constants["window_size"]-1], np.mean(means, axis=1)))
        means[means == 0] = 1
        return arr * arr / means

    def xsinx(self, amp, f, t, c):
        arr = amp * np.sin(f * t) + c
        # plot_general(arr)
        return arr

    def baseline_arr(self, arr):
        """
        Incorporate baseline activity to [arr]
        """
        # amp = (self.constants["reg_baseline"] - self.constants["reg_min"]) / 2
        # c = self.constants["reg_min"] + amp
        # t = np.arange(0, arr.shape[0] * self.transfer_rate, self.transfer_rate)
        # f = 0.5
        # baseline = self.xsinx(amp, f, t, c)
        # return np.maximum(arr, baseline)
        return arr

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
            print("quit process")
        except Exception as e:
            print(f"unexpected error: {e}")
        ser.write(struct.pack('>B', 1))
        ser.write(struct.pack('>B', 1))
        mixer.music.stop()
        ser.close()


if __name__ == "__main__":

    com_port = "/dev/cu.usbmodem141101"
    transfer_rate = 0.5
    dtime = 0.1
    freq = 22050

    compiler = Audio_Compiler(dtime, transfer_rate, com_port, freq)

    compiler.interactive()
