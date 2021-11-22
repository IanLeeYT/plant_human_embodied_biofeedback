from scipy.signal import butter, lfilter

def butter_lowpass(cutoff, freqs, order=5):
    nyq = freqs / 2
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, freqs, order=5):
    b, a = butter_lowpass(cutoff, freqs, order=order)
    filtered_data = lfilter(b, a, data)
    return filtered_data
