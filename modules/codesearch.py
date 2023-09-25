import pandas as pd
import pyperclip
import pyautogui as gui
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

def sorter(data):
    rdf = pd.DataFrame()
    upv = []
    ans = []
    for i in range(len(data)):
        upv.append(data[i]["upvotes"])
        ans.append(data[i]["answer"])
    rdf["upvotes"] = upv
    rdf["answer"] = ans
    rdf.sort_values(by=["upvotes"], inplace = True, ascending=False, ignore_index=True)
    rdf.drop(rdf.columns[0], axis=1, inplace=True)
    return rdf

def altparser(data):
    altdf = pd.DataFrame()
    score = []
    term = []
    for i in range(len(data)):
        score.append(data[i]["score"])
        term.append(data[i]["term"])
    altdf["score"] = score
    altdf["term"] = term
    altdf.sort_values(by=["score"], inplace = True, ascending=False, ignore_index=True)
    return altdf


def qsearch(rdata):
    rdf = sorter(rdata)
    code = rdf.at[0, 'answer']
    pyperclip.copy(code)
    gui.click()
    gui.hotkey('ctrl', 'v')
    rdf = pd.DataFrame(None)
    notification("copied code to clipboard")

        
def gsearch(altdf):
    search = parser.quote(altdf["term"][0])
    notification("I couldn't find any code,so googling")
    webbrowser.open(google_qurl+search)
    for i in range(int(len(altdf["term"])/5)):
        webbrowser.open(google_qurl+parser.quote(altdf["term"][i]))

        

def codesearch(term):
    term = term.replace("search", "")
    search = parser.quote(term)
    titleurl = codegrepper_title_url+search+codegrepper_title_q
    alturl = codegrepper_alt_term_url+search
    rdata = requests.get(titleurl, verify=False).json()
    rdata = rdata["answers"]
    
    if len(rdata) == 0:
        notification("i couldn't find the'code, trying again")
        altdata = requests.get(alturl, verify=False).json()
        altdata = altdata["related_terms"]
        altdf = altparser(altdata)    
        search = parser.quote(altdf["term"][0])
        titleurl = codegrepper_title_url+search+codegrepper_title_q
        rdata = requests.get(titleurl, verify=False).json()
        rdata = rdata["answers"]
        
        if len(rdata) == 0:
            gsearch(altdf)
        
        else:
            qsearch(rdata)        
    
    else:
        qsearch(rdata)

