import numpy as np
from pydub import AudioSegment
from shutil import copyfile
import os
import librosa
# from scipy.io.wavfile import read

file_extentions = [".wav", ".mp3"]


def audio_path_breakdown(file_path):
    file = os.path.splitext(os.path.basename(file_path))
    file_name = file[0]
    file_ext = file[1]
    if file_ext is "" or file_ext not in file_extentions:
        raise Exception("Invalid File Type")
    return file_name, file_ext


def mp3_to_wav(file_path, new_file_path):
    sound = AudioSegment.from_mp3(file_path)
    sound.export(new_file_path, format="wav")


def audio_to_array(file_path, sr_freq):
    """
  return the np array representing audio [file_path] and the sampling frequency (default = 11025hz)

  copies and converts the file into audio/_name_of_file_.wav if needed
  """
    file_name, file_ext = audio_path_breakdown(file_path)
    new_file_path = "audio/" + file_name + ".wav"
    new_file_exist = os.path.exists(new_file_path)
    if not new_file_exist:
        if file_ext == ".mp3":
            mp3_to_wav(file_path, new_file_path)
        else:
            copyfile(file_path, new_file_path)
    arr = librosa.load(new_file_path,
                       sr=sr_freq)[0]  # sampling rate is 22050hz
    # rate, arr = read(new_file_path)
    audio_array = np.array(arr, dtype=float)
    audio_array = audio_array if audio_array.ndim == 1 else audio_array[:, 0]
    return audio_array
