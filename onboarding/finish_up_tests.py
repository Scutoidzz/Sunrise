from asyncio import open_unix_connection
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

    write_to_config()
def write_to_config():
    with open_unix_connection("../config.json, "w") as configfile:
        print(configfile)

verify_files() 