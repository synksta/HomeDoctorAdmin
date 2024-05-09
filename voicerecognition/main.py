from vosk import Model, KaldiRecognizer
from flask import Flask, render_template, request, flash, redirect, url_for
import sys
import json
import os
import librosa
import soundfile as sf
from librosa import core

# объясняется ниже
from werkzeug.utils import secure_filename
import time
import wave
from parser_1 import parseHomeDoc

model = Model(r"vosk-model-small-ru-0.22")


def correct(filepath):
    x, _ = librosa.load(filepath, sr=16000)
    os.remove(filepath)
    sf.write(filepath, x, 16000)


def recognition(filepath):
    wf = wave.open(filepath, "rb")
    rec = KaldiRecognizer(model, 16000)

    result = ""
    last_n = False

    while True:
        data = wf.readframes(16000)
        if len(data) == 0:
            break

        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())

            if res["text"] != "":
                result += f" {res['text']}"
                last_n = False
            elif not last_n:
                result += "\n"
                last_n = True

    res = json.loads(rec.FinalResult())
    result += f" {res['text']}"

    return result


# импортируем Flask

# создаем экземпляр приложения
app = Flask(__name__)


# определяем функцию для обработки запросов к корневому URL
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/microphone", methods=["GET"])
def micro():
    return render_template("microphone.html")


@app.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    # Получаем файл .wav из запроса
    audio_file = request.files["audio"]

    # Сохраняем файл на сервере
    save_path = "./tmp"
    file_name = audio_file.filename
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    audio_file.save(os.path.join(save_path, audio_file.filename))

    # Исправление формата файла
    correct(save_path + "/" + file_name)

    # Распознаем речь и получаем текст
    recognized_text = recognition(save_path + "/" + file_name)

    print(recognized_text)

    # Удаляем временный файл
    os.remove(save_path + "/" + file_name)

    print(parseHomeDoc(recognized_text))

    # Создаем словарь с данными
    data = parseHomeDoc(recognized_text)

    # Преобразуем словарь в JSON
    # json_data = json.dumps(data, ensure_ascii=False)

    # Возвращаем JSON-ответ
    return data


# запускаем приложение
if __name__ == "__main__":
    app.run()
