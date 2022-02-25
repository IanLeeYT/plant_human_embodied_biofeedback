
#%%
import numpy as np
import fft
import audio_interpreter
import freq_filter
import time
import matplotlib.pyplot as plt 
import serial
import struct
from pygame import mixer

#%%
# cached data available for future usage
audio_catalog = dict()

def plot_general(y, x=[], sampling_freq=1, title="Plot"):
    """
    general format for plotting frequency based data.
    """
    if not isinstance(y, np.ndarray) and not isinstance(y,list):
        print("Can not be plotted")
        return
    _, axis = plt.subplots(1, 1)
    axis.set_title(title)
    if x == []:
        len_y = len(y)
        x = np.linspace(0,len_y/sampling_freq,len_y) 
    axis.plot(x,y)
    axis.set_xlabel("Time (s)")
    plt.show()

def noisy_array(arr,low,high):
    return arr + np.random.uniform(low, high, arr.shape[0]) 

def max_array(arr, dt, freq):
  """
  return an array where elements are the maximum of data in 
  [arr] consecutive local buckets of time intervals [dt] seconds 
  """
  freq_dt = int(freq*dt)
  max_arr = np.zeros(len(arr)//freq_dt)
  for i in range(len(arr)//freq_dt):
    max_arr[i] = np.max(np.abs(arr[i*freq_dt:(i+1)*freq_dt]))
  return max_arr

# not used
def derivative_array(arr, dt):
  """
  return the first order derivative (difference) of [arr]
  """
  reg_arr = (np.roll(arr,-1) - arr) / dt
  return reg_arr

def reg_calibrate_array(arr, dt, transfer_rate):
  """
  adjust length of [arr] via averaging buckets of elements. Grouping size is [transfer_rate]/[dt]

  Precondition: [transfer_rate] >= [dt]
  """
  grouping = int(transfer_rate / dt)
  reg_arr = np.nanmean(np.pad(arr.astype(float), (0, (grouping - arr.size%grouping) % grouping), constant_values=np.NaN).reshape(-1, grouping), axis=1)
  return reg_arr 

def normalizexy_array(arr, pmx):
  """
  normalize array: positive maximum == [pmx] * max_feed_factor && positive minimum == 0

  Precondition: arr is a positive array
  """
  max_feed_factor = 2.0
  max_feed = pmx * max_feed_factor
  maxv = np.max(arr)
  minv = np.min(np.abs(arr)) 
  norm_arr = (arr - minv) * max_feed / maxv
  return norm_arr

def scale_array(arr, scale):
  """
  scale [arr] (type: array) by [scale]
  """
  return arr * scale 

def bound_outliers(arr, n_sd):
  """
  remove elements in [arr] that are [n_sd] standard deviations away
  """
  mean = np.mean(arr)
  std = np.std(arr)
  max_arr = mean + n_sd * std
  min_arr = mean - n_sd * std
  return np.clip(arr, min_arr, max_arr)

def int_array(arr):
  """
  convert [arr] to integer array
  """
  return arr.astype(int) 

def bound_extremes_array(arr, uppder_bound, lower_bound):
  return np.clip(arr, lower_bound, uppder_bound, out=arr)

def dynamic_amplification(arr, pmx):
  """
  Extract peaks and amplify audio signal change over a threshold. 
  Incorporate baseline activity to [arr]
  Expand short peaks
  
  precondition: 255 >= [mx] >= 0
  """
  frame_len = 5
  threshold = pmx/3
  pmids = pmx - 1
  pmidw = pmx - 2
  pweak = pmx - 3
  pnone = 0
  baseline = np.resize(np.array([pweak, pweak, 0, 0, 0]), len(arr))
  arr_res = np.copy(arr)
  for i in range(len(arr)):
    if pmids > arr[i] > threshold and arr[i] > arr[i-1] and arr[i] > arr[min(i+1,len(arr)-1)]:
      arr_res[i] = pmids
    arr_res[i] = max(arr_res[i], baseline[i])
  return arr_res

def set_sound(file_path):
  mixer.music.load(file_path) 

# communicate with arduino board to control regulator pressure
def send_serial(port, file_name, transfer_rate):
  """
  send serial data to arduino
  """
  baudrate = 9600
  ser = serial.Serial(port, baudrate)
  time.sleep(2)   #wait for serial connection
  sending = True 
  # when user input detected, break loop
  try:
    while sending:
      data = audio_catalog[file_name]
      mixer.music.play()
      for d in data:
        print(d)
        ser.write(struct.pack('>B',d))
        time.sleep(transfer_rate)
  except KeyboardInterrupt:
    print("Back to Main")
  ser.write(struct.pack('>B',1))
  mixer.music.stop()
  ser.close()

# discriminative function (uses helepr functions declared above)
def regval_real(port, dt=0.1, transfer_rate = 1):
  """
  opens a user session where user can input the path to an audio file for pneumatic actuation or input end/quit to end session.

  breaks down audio file in time blocks of [dt] seconds and contruct the breathing function
  based on the localized maximums. 

  establishes a connection with an Arduino system via [port]

  rate of communication is [transfer_rate] Hz

  reg_val response values:
    min - max : 30 - 34 

  precondition: [transfer_rate] >= [dt]
  """
  cont = True
  pmx = 35
  pmin = pmx - 10
  n_sd = 2.5  # for removing outliers in array
  mixer.init() # initialize pygame.mixer for audio
  while cont:
    try:
      user = input("Please enter the path to audio file: ")
      user = user.strip()
      if user == "end" or user == "quit":
          cont = False
          print("Thank You")
      else:
        file_name = audio_interpreter.audio_path_breakdown(user)[0]
        if file_name not in audio_catalog.keys():
          print("...Loading...\n")  
          arr, freq = audio_interpreter.audio_to_array(user)
          max_arr = max_array(arr, dt, freq)
          reg_arr = reg_calibrate_array(max_arr, dt, transfer_rate)
          reg_arr = bound_outliers(reg_arr, n_sd)
          norm_reg_arr = normalizexy_array(reg_arr, pmx)
          norm_reg_arr = bound_extremes_array(norm_reg_arr, pmx, pmin)
          norm_reg_arr = dynamic_amplification(norm_reg_arr, pmx)
          plot_general(norm_reg_arr)
          audio_catalog[file_name] = int_array(norm_reg_arr)
          print(f"{audio_catalog[file_name]} cached")
        else:
          print("retrieve from cach\n")
        set_sound("audio/"+user)
        send_serial(port, file_name, transfer_rate)
        print("Finished")
    except Exception as err:
      print(f"Invalid.: {err}\nTry again\n")


# generative function (uses helepr functions declared above)
def regval_fft(file, max_freq, dt=0.01, default_cos_funcs = 10):
  """
  return cosine function reconstructed from fast fourier transform of [file]
  """
  arr, freq = audio_interpreter.audio_to_array(file)
  tlen = len(arr) // freq
  tarray = np.arange(tlen)
  arr = max_array(arr, dt, freq)
  freq = 1/dt
  arx, ary = fft.norm_fft(arr,sampling_freq=freq,max_freq=max_freq)
  freq_amp= fft.peaks(arx, ary)
  freq_amp = fft.normalize_array(freq_amp)
  cos_func = fft.cos_reconstruction(freq_amp, default_cos_funcs)
  return cos_func(tarray)


# for testing only
def test(file):
  """
  for testing purposes only
  """
  arr, freq = audio_interpreter.audio_to_array(file)
  # filtered_arr = freq_filter.butter_lowpass_filter(arr, 50, freq) 

  plot_general(arr, sampling_freq=freq)

  fft.plot_fft(arr, sampling_freq=freq, max_freq=100)

  cos_func = regval_fft(file, max_freq=100)
  plot_general(cos_func(np.arange(200)))

  # fourier transform test
  # frequencies: 1/3 & 2
  test = np.cos(1/13*2*np.pi*np.arange(0,100,0.1))+np.cos(1/5*2*np.pi*np.arange(0,100,0.1)+np.cos(1/7*2*np.pi*np.arange(0,100,0.1))+np.cos(3*2*np.pi*np.arange(0,100,0.1)))
  testx, testy = fft.norm_fft(test,sampling_freq=10)
  freq_amp= fft.peaks(testx, testy)
  freq_amp = fft.normalize_array(freq_amp)
  cos_func = fft.cos_reconstruction(freq_amp,10)
  fft.plot_fft(test,sampling_freq=10, max_freq=5)
  plot_general(test,sampling_freq=10)
  plot_general(cos_func(np.arange(0,100,0.1)))
  plot_general(cos_func(np.arange(0,100)))
  
#%%
if __name__ == "__main__":

  # communication port
  com_port = "/dev/cu.usbmodem14201"

  # Initialize parameters
  transfer_rate = 1
  dtime = 0.1


  # file = "bird_song1.wav"
  # file = "bird_song2.wav"
  # file = "forest1.wav"
  # file = "ocean1.wav"
  # file = "ocean2.wav"
  # file = "ocean3.wav"
  # file = "ocean4.wav"
  # file = "ocean5.wav"
  # file = "thunder_storm1.wav"
  # test(file)

  # main function for analyzing audio files and arduino communication
  regval_real(com_port, dtime, transfer_rate)


# TODO
# 1. baseline activity
# 2. microphone input and live interaction
# 3. sync with audio output