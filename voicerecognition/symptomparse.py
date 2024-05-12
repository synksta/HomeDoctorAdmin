import os
from flask import Flask, render_template, request


# def speech_to_text(audio_file):
#     # Получаем файл .wav из запроса
#     audio_file = request.files["audio"]

#     # Сохраняем файл на сервере
#     save_path = "./tmp"
#     file_name = audio_file.filename
#     if not os.path.exists(save_path):
#         os.makedirs(save_path)
#     audio_file.save(os.path.join(save_path, audio_file.filename))

#     # Исправление формата файла
#     correct(save_path + "/" + file_name)

#     # Распознаем речь и получаем текст
#     recognized_text = recognition(save_path + "/" + file_name)

#     # print(recognized_text)

#     # Удаляем временный файл
#     os.remove(save_path + "/" + file_name)

#     print(parseHomeDoc(recognized_text))

#     # Создаем словарь с данными
#     data = parseHomeDoc(recognized_text)

#     # Преобразуем словарь в JSON
#     # json_data = json.dumps(data, ensure_ascii=False)

#     # Возвращаем JSON-ответ
#     return data
