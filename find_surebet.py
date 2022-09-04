import subprocess
import pandas as pd
import pickle
from fuzzywuzzy import process, fuzz
from sympy import symbols, Eq, solve

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

#scrape in parallel (at the same time)
#subprocess.run("python3 bookie1_tipico_live.py & python3 bookie2_bwin_live.py & python3 bookie3_betfair_live.py & wait", shell=True)
subprocess.run("python3 bookie-1.py & python3 bookie-2.py & python3 bookie-3.py & wait", shell=True)

#1.#focus only on btts
df_tipico = pickle.load(open('df_tipico','rb'))
df_tipico = df_tipico[['Teams', 'btts']]
df_tipico = df_tipico.replace(r'', '0\n0', regex=True)#odds with no values
df_tipico = df_tipico.replace(r'^\d+\.\d+$', '0\n0', regex=True)#odds with only one element

df_bwin = pickle.load(open('df_bwin','rb'))
df_bwin = df_bwin[['Teams', 'btts']]
df_bwin = df_bwin.replace(r'', '0\n0', regex=True)
df_bwin = df_bwin.replace(r'^\d+\.\d+$', '0\n0', regex=True)

df_betfair = pickle.load(open('df_betfair','rb'))
df_betfair = df_betfair[['Teams', 'btts']]
df_betfair = df_betfair.replace(r'', '0\n0', regex=True)#odds with no values
df_betfair = df_betfair.replace(r'^\d+\.\d+$', '0\n0', regex=True)#odds with only one element

#2.String matching
teams_1 = df_tipico['Teams'].tolist()
teams_2 = df_bwin['Teams'].tolist()
teams_3 = df_betfair['Teams'].tolist()

#team names and scores matched
df_tipico[['Teams_matched_bwin', 'Score_bwin']] = df_tipico['Teams'].apply(lambda x:process.extractOne(x, teams_2, scorer=fuzz.token_set_ratio)).apply(pd.Series)
df_tipico[['Teams_matched_betfair', 'Score_betfair']] = df_tipico['Teams'].apply(lambda x:process.extractOne(x, teams_3, scorer=fuzz.token_set_ratio)).apply(pd.Series)
df_bwin[['Teams_matched_betfair', 'Score_betfair']] = df_bwin['Teams'].apply(lambda x:process.extractOne(x, teams_3, scorer=fuzz.token_set_ratio)).apply(pd.Series)

df_surebet_tipico_bwin = pd.merge(df_tipico, df_bwin, left_on='Teams_matched_bwin', right_on='Teams')
df_surebet_tipico_bwin = df_surebet_tipico_bwin[df_surebet_tipico_bwin['Score_bwin']>60]
df_surebet_tipico_bwin = df_surebet_tipico_bwin[['Teams_x', 'btts_x', 'Teams_y', 'btts_y']]

df_surebet_tipico_betfair = pd.merge(df_tipico, df_betfair, left_on='Teams_matched_betfair', right_on='Teams')
df_surebet_tipico_betfair = df_surebet_tipico_betfair[df_surebet_tipico_betfair['Score_betfair']>60]
df_surebet_tipico_betfair = df_surebet_tipico_betfair[['Teams_x', 'btts_x', 'Teams_y', 'btts_y']]

df_surebet_bwin_betfair = pd.merge(df_bwin, df_betfair, left_on='Teams_matched_betfair', right_on='Teams')
df_surebet_bwin_betfair = df_surebet_bwin_betfair[df_surebet_bwin_betfair['Score_betfair']>60]
df_surebet_bwin_betfair = df_surebet_bwin_betfair[['Teams_x', 'btts_x', 'Teams_y', 'btts_y']]

#3,Finding Surebets
#Formula to find surebets
def find_surebet(frame):
    frame[['btts_x_1', 'btts_x_2']] = frame['btts_x'].apply(lambda x: x.split('\n')).apply(pd.Series).astype(float)
    frame[['btts_y_1', 'btts_y_2']] = frame['btts_y'].apply(lambda x: x.split('\n')).apply(pd.Series).astype(float)
    frame['sure_btts1'] = (1 / frame['btts_x_1']) + (1 / frame['btts_y_2'])
    frame['sure_btts2'] = (1 / frame['btts_x_2']) + (1 / frame['btts_y_1'])
    frame = frame[['Teams_x', 'btts_x', 'Teams_y', 'btts_y', 'sure_btts1', 'sure_btts2']]
    frame = frame[(frame['sure_btts1'] < 1) | (frame['sure_btts2'] < 1)]
    frame.reset_index(drop=True, inplace=True)
    return frame

#applying formula
df_surebet_tipico_bwin = find_surebet(df_surebet_tipico_bwin)
df_surebet_tipico_betfair = find_surebet(df_surebet_tipico_betfair)
df_surebet_bwin_betfair = find_surebet(df_surebet_bwin_betfair)

#creating dictionary
dict_surebet = {'Tipico-Bwin':df_surebet_tipico_bwin, 'Tipico-Betfair':df_surebet_tipico_betfair, 'Bwin-Betfair':df_surebet_bwin_betfair}

#formula to calculate stakes
def beat_bookies(odds1, odds2, total_stake):
    x, y = symbols('x y')
    eq1 = Eq(x + y - total_stake, 0) # total_stake = x + y
    eq2 = Eq((odds2*y) - odds1*x, 0) # odds1*x = odds2*y
    stakes = solve((eq1,eq2), (x, y))
    total_investment = stakes[x] + stakes[y]
    profit1 = odds1*stakes[x] - total_stake
    profit2 = odds2*stakes[y] - total_stake
    benefit1 = f'{profit1 / total_investment * 100:.2f}%'
    benefit2 = f'{profit2 / total_investment * 100:.2f}%'
    dict_gabmling = {'Odds1':odds1, 'Odds2':odds2, 'Stake1':f'${stakes[x]:.0f}', 'Stake2':f'${stakes[y]:.0f}', 'Profit1':f'${profit1:.2f}', 'Profit2':f'${profit2:.2f}',
                    'Benefit1': benefit1, 'Benefit2': benefit2}
    return dict_gabmling

total_stake = 100 #set your total stake
#calculating stakes
for frame in dict_surebet:
    if len(dict_surebet[frame])>=1:
        print('------------------SUREBETS Found! '+ frame +' (check team names)--------------------------------------------------')
        print(dict_surebet[frame])
        print('------------------Stakes-------------------------')
        for i, value in enumerate(dict_surebet[frame]['sure_btts1']):
            if value<1:
                odds1 = float(dict_surebet[frame].at[i, 'btts_x'].split('\n')[0])
                odds2 = float(dict_surebet[frame].at[i, 'btts_y'].split('\n')[1])
                teams = dict_surebet[frame].at[i, 'Teams_x'].split('\n')
                dict_1 = beat_bookies(odds1, odds2, total_stake)
                print(str(i)+' '+'-'.join(teams)+ ' ----> '+ ' '.join('{}:{}'.format(x, y) for x,y in dict_1.items()))
        for i, value in enumerate(dict_surebet[frame]['sure_btts2']):
            if value<1:
                odds1 = float(dict_surebet[frame].at[i, 'btts_x'].split('\n')[1])
                odds2 = float(dict_surebet[frame].at[i, 'btts_y'].split('\n')[0])
                teams = dict_surebet[frame].at[i, 'Teams_x'].split('\n')
                dict_2 = beat_bookies(odds1, odds2, total_stake)
                print(str(i) + ' ' + '-'.join(teams) + ' ----> ' + ' '.join('{}:{}'.format(x, y) for x, y in dict_2.items()))