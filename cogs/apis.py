import sys
import openai
from pathlib import Path
import time


# function to load API key from file
def load_api_key():
    global _key

    _keypath = Path("api-key.txt")
    _keypath.touch(exist_ok=True)

    print("     Loading API key...")

    with open("api-key.txt", "r") as h:
        _key = h.readline().strip("\n")
    if not _key:
        print(
            "No API key found, or an invalid one was detected. Set a valid key in api-key.txt"
        )
        sys.exit()
    else:
        print("     API key loaded successfully!")

    openai.api_key = _key

    # loading API key and models in the background
    time_start = time.time()
    time_end = time.time() - time_start
    print(f"Loaded in {time_end} seconds")

    return _key


def load_models():
    models = openai.Model.list()

    # exclude useless models
    exclude = [
        "instruct",
        "similarity",
        "if",
        "query",
        "document",
        "insert",
        "search",
        "edit",
        "dall-e",
        "tts",
    ]

    print("     loading engines...")

    model_list = [
        str(model.id)
        for model in models.data
        if not any(y in str(model.id) for y in exclude)
    ]

    print("     engines loaded successfully")

    # loading API key and models in the background
    time_start = time.time()
    time_end = time.time() - time_start
    print(f"Loaded in {time_end} seconds")

    return model_list
