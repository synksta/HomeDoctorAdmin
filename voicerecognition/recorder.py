"""
This module is responsible for recording audio from a microphone and saving it as a temporary .wav file.
The file is then deleted once the recording is stopped.
"""

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


def start() -> None:
    """
    Starts recording audio from a microphone.

    This function initializes a PyAudio object, sets the sample width
    of the recording format (based on the current PyAudio object),
    opens an audio stream using the current settings, and starts a
    separate thread for recording the audio.
    """
    print("start!")

    # Initialize PyAudio object
    global audio
    audio = pyaudio.PyAudio()

    # Set sample width of recording format based on current PyAudio object
    global settings
    settings["sample_width"] = audio.get_sample_size(settings["format"])

    # Open audio stream using current settings
    global stream
    stream = audio.open(
        format=settings["format"],
        channels=settings["channels"],
        rate=settings["rate"],
        input=True,
        frames_per_buffer=settings["frames_per_buffer"],
    )

    # Start separate thread for recording audio
    global record_thread
    record_thread = threading.Thread(target=record, name="trd-record")
    record_thread.start()


def record() -> None:
    """
    Records audio from a microphone in a separate thread.

    This function is run in a separate thread and is responsible for recording audio from the microphone.
    It uses the global "recording" flag to determine when to stop recording. The recorded audio is stored in the
    global "chunks" list as a series of bytes objects, where each bytes object represents a single frame of audio.
    """
    global recording
    recording = True

    global chunks
    chunks = []

    # Read audio frames from the microphone and store them in the chunks list
    while recording:
        # Read the next frame of audio from the microphone
        data = stream.read(settings["frames_per_buffer"])
        # Append the read frame to the chunks list
        chunks.append(data)


def stop_and_get_path() -> str:
    """
    Stops recording audio from a microphone and returns the path to the temporary .wav file.

    This function is responsible for:
    1. Stopping the recording thread.
    2. Stopping the audio stream and closing the audio interface.
    3. Checking if there is enough space in the temporary directory.
    4. If there is not enough space, remove the oldest files until there is enough space.
    5. Create a new file with a unique name based on current date and time.
    6. Save the recorded audio to the new file.
    7. Return the path to the new file.

    The temporary directory is specified in the settings dictionary and is default to "temp/".
    The maximum size of the temporary directory is specified in the settings dictionary and is default to 500MB.
    """
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
            # Get a list of files in the temporary directory, sorted by date
            files_list = utils.get_sorted_list_of_files_by_date(path)
            removed = ""
            while settings["max_temp_dir_size"] < temp_dir_size and len(files_list) > 0:
                # Remove the oldest file until there is enough space
                removed += f"{files_list[0]} "
                temp_dir_size -= os.path.getsize(files_list[0])
                os.remove(files_list[0])
                files_list.pop(0)
            print(f"Removed {removed} to free space")
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
