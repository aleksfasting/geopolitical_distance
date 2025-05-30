import pandas as pd
import subprocess as sb
import requests
import sys

data = pd.read_csv('resolutions.csv')

startyear = 2023
if len(sys.argv) > 1:
    startyear = int(sys.argv[1])

data = data.transpose()
for y in range(2023, startyear, -1):
    data = data.drop(str(y))

print("Scraping resolutions for years" + str(list(data.index)))

data = data.to_numpy()

BASE_SEARCH = "https://digitallibrary.un.org/search?"

for year in data:
    r = requests.get(BASE_SEARCH)
    if r.status_code == 202:
        print("Status code 202 on year: " + str(year))
        break
    for res in year:
        if str(res) == 'nan':
            continue
        print("Scraping record: " + res)
        sb.run(['python', 'scraper.py', res], shell=True)