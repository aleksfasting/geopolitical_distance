import requests
import sys
import pandas as pd
import os

BASE_SEARCH = "https://digitallibrary.un.org/search?"
BASE_RECORD = "https://digitallibrary.un.org/record/"

RECORD_PATH = "voting_record.csv"

def get_record_id(res_symbol: str) -> str:
    # build search URL: ln=en (English), output=json, q=<symbol>
    params = {
        "p": res_symbol,
        "cc": "Voting Data"
    }
    r = requests.get(BASE_SEARCH, params=params)
    r.raise_for_status()
    data = r.text
    hits = data.find("/record/")
    if hits == -1:
        print("No record found")
        print("Request", r)
        raise ValueError("No record found")
    record = data[hits+len('/record/'):].split('?')[0]
    return record

def fetch_voting_data(record_id: str) -> dict:
    # the record JSON endpoint
    url = f"{BASE_RECORD}{record_id}"
    params = {"ln": "en", "output": "json"}
    r = requests.get(url, params=params)
    r.raise_for_status()
    text = r.text
    vote_index = text.find("AFGHANISTAN") - 2
    end_vote_index = text[vote_index:].find("</span>")
    vote_text = text[vote_index: vote_index + end_vote_index]
    if vote_text[0] == ">":
        vote_text = '0' + vote_text[1:]
    vote_text = ' ' + vote_text

    vote_array = vote_text.split("<br/>")

    votes = {}
    for vote in vote_array:
        a = vote.split(' ')
        v = a[1]
        if v not in ['Y', 'N', 'A']:
            v = '0'
        votes[" ".join(a[2:])] = v

    return votes

def get_voting_record(res_symbol: str) -> dict:
    rec_id = get_record_id(res_symbol)
    print("Record ID: " + rec_id)
    votes = fetch_voting_data(rec_id)
    return votes

def write_record(voting: dict):
    newline = pd.DataFrame(voting.values()).transpose()
    newline.columns = list(voting.keys())
    if os.path.exists(RECORD_PATH):
        csv_content = pd.read_csv(RECORD_PATH)
        new_df = csv_content._append(newline)
        new_df.to_csv(RECORD_PATH, header=True, index=False)
    else:
        newline.to_csv(RECORD_PATH, header=True, index=False)
        
        

if __name__ == "__main__":
    try:
        symbol = sys.argv[1]
    except:
        symbol = "A/RES/78/20"
    try:
        voting = get_voting_record(symbol)
        print(f"Voting record for {symbol}:")
        for category, countries in voting.items():
            print(f"  {category.title():8s}: {', '.join(countries)}")
        write_record(voting)
    except Exception as e:
        print("Error:", e)
