import os
import sys
import json


def verify_files():
    path_to_voice = os.path.join("..", "voice")
    path_to_embedding = os.path.join("..", "starry")
    path_to_config_json = os.path.join("config.json")



    if os.path.isdir(path_to_voice) == True:
        print("os returned true to voice")
    elif os.path.isdir(path_to_voice) == False:
        print("os returned false")
    else:
        print("os reported something incorrectly")

    
    if os.path.isdir(path_to_embedding) == True:
        print("os returned true to voice")
    elif os.path.isdir(path_to_embedding) == False:
        print("os returned false")
    else:
        print("os reported something incorrectly")

def write_to-

verify_files()  