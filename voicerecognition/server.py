from flask import Flask
from voicerecognition.recorder import start
from speechtotext import get_text_from_speech

# This module is expected to do stuff on server via Flask I dunno
# It does nothing now

app = Flask(__name__)


def main():
    app.run()


if __name__ == "__main__":
    main()
