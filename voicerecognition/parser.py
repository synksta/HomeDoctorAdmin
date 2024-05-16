import json

from utilities import utils


# Parses digit words to the actual digits
digits = [
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
]


key_by_val = lambda dict, val: [key for key in dict if dict[key] == val][0]


# Returns json formatted string with 'symptom' entity attributes
def get_symptom_data(text):

    root_dir = "./voicerecognition/"
    trigger_phrases_file_name = "symptom_attributes_trigger_phrases.json"

    result = ""
    result_dictionary = {}

    marker = "@"

    # Attributes and their trigger phrases
    trigger_phrases = {
        "name": "название",
        "description": "описание",
        "page": "страница",
        "yes": "дассылка",
        "no": "нетссылка",
        "keywords": "ключевыеслова",
    }

    trigger_phrases = utils.sync_dict_with_json(
        trigger_phrases, trigger_phrases_file_name, root_dir
    )

    for key, phrase in trigger_phrases.items():
        trigger_phrases[key] = phrase.lower().replace(" ", "")

    text_word_list = text.split()

    print(text_word_list)

    found_trigger_phrases = []
    potential_trigger_phrase_words = []
    for word in text_word_list:
        potential_trigger_phrase = "".join(potential_trigger_phrase_words)
        if any(
            ((potential_trigger_phrase + word) in phrase and word in phrase)
            for phrase in trigger_phrases.values()
        ):
            potential_trigger_phrase_words.append(word)
        else:
            if (
                potential_trigger_phrase in list(trigger_phrases.values())
                and potential_trigger_phrase_words not in found_trigger_phrases
            ):
                found_trigger_phrases.append(list(potential_trigger_phrase_words))
            potential_trigger_phrase_words.clear()

    for phrase_words in found_trigger_phrases:
        phrase = "".join(phrase_words)
        phrase_index = text_word_list.index(phrase_words[0])
        # Odd move here - paste the marker '@' to define attribute as ready for fill
        text_word_list[phrase_index] = f"{marker}{phrase}"
        for i in range(1, len(phrase_words)):
            text_word_list[phrase_index + i] = ""

    for key, phrase in trigger_phrases.items():
        trigger_phrases[key] = f"{marker}{phrase}"

    print(text_word_list)
    text_word_list = list(filter(lambda word: len(word) > 0, text_word_list))
    print(text_word_list)

    # fix this bullshit - similar words are disappeating in the loop below!!!
    current_attribute = ""
    for word in text_word_list:
        if word in trigger_phrases.values():
            # Clean the phrase to ignore its atribute it in future iterations
            current_attribute = key_by_val(trigger_phrases, word)
            trigger_phrases[current_attribute] = ""
        elif len(current_attribute) > 0:
            # Add all the other words
            if current_attribute == "page" and word in digits:
                trigger_phrases[current_attribute] += f"{str(digits.index(word))}"
            elif current_attribute == "keywords":
                separator = ", "
                trigger_phrases[current_attribute] = (
                    trigger_phrases[current_attribute] + f"{separator}{word}"
                ).removeprefix(separator)
            else:
                separator = " "
                trigger_phrases[current_attribute] = (
                    trigger_phrases[current_attribute] + f"{separator}{word}"
                ).removeprefix(separator)

    for key, phrase in trigger_phrases.items():
        trigger_phrases[key] = (
            "" if marker in trigger_phrases[key] else trigger_phrases[key]
        )

    print(trigger_phrases)


# Example

if __name__ == "__main__":
    input_string = "еброчка описание бебра название эээ kjhkjh kj страница два да ссылка прикол нет ссылка нет да ссылка приколk ключевые    слова hjk hbh jkj"
    output_json = get_symptom_data(input_string)
    print(output_json)
    # input_string = "двадцать слово пять пять"
    # print(text_to_number(input_string))
