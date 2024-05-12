import json


# Parses nuber words to the actual number
def text_to_number(textnum, numwords={}):
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

    result += current

    return result


# Returns json formatted string with 'symptom' entity attributes
def get_symptom_data(text):

    print(text)

    result = ""

    # Trigger phrases
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
        "yes",
        "no",
        "page",
        "description",
        "keywords",
        "end",
    ]

    current_dict = []
    dict_idx = []

    for i in range(len(phrases)):
        if phrases[i] in text:
            current_dict.append(phrases[i])
            dict_idx.append(text.index(phrases[i]))

    if 0 not in (len(current_dict), len(dict_idx)):
        parsed = {}

        dict_idx, current_dict = zip(
            *[(b, a) for b, a in sorted(zip(dict_idx, current_dict))]
        )

        # Проход по списку фраз
        for i, phrase in enumerate(phrases):
            if phrase in text:
                if phrase != "закончить":
                    # Если фраза найдена, добавляем ее в результат
                    start = phrase
                    end = current_dict[current_dict.index(phrase) + 1]
                    start_idx = text.index(start)
                    end_idx = text.index(end)
                    if phrase == "страница":
                        parsed[phrasesTrans[i]] = str(
                            text_to_number(
                                text[start_idx + len(start) : end_idx].strip()
                            )
                        )
                    else:
                        parsed[phrasesTrans[i]] = text[
                            start_idx + len(start) : end_idx
                        ].strip()
                    # print(result[phrase])

            else:
                # Если фразы нет, добавляем пустое значение
                parsed[phrasesTrans[i]] = ""

        result = json.dumps(parsed, ensure_ascii=False)

    return result


# Example
# input_string = "симптом идет кровь из носа да симптом кровь пульсирует ключевые слова кровь нос течение нет симптом остановить кровотечение описание идет темная кровь закончить"
# output_json = symptom_form_data(input_string)
# print(output_json)
