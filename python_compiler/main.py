import numpy as np
import fft
import audio_interpreter
import freq_filter
import time
import matplotlib.pyplot as plt 
import serial

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
  [arr] consecutive local blocks of time intervals [dt] seconds 
  """
  freq_dt = int(freq*dt)
  max_arr = np.zeros(len(arr)//freq_dt)
  for i in range(len(arr)//freq_dt):
    max_arr[i] = np.max(np.abs(arr[i*freq_dt:(i+1)*freq_dt]))
  plot_general(max_arr)
  return max_arr

def reg_array(arr, dt):
  reg_arr = (np.roll(arr,-1) - arr) / dt
  plot_general(reg_arr)
  return reg_arr

def reg_calibrate_array(arr, dt, transfer_rate):
  grouping = int(transfer_rate / dt)
  reg_arr = np.nanmean(np.pad(arr.astype(float), (0, (grouping - arr.size%grouping) % grouping), constant_values=np.NaN).reshape(-1, grouping), axis=1)
  plot_general(reg_arr)
  return reg_arr 

def normalizexy_array(arr, noise):
  """
  normalize array: positive maximum == 255 && positive minimum == 0
  """
  maxv = np.max(arr)
  minv = np.min(np.abs(arr)) 
  norm_arr = (arr - minv) * (255-np.abs(noise))/maxv
  plot_general(norm_arr)
  return norm_arr

def send_serial(port, file_name, transfer_rate):
  """
  send serial data to arduino
  """
  baudrate = 9600
  ser = serial.Serial(port, baudrate)
  time.sleep(2)   #wait for serial connection
  for d in audio_catalog[file_name]:
    ser.write(bytes(d))
    time.sleep(transfer_rate)
  ser.close()

def regval_real(port, dt=1, transfer_rate = 1, noise=0):
  """
  establish a connection with an Arduino system via [port]

  break down file in time blocks of [dt] seconds and contruct the breathing function
  based on the derivative of localized maximums

  rate of communication is [transfer_rate] Hz. 

  precondition: transfer_rate >= dt
  """
  cont = True
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
          plot_general(arr, sampling_freq=freq)
          max_arr = max_array(arr, dt, freq)
          reg_arr = reg_array(max_arr, dt)
          reg_arr = reg_calibrate_array(reg_arr, dt, transfer_rate)
          norm_reg_arr = normalizexy_array(reg_arr, noise)
          norm_reg_arr = noisy_array(norm_reg_arr, -1*noise, noise)
          audio_catalog[file_name] = norm_reg_arr
          print("cached")
        else:
          print("retrieve from cach\n")
        send_serial(port, file_name, transfer_rate)
        print("Finished")
    except Exception as err:
      print(f"Invalid.: {err}\nTry again\n")

def regval_fft(file, max_freq, dt=0.01, default_cos_funcs = 10):
  """
  return cosine function reconstructed from fast fourier transform of [file]
  """
  arr, freq = audio_interpreter.audio_to_array(file)
  arr = max_array(arr, dt, freq)
  freq = 1/dt
  arx, ary = fft.norm_fft(arr,sampling_freq=freq,max_freq=max_freq)
  freq_amp= fft.peaks(arx, ary)
  freq_amp = fft.normalize_array(freq_amp)
  cos_func = fft.cos_reconstruction(freq_amp, default_cos_funcs)
  return cos_func




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
  
if __name__ == "__main__":

  # Initialize parameters
  com_port = ""
  transfer_rate = 1
  dtime = 0.1
  noise = 25

  file = "bird_song1.wav"
  # file = "bird_song2.wav"
  # file = "forest1.wav"
  # file = "ocean1.wav"
  # file = "ocean2.wav"
  # file = "ocean3.wav"
  # file = "ocean4.wav"
  # file = "ocean5.wav"
  # file = "thunder_storm1.wav"

  regval_real(com_port, dtime, transfer_rate, noise)
  # test(file)