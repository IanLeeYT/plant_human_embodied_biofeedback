import numpy as np
import fft
import audio_interpreter
import subprocess

def update_arduino(path):
  with open(path, "r+") as f:
    rlines = f.readlines()
    print(rlines)
    f.close()
  # subprocess.run(f"{path}")

# upload arduino code
# https://forum.arduino.cc/t/uploading-arduino-code-interactively-using-python/368055
# https://playground.arduino.cc/Learning/CommandLine/
# https://github.com/arduino/Arduino/blob/master/build/shared/manpage.adoc
# https://github.com/sudar/Arduino-Makefile
# https://playground.arduino.cc/BuildArduino/Py/
# https://arduino.stackexchange.com/questions/15893/how-to-compile-upload-and-monitor-via-the-linux-command-line

def regval(file,max_freq,default_cos_funcs = 10):
  arr, freq = audio_interpreter.audio_to_array(file)
  arx, ary = fft.norm_fft(arr,sampling_freq=freq,max_freq=max_freq)
  freq_amp= fft.peaks(arx, ary)
  freq_amp = fft.normalize_array(freq_amp)
  cos_func = fft.cos_reconstruction(freq_amp, default_cos_funcs)
  return cos_func

if __name__ == "__main__":
  # update_arduino("../OceanWaveModel_5_24_21/OceanWaveModel_5_24_21.ino")

  file = "bird_song1.wav"
  # file = "bird_song2.wav"
  # file = "forest1.wav"
  # file = "ocean1.wav"
  # file = "ocean2.wav"
  # file = "ocean3.wav"
  # file = "ocean4.wav"
  # file = "ocean5.wav"
  # file = "thunder_storm1.wav"

  arr, freq = audio_interpreter.audio_to_array(file)

  fft.plot_general(arr, sampling_freq=freq)
  fft.plot_fft(arr, sampling_freq=freq)
  fft.plot_fft(arr, sampling_freq=freq, max_freq=100)
  fft.plot_fft(arr, sampling_freq=freq, max_freq=20)

  # Serial Transfer

  cos_func = regval(file, max_freq=20)
  fft.plot_general(cos_func(np.arange(100)))

  # fourier transform test
  # frequencies: 1/3 & 2
  # fft.plot_general(np.cos(1/3*2*np.pi*np.arange(0,100,0.1))+np.cos(2*2*np.pi*np.arange(0,100,0.1)),sampling_freq=10)
  # fft.plot_fft(np.cos(1/3*2*np.pi*np.arange(0,100,0.1))+np.cos(2*2*np.pi*np.arange(0,100,0.1)),sampling_freq=10, max_freq=3)
