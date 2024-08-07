import os
import wave
import subprocess
import sys
import time
import threading
import queue
import uuid

try:
    import torch
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "torch"])

try:
    import win32pipe
    import win32file
    import pywintypes
    import win32security
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
    import win32pipe
    import win32file
    import pywintypes
    import win32security

try:
    from faster_whisper import WhisperModel
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "faster_whisper"])
    from faster_whisper import WhisperModel

try:
    import pyaudio
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio"])
    import pyaudio

try:
    import numpy as np
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    import numpy as np

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def list_microphones(p):
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    devices = []
    for i in range(0, num_devices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        if device_info.get('maxInputChannels') > 0:
            devices.append((i, device_info.get('name')))
    return devices

def find_vive_microphone(devices):
    for index, name in devices:
        if "VIVE" in name:
            return index, name
    return None, None

def record_chunk(p, stream, chunk_queue, chunk_length=2, threshold=500):
    CHUNK_SIZE = int(16000 / 1024 * chunk_length) * 1024
    while True:
        chunk_data = stream.read(CHUNK_SIZE)
        audio_data = np.frombuffer(chunk_data, dtype=np.int16)
        peak_amplitude = np.abs(audio_data).max()
        if peak_amplitude > threshold:
            chunk_queue.put(chunk_data)

def save_wave_file(data, file_path, p):
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(data)
    wf.close()

def transcribe_chunk(model, data, p, transcription_queue):
    chunk_file = f"temp_chunk_{uuid.uuid4()}.wav"
    save_wave_file(data, chunk_file, p)
    segments, info = model.transcribe(chunk_file, beam_size=5, language="nl")
    transcription = ''.join(segment.text for segment in segments)
    if os.path.exists(chunk_file):
        os.remove(chunk_file)
    transcription_queue.put(transcription)

def main():
    print('main started')

    if torch.cuda.is_available():
        wdevice = "cuda"
        print("CUDA is available. Using GPU.")
    else:
        wdevice = "cpu"
        print("CUDA is not available. Using CPU.")
    
    model = WhisperModel("small", device=wdevice, compute_type="float32")
    print('faster whisper model initialized')

    p = pyaudio.PyAudio()
    print('pyaudio initialized')

    microphones = list_microphones(p)
    print("Available microphones:")
    for index, name in microphones:
        print(f"{index}: {name}")

    mic_index, mic_name = find_vive_microphone(microphones)
    if mic_index is None:
        print("Vive microphone not found.")
        mic_index = microphones[0][0]
        print(f"Using microphone: {microphones[1][1]}")
    else:
        print(f"Using microphone: {mic_name}")

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, input_device_index=mic_index, frames_per_buffer=1024)

    chunk_queue = queue.Queue()
    transcription_queue = queue.Queue()

    recording_thread = threading.Thread(target=record_chunk, args=(p, stream, chunk_queue))
    recording_thread.daemon = True
    recording_thread.start()

    accumulated_transcription = ""
    print('transcription loop has started')

    while True:
        if not chunk_queue.empty():
            chunk_data = chunk_queue.get()
            transcription_thread = threading.Thread(target=transcribe_chunk, args=(model, chunk_data, p, transcription_queue))
            transcription_thread.daemon = True
            transcription_thread.start()

        if not transcription_queue.empty():
            transcription = transcription_queue.get()
            if transcription is not None and transcription != " TV GELDERLAND 2020" and transcription != " TV GELDERLAND 2021" and transcription != " TV GELDERLAND 2021." and transcription != " TV Gelderland 2021" and transcription != " TV Gelderland 2021." and transcription != " Bedankt voor het kijken!" and transcription != " Bedankt voor het kijken" and transcription != " Bedankt voor het kijken.":
                print(transcription)

        time.sleep(0.1)

if __name__ == "__main__":
    main()
