import numpy as np
import wave
import pyaudio
import time
import threading

global audio_buff, out_stream

waterfall_duration = 2
waterfall_dt = 0.0005
waterfall_update_dt = 0.1
sample_rate = 6000
max_freq = 2000
waterfall_df = 20
fft_len = int(sample_rate / waterfall_df)
nFreqs = int(max_freq / waterfall_df)

audio_buff = np.zeros(fft_len, dtype=np.float32)
out_stream = None

pya = pyaudio.PyAudio()

def find_device(device_str_contains):
    if(not device_str_contains): #(this check probably shouldn't be needed - check calling code)
        return
    print(f"[Audio] Looking for audio device matching {device_str_contains}")
    for dev_idx in range(pya.get_device_count()):
        name = pya.get_device_info_by_index(dev_idx)['name']
        match = True
        for pattern in device_str_contains:
            if (not pattern in name): match = False
        if(match):
            print(f"[Audio] Found device {name} index {dev_idx}")
            return dev_idx
    print(f"[Audio] No audio device found matching {device_str_contains}")


def start_live(input_device_idx, output_device_idx):
    global out_stream
    stream = pya.open(
        format = pyaudio.paInt16, channels=1, rate = sample_rate,
        input = True, input_device_index = input_device_idx,
        frames_per_buffer = len(audio_buff), stream_callback=_callback,)
    stream.start_stream()
    out_stream = pya.open(format=pyaudio.paInt16, channels=1, rate=sample_rate,
                          output=True,
                          output_device_index = output_device_idx)
    threading.Thread(target = threaded_output).start()
    threading.Thread(target = threaded_get_sigs).start()

def threaded_output():
    global audio_buff
    while(True):
        time.sleep(0)
        wf = np.int16(audio_buff * 32767)
        out_stream.write(wf.tobytes())

def _callback(in_data, frame_count, time_info, status_flags):
    global audio_buff
    samples = np.frombuffer(in_data, dtype=np.int16).astype(np.float32)
    ns = len(samples)
    audio_buff = samples
    time.sleep(0)
    return (None, pyaudio.paContinue)


global waterfall
waterfall = np.zeros((int(waterfall_duration / waterfall_dt), nFreqs))
def threaded_get_sigs():
    global waterfall
    speclev = 1
    while(True):
        time.sleep(waterfall_dt)
        z = np.fft.rfft(audio_buff)[:nFreqs]
        p = z.real*z.real + z.imag*z.imag
        speclev = np.max([speclev,np.max(p)])
        p /= speclev
        waterfall[:-1,:] = waterfall[1:,:] 
        waterfall[-1,:] = np.clip(10*p, 0, 1)

def time_plot():
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(figsize = (8,3))
    waterfall_plot = axs.imshow(waterfall, extent = (0, waterfall.shape[1]*50, 0, waterfall.shape[0]))

    #axs[0].set_xticks(np.array([95,105])-0.5, labels=["",""])
    #axs[0].set_ylim(-10,0)
    while(True):
        waterfall_plot.set_data(waterfall)
        plt.pause(waterfall_update_dt)

    
input_device_idx =  find_device(['Mic', 'CODEC'])
output_device_idx =  find_device(['Spea', 'High'])
start_live(input_device_idx, output_device_idx)
time_plot()



