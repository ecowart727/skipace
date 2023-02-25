import pandas as pd
import requests
import streamlit as st

url = 'https://www.pdga.com/tour/event/65206'

header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}

r = requests.get(url, headers=header)

MPO = pd.read_html(r.text)[1]
FPO = pd.read_html(r.text)[2]

FPO = FPO[['Name', 'Place', 'Total']]
MPO = MPO[['Name', 'Place', 'Total']]

import requests

cookies = {
    '_ga': 'GA1.1.712981455.1677266981',
    'skipace_fantasy_disc_golf_session': 'tOFUyov33VyT8TwJZZUBhgEConE0YkBxhOBow9Uu',
    'XSRF-TOKEN': 'eyJpdiI6InVoTnhLcHU2YW5HVWxFU084aUtZbHc9PSIsInZhbHVlIjoiY3FIOEE5OVN4Qnd4ZE9tKzc0aVFxdXB6TkZqbHczRHpmeVNhN1MvVkhpRjFOYUwzR0ljSFVjMWplZWNjR1RzaGlJL0VpOUpENG9weEhUeWFTT21jM2k3S3hnNGgzdXYwa2x6VUxHRkhOZTlHd1VEeHEzZ3pwQ2hiWGx0Y0ZxNTAiLCJtYWMiOiIzMmNkMTY1NWFmN2ZkYzBkMWFhMDQ3ODlkMDY3ZWU5OWZiYjc5OTI1NjBjNzAxNzNhZDZjNWJlZDdlMzQ1MzRhIiwidGFnIjoiIn0%3D',
    '_ga_8N3LRJXS8Q': 'GS1.1.1677276635.2.0.1677276635.0.0.0',
}

headers = {
    'authority': 'skipace.com',
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    # 'cookie': '_ga=GA1.1.712981455.1677266981; skipace_fantasy_disc_golf_session=tOFUyov33VyT8TwJZZUBhgEConE0YkBxhOBow9Uu; XSRF-TOKEN=eyJpdiI6InVoTnhLcHU2YW5HVWxFU084aUtZbHc9PSIsInZhbHVlIjoiY3FIOEE5OVN4Qnd4ZE9tKzc0aVFxdXB6TkZqbHczRHpmeVNhN1MvVkhpRjFOYUwzR0ljSFVjMWplZWNjR1RzaGlJL0VpOUpENG9weEhUeWFTT21jM2k3S3hnNGgzdXYwa2x6VUxHRkhOZTlHd1VEeHEzZ3pwQ2hiWGx0Y0ZxNTAiLCJtYWMiOiIzMmNkMTY1NWFmN2ZkYzBkMWFhMDQ3ODlkMDY3ZWU5OWZiYjc5OTI1NjBjNzAxNzNhZDZjNWJlZDdlMzQ1MzRhIiwidGFnIjoiIn0%3D; _ga_8N3LRJXS8Q=GS1.1.1677276635.2.0.1677276635.0.0.0',
    'referer': 'https://skipace.com/draft-leagues/657/rosters',
    'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
}

r = requests.get('https://skipace.com/api/v1/draft-leagues/657/roster-summary', cookies=cookies, headers=headers)
data = r.json()

rosters = pd.json_normalize(data.get('data').get('rosters'))
users = pd.json_normalize(data.get('data').get('users'))
players = pd.json_normalize(data.get('data').get('players'))

rosterDict = {}

for i in range(len(users)):
    user = users['public_name'][i]
    userID = users['id'][i]
    playerList = []
    
    temp = rosters[rosters['user_id'] == userID]
    
    for player in temp['player_id']:
        first = (players[players['id'] == player]['first_name'].iloc[0])
        last = (players[players['id'] == player]['last_name'].iloc[0])
        name = first + ' ' + last
    
        if rosters[rosters['player_id'] == player]['is_starting'].iloc[0]:
            if rosters[rosters['player_id'] == player]['division_code'].iloc[0] == 'FPO':
                playerList.append(name)
            else:
                playerList.insert(0, name)
                
    rosterDict[user] = playerList
                
standings = pd.DataFrame(columns = ['MPO1', 'MPO2', 'MPO3', 'MPO4', 'FPO1', 'FPO2'], index = rosterDict.keys())

for owner in rosterDict.keys():
    team = rosterDict.get(owner)
    for i in range(6):
        if i < 4:
            try:
                score = MPO[MPO['Name'] == team[i]]['Place'].iloc[0]
                standings['MPO' + str(i + 1)][owner] = score
            except IndexError:
                standings['MPO' + str(i + 1)][owner] = len(MPO)
        else:
            try:
                score = FPO[FPO['Name'] == team[i]]['Place'].iloc[0]
                standings['FPO' + str(i - 3)][owner] = score
            except IndexError:
                standings['FPO' + str(i - 3)][owner] = len(FPO)
            
standings['Total'] = standings['MPO1'] + standings['MPO2'] + standings['MPO3'] + standings['MPO4'] + standings['FPO1'] + standings['FPO2']
ordered = standings.sort_values(by = 'Total')
st.dataframe(data = ordered)
