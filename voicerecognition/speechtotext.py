"""
This module provides a function to recognize speech from a .wav file and return a string
containing the recognized text.

The function opens the .wav file, reads it frame by frame, feeds the frames to a Vosk
speech recognition model, which tries to recognize the speech in the frames and
returns a JSON object containing the recognized text.

The function then takes this JSON object, extracts the recognized text from it and adds
it to a result string. If the recognized text is not empty, it also resets a flag
indicating that there was no recognized text in the previous frame.

If there is no recognized text in a frame, the function checks if there was recognized
text in the previous frame. If there was, it adds a newline character to the result
string and sets the flag to True. This is done to avoid adding unnecessary newline
characters to the result string.

After all frames have been processed, the function closes the .wav file and extracts
the final result from the speech recognition model. This final result is also added
to the result string.

Finally, the function returns the result string.
"""

import json
import wave

from vosk import Model, KaldiRecognizer

model = Model(r"./voicerecognition/vosk-model-small-ru-0.22")
recognizer = KaldiRecognizer(model, 16000)


def get_text_from_speech(path):
    result = ""
    wav = wave.open(path, "rb")
    if wav is not None:
        last_n = False

        while True:
            data = wav.readframes(16000)
            if len(data) == 0:
                break

            if recognizer.AcceptWaveform(data):
                res = json.loads(recognizer.Result())

                if res["text"] != "":
                    result += f" {res['text']}"
                    last_n = False
                elif not last_n:
                    result += "\n"
                    last_n = True

        wav.close()

        recognized = json.loads(recognizer.FinalResult())
        result += f" {recognized['text']}"

    return result


if __name__ == "__main__":
    pass
