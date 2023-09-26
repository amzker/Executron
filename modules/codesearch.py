import pandas as pd
import pyperclip
import webbrowser
from .notification import notification 
import requests
import urllib.parse as parser
from urllib.request import urlopen
import configparser
config = configparser.ConfigParser()
config.read("config.paper")


codegrepper_title_url = config.get("Default","codegrepper_title_url")
codegrepper_title_q = config.get("Default","codegrepper_title_q")
codegrepper_alt_term_url = config.get("Default","codegrepper_alt_term_url")
google_qurl = config.get("Default","google_qurl")


def sort_answers(data):
    df = pd.DataFrame(data)
    df.sort_values(by="upvotes", ascending=False, inplace=True, ignore_index=True)
    return df["answer"].iloc[0]

def sort_alternative_terms(data):
    df = pd.DataFrame(data)
    df.sort_values(by="score", ascending=False, inplace=True, ignore_index=True)
    return df["term"].iloc[0]

def copy_to_clipboard(code):
    pyperclip.copy(code)
    notification("Code copied to clipboard")

def search_google(term):
    search = parser.quote(term)
    webbrowser.open(google_qurl + search)
    notification("Couldn't find any code, so searching on Google")

def codesearch(term):
    term = term.replace("search", "")
    search = parser.quote(term)
    title_url = codegrepper_title_url + search + codegrepper_title_q
    alt_url = codegrepper_alt_term_url + search

    title_response = requests.get(title_url, verify=False)
    title_data = title_response.json().get("answers", [])

    if not title_data:
        notification("Couldn't find any code, trying alternative terms")
        alt_response = requests.get(alt_url, verify=False)
        alt_data = alt_response.json().get("related_terms", [])

        if alt_data:
            alt_term = sort_alternative_terms(alt_data)
            title_url = codegrepper_title_url + parser.quote(alt_term) + codegrepper_title_q
            title_response = requests.get(title_url, verify=False)
            title_data = title_response.json().get("answers", [])

            if not title_data:
                search_google(alt_data)
            else:
                code = sort_answers(title_data)
                copy_to_clipboard(code)
        else:
            search_google(term)
    else:
        code = sort_answers(title_data)
        copy_to_clipboard(code)
