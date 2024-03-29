# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:56:21 2023

@author: Sanyam
"""

import matplotlib.pyplot as plt
import wave
import numpy as np
import scipy
from scipy import signal
from scipy.signal import hilbert      #for signal envelope



# Python3 program to illustrate
# splitting stereo audio to mono
# using pydub

# Import AudioSegment from pydub
from pydub import AudioSegment

# Open the stereo audio file as
# an AudioSegment instance
stereo_audio = AudioSegment.from_file(r'C:\Users\kando\OneDrive\Documents\srijan\reading_1.wav')
#

# Calling the split_to_mono method
# on the stereo audio file
mono_audios = stereo_audio.split_to_mono()

# Exporting/Saving the two mono
# audio files present at index 0(left)
# and index 1(right) of list returned
# by split_to_mono method
mono_left = mono_audios[0].export(r'C:\Users\kando\OneDrive\Documents\srijan\mono_left.wav',format="wav")
# mono_right = mono_audios[1].export(
# 	"C:\\Users\\NEERAJ RANA\\Desktop\\GFG_Articles\\pydub\\mono_right.wav",
# 	format="wav")


# reading the audio file
raw = wave.open(r'C:\Users\kando\OneDrive\Documents\srijan\mono_left.wav')

# reads all the frames
# -1 indicates all or max frames
signal1 = raw.readframes(-1)
signal1 = np.frombuffer(signal1, dtype="int16")

# gets the frame rate
f_rate = raw.getframerate()
print(f_rate)


time = np.linspace(0,  # start
                    len(signal1) / f_rate,
    num=len(signal1)
)

print(len(signal1))


def cross_correlate(input1, input2):
    corr = scipy.signal.correlate(input1, input2, mode='full', method='auto')
    arr1 = np.arange(0, len(input1))
    arr2 = np.arange(-len(input2)+1, len(input1))
    figure, axes = plt.subplots(2, 1)
    axes[0].plot(arr1, input1)
    axes[0].set_title("Sound Signal waveform")
    axes[1].plot(arr2, corr)
    axes[1].set_title("Cross Correlation")
    figure.tight_layout()
    plt.show()
    return corr



t1=483
t2=484
desired_signal= signal1[f_rate*t1 :f_rate*t2 ]
time = np.linspace(t1,  t1+len(desired_signal)/f_rate, num=len(desired_signal) )


# FILTERING THROUGH BAND PASS
fL = 1000
fH = 4000
Wn= [fL,fH]
sos= scipy.signal.butter(2,Wn,fs= f_rate, btype='band', output= 'sos')
filtered_signal= scipy.signal.sosfilt(sos,desired_signal)
analytic_signal = hilbert(filtered_signal)
amplitude_envelope = np.abs(analytic_signal)





def Amp_Envelope (signal, interval_size):
    amp_env = []
    # calculate amplitude envelope for each frame
    for i in range(0, len(signal)):
        amplitude_envelope_current_frame = max(signal[i:i + interval_size])
        amp_env.append(amplitude_envelope_current_frame)

    return np.array(amp_env)

amp_env= Amp_Envelope(desired_signal,50)

def thirty_percent_threshold(input1):
    index = 0
    peaks_array, _ = signal.find_peaks(input1)
    for i in range(len(input1)):
        if input1[i] >= 0.3*max(peaks_array):
            index= i
            break
    return index

def smoothening_envelope(input_amp_env):
    index = thirty_percent_threshold(input_amp_env)
    sigma = 300
    gx = np.arange(-3 * sigma, 3 * sigma)
    gaussian = np.exp(-(gx / sigma) ** 2 / 2)
    smoothened_env = np.convolve(input_amp_env, gaussian, mode="same")
    resulting_array = smoothened_env
    #resulting_array= np.concatenate( (input_amp_env[:index],smoothened_env) )

    fig_f, axs_f = plt.subplots(4, 1)
    axs_f[0].plot(time, desired_signal)
    axs_f[0].set_title("Section of original signal containing notification waveform")

    axs_f[1].plot(time, filtered_signal)
    axs_f[1].set_title("Filtered Signal")

    axs_f[2].plot(np.arange(0,len(input_amp_env)),input_amp_env)
    axs_f[2].set_title("Amplitude Envelope")

    axs_f[3].plot(np.arange(0,len(resulting_array)),resulting_array)
    axs_f[3].set_title("Final Smoothened Envelope")

    fig_f.tight_layout()
    plt.show()
    return resulting_array


def peak_return(input1):
    new_smooth_env = smoothening_envelope(input1)
    peaks_new, _ = signal.find_peaks(new_smooth_env)
    return peaks_new

print(peak_return(amp_env))

corr= cross_correlate(signal1,amplitude_envelope)

