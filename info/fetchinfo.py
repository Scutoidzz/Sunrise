import os
import sys
import random
import requests
import json
import urllib
import logging
import subprocess


def init_fetch():
    timeout = 7
    logging.info("Fetch is being initialized.")
    output = urllib.request.urlopen("http://clients3.google.com/generate_204", timeout=timeout)
    if output.getcode() == 204:
        logging.info("Fetch completed successfully.")
        print("Internet connected sucesssfully")
        return True
    else:
        logging.info("no internet")
        print("No internet connection")
        return False


def fetch_weather(zipcode):
    logging.info("Attempting to connect to weather")
    amount_of_retries = 0
    # TODO: Find free weather API

    

