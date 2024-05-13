import json

from utilities import utils


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

    root_dir = "./voicerecognition/"
    trigger_phrases_file_name = "symptom_attributes_trigger_phrases.json"

    print(text)

    result = ""
    result_dictionary = {}

    # Attributes and their trigger phrases
    trigger_phrases = {
        "name": "симптом",
        "description": "описание",
        "page": "страница",
        "yes": "да ссылка",
        "no": "нет ссылка",
        "keywords": "ключевые слова",
    }

    settings = utils.sync_dict_with_json(settings, trigger_phrases_file_name, root_dir)

    trigger_phrases_multiword = {
        key: val for key, val in trigger_phrases.items() if len(val.split()) > 1
    }

    combophrase_word = ""
    index = 0
    combophrase_indexes = []

    text_word_list = text.split()

    print(text_word_list)

    for word in text_word_list:
        if word in [
            trigger_phrases["yes"].split()[0],
            trigger_phrases["no"].split()[0],
            trigger_phrases["keywords"].split()[0],
        ]:
            combophrase_word = word
            index += 1
            continue
        if len(combophrase_word) > 0:
            if (
                combophrase_word
                in [
                    "да",
                    "нет",
                ]
                and word in ["ссылка"]
            ) or (combophrase_word == "ключевые" and word == "слова"):
                combophrase_indexes.append(index - 1)
            else:
                combophrase_word = ""
        index += 1

    for index in combophrase_indexes:
        text_word_list[index] += f" {text_word_list[index + 1]}"
        text_word_list[index + 1] = ""

    text_word_list = list(filter(lambda word: len(word) != 0, text_word_list))

    print(text_word_list)

    current_attribute = ""
    attribute_value_list = []
    attribute_value = ""
    for word in text_word_list:
        if word in trigger_phrases.values():
            # Clean the phrase to ignore its atribute it in future iterations
            if current_attribute != "" and current_attribute in trigger_phrases.keys():
                if current_attribute == "page":
                    # Remove all non number words from attribute_value_list then parse into a number
                    pass
                elif current_attribute == "keywords":
                    attribute_value = ",".join(attribute_value_list)
                else:
                    attribute_value = " ".join(attribute_value_list)
                # Comparing with this value obviously False
                trigger_phrases[current_attribute] = attribute_value
                attribute_value_list = []
                attribute_value = ""
            current_attribute = trigger_phrases.keys()[
                trigger_phrases.values().index(word)
            ]
        attribute_value_list.append(word)

        # if phrases["name"]
    # You need to split together two neighbors in the list somehow
    # phrases = [
    #     "симптом",
    #     "диагноз",
    #     "да ссылка",
    #     "нет ссылка",
    #     "страница",
    #     "описание",
    #     "ключевые слова",
    #     "закончить",
    # ]

    # phrasesTrans = [
    #     "symptom",
    #     "yes",
    #     "no",
    #     "page",
    #     "description",
    #     "keywords",
    #     "end",
    # ]

    # current_dict = []
    # dict_idx = []

    # for i in range(len(phrases)):
    #     if phrases[i] in text:
    #         current_dict.append(phrases[i])
    #         dict_idx.append(text.index(phrases[i]))

    # if 0 not in (len(current_dict), len(dict_idx)):
    #     parsed = {}

    #     dict_idx, current_dict = zip(
    #         *[(b, a) for b, a in sorted(zip(dict_idx, current_dict))]
    #     )

    #     # Проход по списку фраз
    #     for i, phrase in enumerate(phrases):
    #         if phrase in text:
    #             if phrase != "закончить":
    #                 # Если фраза найдена, добавляем ее в результат
    #                 start = phrase
    #                 end = current_dict[current_dict.index(phrase) + 1]
    #                 start_idx = text.index(start)
    #                 end_idx = text.index(end)
    #                 if phrase == "страница":
    #                     parsed[phrasesTrans[i]] = str(
    #                         text_to_number(
    #                             text[start_idx + len(start) : end_idx].strip()
    #                         )
    #                     )
    #                 else:
    #                     parsed[phrasesTrans[i]] = text[
    #                         start_idx + len(start) : end_idx
    #                     ].strip()
    #                 # print(result[phrase])

    #         else:
    #             # Если фразы нет, добавляем пустое значение
    #             parsed[phrasesTrans[i]] = ""

    #     result = json.dumps(parsed, ensure_ascii=False)

    # return result


# Example

if __name__ == "__main__":
    input_string = "симптом идет кровь из носа да ссылка нет ссылка нет да да ссылка ключевые слова ключевые да ссылка ключевые слова симптом кровь пульсирует ключевые слова кровь нос течение нет симптом остановить кровотечение описание идет темная кровь закончить да ссылка ключевые"
    output_json = get_symptom_data(input_string)
    print(output_json)
    # input_string = "двадцать слово пять пять"
    # print(text_to_number(input_string))
