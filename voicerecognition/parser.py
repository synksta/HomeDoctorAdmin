from utilities import utils

# List of Russian digits words for voice recognition
# This list is used to detect numbers in speech recognition results
# and convert them to integers
digits = [
    "ноль",  # zero
    "один",  # one
    "два",  # two
    "три",  # three
    "четыре",  # four
    "пять",  # five
    "шесть",  # six
    "семь",  # seven
    "восемь",  # eight
    "девять",  # nine
]

# A marker used to define attribute as ready for fill
marker = "@"

# This line is a lambda function that takes a dictionary and a value as arguments and returns the key of the dictionary that corresponds to the given value.
# It does this by creating a list of keys whose values are equal to the given value and then returning the first element of that list.
# The list comprehension [key for key in dict if dict[key] == val] creates the list of keys, and [0] at the end of the line returns the first element of that list.
key_by_val = lambda dict, val: [key for key in dict if dict[key] == val][0]


# Returns json formatted string with 'symptom' entity attributes
def parse_symptom_data(text):
    """
    A function that processes text input to extract specific attributes based on trigger phrases.

    Args:
        text (str): The input text to be processed.

    Returns:
        dict: A dictionary containing the extracted attributes and their corresponding values.
    """

    root_dir = "./voicerecognition/"
    trigger_phrases_file_name = "symptom_attributes_trigger_phrases.json"

    # Attributes and their trigger phrases
    trigger_phrases = {
        "name": "название",
        "description": "описание",
        "page": "страница",
        "yes_name": "ссылкада",
        "no_name": "ссылканет",
        "keywords": "ключевыеслова",
    }

    # Synchronize the trigger phrases dictionary with the JSON file
    trigger_phrases = utils.sync_dict_with_json(
        trigger_phrases, trigger_phrases_file_name, root_dir
    )

    # Normalize the trigger phrases to ignore case and spaces
    trigger_phrases = {
        key: phrase.lower().replace(" ", "") for key, phrase in trigger_phrases.items()
    }
    # Split the input text into words
    text_word_list = text.split()

    print(text_word_list)

    # Initialize lists to store the found trigger phrases and their corresponding words
    found_trigger_phrases = []
    potential_trigger_phrase_words = []

    # Iterate over the text words
    for word in text_word_list:
        # Construct the potential trigger phrase by joining the current word with the previously found words
        potential_trigger_phrase = "".join(potential_trigger_phrase_words)
        # Check if the potential trigger phrase is a valid trigger phrase
        if any(
            ((potential_trigger_phrase + word) in phrase and word in phrase)
            for phrase in trigger_phrases.values()
        ):
            # If it is, append the current word to the potential trigger phrase words
            potential_trigger_phrase_words.append(word)
        else:
            # If it is not, check if the potential trigger phrase is a valid trigger phrase
            if (
                potential_trigger_phrase in list(trigger_phrases.values())
                and potential_trigger_phrase_words not in found_trigger_phrases
            ):
                # If it is, append the potential trigger phrase words to the found trigger phrases
                found_trigger_phrases.append(list(potential_trigger_phrase_words))
            # Clear the potential trigger phrase words
            potential_trigger_phrase_words.clear()

    # Iterate over the found trigger phrases and their words
    for phrase_words in found_trigger_phrases:
        # Construct the trigger phrase by joining the words
        phrase = "".join(phrase_words)
        # Find the index of the first word in the trigger phrase
        phrase_index = text_word_list.index(phrase_words[0])
        # Replace the first word with the marker to define the attribute as ready for fill
        text_word_list[phrase_index] = f"{marker}{phrase}"
        # Replace the remaining words with an empty string
        for i in range(1, len(phrase_words)):
            text_word_list[phrase_index + i] = ""

    # Iterate over the trigger phrases and their words
    for key, phrase in trigger_phrases.items():
        # Replace the trigger phrase with the marker to define the attribute as ready for fill
        trigger_phrases[key] = f"{marker}{phrase}"

    print(text_word_list)

    # Filter out the empty strings from the text word list
    text_word_list = list(filter(lambda word: len(word) > 0, text_word_list))
    print(text_word_list)
    return text_word_list, trigger_phrases


def convert_symptop_data_to_dict(text_word_list, trigger_phrases):
    # Initialize the current attribute
    current_attribute = ""
    # Iterate over the text words
    for word in text_word_list:
        # Check if the word is a trigger phrase
        if marker in word and word in trigger_phrases.values():
            # If it is, update the current attribute
            current_attribute = key_by_val(trigger_phrases, word)
            # Replace the trigger phrase with an empty string
            trigger_phrases[current_attribute] = ""
        elif len(current_attribute) > 0:
            # Add all the other words to the current attribute
            if current_attribute == "page":
                trigger_phrases[current_attribute] += (
                    f"{str(digits.index(word))}" if word in digits else ""
                )
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

    # Iterate over the trigger phrases and their words
    for key, phrase in trigger_phrases.items():
        # Replace the marker with an empty string
        trigger_phrases[key] = (
            "" if marker in trigger_phrases[key] else trigger_phrases[key]
        )

    print(trigger_phrases)
    return trigger_phrases


# Example

if __name__ == "__main__":
    input_string = "еброчка описание бебра название эээ kjhkjh kj страница два asdad два фывф три фывфыв да ссылка прикол нет ссылка нет да ссылка прикол ключевые    слова hjk hbh jkj"
    output_json = parse_symptom_data(input_string)
    print(output_json)
    # input_string = "двадцать слово пять пять"
    # print(text_to_number(input_string))
