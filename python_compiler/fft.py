import numpy as np
from math import pi
import matplotlib.pyplot as plt
from detecta import detect_peaks

# Set figure size
plt.rcParams["figure.figsize"] = (15, 6)

def norm_fft(y, sampling_freq=1, max_freq=0):
    """
    perform fast fourier transform on [y] and return the two dimensions [xf] and [yf].

    Support 16 bit data
    """
    N = y.shape[0]
    # Nf = N // 2
    xf = np.fft.rfftfreq(N, d = 1/sampling_freq) 
    yf = np.fft.rfft(y) * 2 / N
    if max_freq > 0:
        n = int(N * max_freq // sampling_freq)
        xf = xf[:n]
        yf = yf[:n]
    return xf, abs(yf)

def plot_fft(y, sampling_freq=1, max_freq=0):
    """
    plot fast fourier transform of [y].
    """
    xf, yf = norm_fft(y, sampling_freq, max_freq)
    _, axis = plt.subplots(1, 1)
    axis.set_title('Fourier Transform')
    axis.plot(xf, yf)
    sampling_freq = int(sampling_freq/2)
    if max_freq <= 0:
        max_freq = sampling_freq
    axis.set_xlabel(f'Frequency at {max_freq} / {sampling_freq} Hz')
    axis.set_ylabel('Amplitude')
    plt.show()

def inv_fft(y):
    return np.fft.ifft(y)

def normalize_array(freq_amp, means = [1,1]):
    """
    returns a weighted [freq_amp] where the averages of amplitudes and frequencies are respectively scaled.

    [means][0] is the value for frequencies to normalize to.
    [means][1] is the value for amplitudes to normalize to.
    """
    return freq_amp

def peaks(x, y):
    """
    return a two row array where the rows are frequencies and amplitudes of peaks. 
    Sorted by amplitudes in descending order.
    """
    d = len(x)/200
    ymean = np.mean(y)
    ystd = np.std(y) 
    # peaks, property = find_peaks(y,height=ymean+2*ystd, distance=d)
    peak_locations = detect_peaks(y, mph=ymean+1*ystd, mpd=d, show=True)
    freqs = x[peak_locations]
    amplitudes = abs(y[peak_locations])
    freq_amp = np.vstack((freqs, amplitudes))
    freq_amp = freq_amp[:,np.argsort(-1*freq_amp[1,:])]
    # print(freq_amp)
    return freq_amp

def cos_reconstruction(freq_amp, components, bias=0):
    """
    idea: use knn initialization to select components
    """
    iterations = min(components, len(freq_amp[0]))
    def cos_func(t,weight=1):
        regval = bias
        for i in range(iterations):
            regval += freq_amp[1,i] * np.cos(2*pi*t*freq_amp[0,i]*weight)
        return regval
    return cos_func


if __name__ == "__main__":
    pass
    # # How many time points are needed i,e., Sampling Frequency
    # samplingFrequency = 100

    # # At what intervals time points are sampled
    # samplingInterval  = 1 / samplingFrequency

    # # Begin time period of the signals
    # beginTime = 0

    # # End time period of the signals
    # endTime = 5

    # # Frequency of the signals
    # signal1Frequency = 3
    # signal2Frequency = 13
    # signal3Frequency = 35

    # # Time points
    # time = np.arange(beginTime, endTime, samplingInterval)

    # noise = np.random.rand(time.shape[-1]) * 3

    # # Create sine waves
    # amplitude1 = 1 * np.sin(2*np.pi*signal1Frequency*time) 
    # amplitude2 = 2 * np.sin(2*np.pi*signal2Frequency*time)
    # amplitude3 = 0.5 * np.sin(2*np.pi*signal3Frequency*time) 
    # amplitude = amplitude1 + amplitude2 + amplitude3 + noise

    # plot_fft(amplitude, samplingFrequency)

    # #try inverse fft function
    # xf_, yf_ = norm_fft(amplitude1, samplingFrequency) 
    # iyf = np.fft.fft(yf_)
    # plot_general(y=iyf, sampling_freq=samplingFrequency)


    # fourier transform test
    # frequencies: 1/3 & 2
    # fft.plot_general(np.cos(1/3*2*np.pi*np.arange(0,100,0.1))+np.cos(2*2*np.pi*np.arange(0,100,0.1)),sampling_freq=10)
    # fft.plot_fft(np.cos(1/3*2*np.pi*np.arange(0,100,0.1))+np.cos(2*2*np.pi*np.arange(0,100,0.1)),sampling_freq=10, max_freq=3)

