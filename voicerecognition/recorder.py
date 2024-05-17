import os
import threading
import time
import pyaudio
import wave
from utilities import utils
from datetime import datetime

root_dir = "./voicerecognition/"
settings_file_name = "recorder_settings.json"

if not os.path.exists(root_dir):
    os.makedirs(root_dir)

audio = pyaudio.PyAudio()

settings = {
    "format": pyaudio.paInt16,
    "channels": 1,
    "rate": 16000,
    "frames_per_buffer": 1024,
    "sample_width": audio.get_sample_size(pyaudio.paInt16),
    # Temporary files directory size in bytes
    "max_temp_dir_size": 3000000,
}

settings = utils.sync_dict_with_json(settings, settings_file_name, root_dir)

print(settings)

# Audio stream
stream: pyaudio.Stream
# List of audio stream chunks
chunks: list

# Flag for recording
recording: bool
# Separate thread for recording on the background
record_thread: threading.Thread


def start():
    print("start!")

    global audio
    audio = pyaudio.PyAudio()

    global settings
    settings["sample_width"] = audio.get_sample_size(settings["format"])

    global stream
    stream = audio.open(
        format=settings["format"],
        channels=settings["channels"],
        rate=settings["rate"],
        input=True,
        frames_per_buffer=settings["frames_per_buffer"],
    )

    global record_thread
    record_thread = threading.Thread(target=record, name="trd-record")
    record_thread.start()


def record():
    global recording
    recording = True

    global chunks
    chunks = []
    while recording:
        data = stream.read(settings["frames_per_buffer"])
        chunks.append(data)


def stop_and_get_path():
    time.sleep(0.5)

    global recording
    recording = False

    record_thread.join()

    stream.stop_stream()
    stream.close()

    audio.terminate()

    # Temp .wav file with speech
    # Making sure there is a such directory
    path = f"{root_dir}temp/"
    if os.path.exists(path):
        # If it is, we must check for enough space
        temp_dir_size = utils.get_dir_size(path)
        # And free it if needed
        if settings["max_temp_dir_size"] < temp_dir_size:
            files_list = utils.get_sorted_list_of_files_by_date(path)
            removed = ""
            while settings["max_temp_dir_size"] < temp_dir_size and len(files_list) > 0:
                print(f"{files_list[0]}")
                temp_dir_size -= os.path.getsize(files_list[0])
                os.remove(files_list[0])
                files_list.pop(0)
    else:
        # Create the directory for temporary files
        os.makedirs(path)

    timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
    path += f"{timestamp}.wav"

    save = wave.open(path, "wb")
    save.setnchannels(settings["channels"])
    save.setsampwidth(settings["sample_width"])
    save.setframerate(settings["rate"])
    save.writeframes(b"".join(chunks))
    save.close()

    return path
