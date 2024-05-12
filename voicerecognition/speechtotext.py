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

        wav.close

        recognized = json.loads(recognizer.FinalResult())
        result += f" {recognized['text']}"
    return result


if __name__ == "__main__":
    print(get_text_from_speech(path="./temp/11052024182533.wav"))
