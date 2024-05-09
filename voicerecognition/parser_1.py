import json


def text2int(textnum, numwords={}):
    if not numwords:
        units = [
            "ноль",
            "один",
            "два",
            "три",
            "четыре",
            "пять",
            "шесть",
            "семь",
            "восемь",
            "девять",
            "десять",
            "одиннадцать",
            "двенадцать",
            "тринадцать",
            "четырнадцать",
            "пятнадцать",
            "шестнадцать",
            "семнадцать",
            "восемнадцать",
            "девятнадцать",
        ]

        tens = [
            "",
            "",
            "двадцать",
            "тридцать",
            "сорок",
            "пятьдесят",
            "шестьдесят",
            "семьдесят",
            "восемьдесят",
            "девяносто",
        ]

        scales = ["сто", "тысяч", "миллион", "миллиард", "триллион"]

        numwords["и"] = (1, 0)
        for idx, word in enumerate(units):
            numwords[word] = (1, idx)
        for idx, word in enumerate(tens):
            numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):
            numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
            raise Exception("Неверное слово: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current


def parseHomeDoc(input_string):
    # Разделяющие фразы
    phrases = [
        "симптом",
        "диагноз",
        "да ссылка",
        "нет ссылка",
        "страница",
        "описание",
        "ключевые слова",
        "закончить",
    ]

    phrasesTrans = [
        "symptom",
        "diagnoz",
        "Ysymptom",
        "Nsymptom",
        "page",
        "descript",
        "keyword",
        "end",
    ]
    current_dict = []
    dict_idx = []

    # Инициализация словаря для хранения результатов
    result = {}

    for i in range(len(phrases)):
        if phrases[i] in input_string:
            current_dict.append(phrases[i])
            dict_idx.append(input_string.index(phrases[i]))

    dict_idx, current_dict = zip(
        *[(b, a) for b, a in sorted(zip(dict_idx, current_dict))]
    )

    # Проход по списку фраз
    for i, phrase in enumerate(phrases):
        if phrase in input_string:
            if phrase != "закончить":
                # Если фраза найдена, добавляем ее в результат
                start = phrase
                end = current_dict[current_dict.index(phrase) + 1]
                start_idx = input_string.index(start)
                end_idx = input_string.index(end)
                if phrase == "страница":
                    result[phrasesTrans[i]] = str(
                        text2int(input_string[start_idx + len(start) : end_idx].strip())
                    )
                else:
                    result[phrasesTrans[i]] = input_string[
                        start_idx + len(start) : end_idx
                    ].strip()
                # print(result[phrase])

        else:
            # Если фразы нет, добавляем пустое значение
            result[phrasesTrans[i]] = ""

    # Преобразование в JSON
    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


# Пример входной строки
input_string = "симптом идет кровь из носа да симптом кровь пульсирует ключевые слова кровь нос течение нет симптом остановить кровотечение описание идет темная кровь закончить"

# Вызов функции
output_json = parseHomeDoc(input_string)
# print(output_json)
