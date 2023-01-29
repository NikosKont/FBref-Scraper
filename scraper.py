
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re

statsList = ['stats', 'keepers', 'keepersadv', 'shooting', 'passing', 'passing_types', 'gca', 'defense', 'possession', 'playingtime', 'misc']

def getPlayerStats(stat: str, compid: int):
    if stat not in statsList:
        raise ValueError(f"stat must be one of {statsList}")

    table = _getRawTable(stat, compid)
    return _getDataframe(table)


def _getRawTable(stat: str, compid: int):
    url = f"https://fbref.com/en/comps/{compid}/{stat}/"
    print(f"Getting data from {url}")
    res = requests.get(url)
    comm = re.compile("<!--|-->")
    soup = bs(comm.sub("", res.text), 'lxml')

    return soup.find("div", {"id": f"div_stats_{stat}"})


def _getDataframe(table):
    df = pd.read_html(str(table))
    df = df[0]

    # delete the first and last column (Rk, Match)
    df = df.iloc[:, 1:-1]

    # keep only the second value for the headers
    df.columns = [h[1] for h in df.columns]

    # only keep the part after space for 'Nation'
    df['Nation'] = df['Nation'].apply(lambda x: str(x).rsplit(' ', maxsplit=1)[-1])

    # delete rows with the column names
    df = df[df[df.columns[0]] != df.columns[0]]
    df.reset_index(drop=True, inplace=True)

    for col in df.columns:
        try:
            df[col] = df[col].astype(float)
            if df[col].apply(lambda x: x.is_integer()).all():
                df[col] = df[col].astype(int)
        except ValueError:
            pass

    return df