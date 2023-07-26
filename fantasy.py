import sys, os
import pandas as pd
import requests

#globals
#east league id - 868258
#west league id - 352716

#update and run twice, once for each league
#this writes out a spreadsheet with the following columns
#player name, team, last year $, this year $ increase by $5, and this years projected $ amount
league_id = 352716
year=2022


#constants
POSITIONS_MAPPING = {
 1: 'QB',
 2: 'RB',
 3: 'WR',
 4: 'TE',
 5: 'K',
 16: 'D/ST'
 }


#get draft details
def get_draft_details(league_id, year):
    url = 'https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{}?view=mDraftDetail&view=mSettings&view=mTeam&view=modular&view=mNav&seasonId={}'.format(league_id, year)

    #return draft picks
    r = requests.get(url)
    espn_raw_data = r.json()
    espn_draft_detail = espn_raw_data[0]
    draft_picks = espn_draft_detail['draftDetail']['picks']

    #put draft picks into pandas data frame
    df = pd.DataFrame(draft_picks)
        
    draft_df = df[['overallPickNumber', 'playerId', 'teamId', 'bidAmount', 'memberId', 'lineupSlotId']]
    draft_df.rename(columns = {'teamId':'fantasy_mgr_id'}, inplace = True)
    draft_df.rename(columns = {'bidAmount':'priceLastYear'}, inplace = True)

    #add the +$5 column
    increased_price = []
    bid_amnt_list=draft_df['priceLastYear'].values.tolist()
    for price in bid_amnt_list:
        increased_price.append(price + 5)
    draft_df['priceToKeepThisYear'] = increased_price

    return draft_df

def get_player_info(league_id, year):
    #get player id and names
    headers = {'x-fantasy-filter': '{"filterActive":null}'}
    url = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{}/players?scoringPeriodId=0&view=players_wl'.format(year)
    r = requests.get(url, headers=headers)
    player_data = r.json()

    #put into simplified data fram
    df = pd.DataFrame(player_data)
    player_df = df[['defaultPositionId', 'fullName', 'id', 'proTeamId']]
    player_df.rename(columns = {'id':'player_id'}, inplace = True)
    return player_df

def get_team_info(league_id, year):
    #get team names
    url = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{}?view=proTeamSchedules_wl'.format(year)
    r = requests.get(url)
    team_data = r.json()
    team_names = team_data['settings']['proTeams']
    df = pd.DataFrame(team_names)
    team_df = df[['id', 'location', 'name']]
    team_df['team name']  = team_df['location'].astype(str) + ' ' + team_df['name']
    team_df.rename(columns = {'id':'proTeam_Id'}, inplace = True)
    return team_df

def build_projected_dollar_amt():
    #paste in fantasy pros projected auction dollar amt from https://www.fantasypros.com/nfl/auction-values/calculator.php
    #delete Kicker and defense lines
    #see file path and file name below

    #returns a dict of playername:projected dollar amt

    file_path=os.path.join('D:', os.sep, 'python_data')
    file_name = 'paste_from_fp.txt'

    player_dollar_dict ={}

    #read in file
    f=open(os.path.join(file_path, file_name))

    #QBs in superflex are weird. so want to pump up their $ amount to close match actual amount.
    #QBs come first, so enable this to start.
    #for position players, doesnt make sene to keep 1,2,3,4 $ projected players. since they would go for at least $6
    qb_parse = True
    min_dollar_thresh_to_keep = 1

    for line in f:

        #once you get to the RB Section, disable the qb multipler stuff for the rest of the list.
        if 'RB' in line:
            qb_parse = False
            min_dollar_thresh_to_keep = 4
        
        if not line.startswith('#'):
            if '$' in line:
                tmp=str(line)
                if int(tmp.split('$')[-1]) >= min_dollar_thresh_to_keep:
                    player_name = tmp.split('.',1)[-1]
                    player_name = player_name.split(',')[0]
                    player_name = player_name.split('\t')[-1]
                    dollar_amt = tmp.split('$')[-1]
                    dollar_amt = int(dollar_amt.split('\n')[0])
                    
                    #adjust qb price since superflex
                    if qb_parse is False:
                        multipler = 1
                    if qb_parse is True:
                        if dollar_amt > 19:
                            multipler=2
                        elif dollar_amt > 9:
                            multipler = 3
                        elif dollar_amt > 4:
                            multipler = 4
                        elif dollar_amt > 0:
                            multipler = 6
                        else:
                            multipler = 1

                    dollar_amt = int(dollar_amt * multipler)

                    #create dict
                    player_dollar_dict[player_name] = dollar_amt
                    
    f.close()     
    return player_dollar_dict


#########MAIN###############
# get all needed info for the year
draft_df = get_draft_details(league_id, year)
player_df = get_player_info(league_id, year)
team_df = get_team_info(league_id, year)

#print (draft_df)
#print (player_df)
#print (team_df)

df2 = pd.merge(draft_df, player_df, how='inner', left_on='playerId', right_on = 'player_id')
final_df = pd.merge(df2, team_df, how='inner', left_on='proTeamId', right_on = 'proTeam_Id')
league_df = final_df.replace({"defaultPositionId": POSITIONS_MAPPING})

league_draft_final = league_df[['fullName', 'team name', 'priceLastYear', 'priceToKeepThisYear']]
proj_dollar_dict = build_projected_dollar_amt()
#print(league_draft_final)

espn_drafted_players_list=league_draft_final['fullName'].tolist()
#print(espn_drafted_players_list)

#A list of names that need to be modifed between ESPN and Fantasy Pros
his_dollar_amt=proj_dollar_dict['Patrick Mahomes II']
proj_dollar_dict['Patrick Mahomes'] = his_dollar_amt
del proj_dollar_dict['Patrick Mahomes II']


print('Review this list, these are players for >4$ but were not drafted. names mismatched? \n this should be rookies and people not drafted last year because bad/hurt' )
for player in proj_dollar_dict:
    if player not in espn_drafted_players_list:
        print(player)


#make a list of players from fantasy pros
fantasy_pros_players = []
for player in proj_dollar_dict:
    fantasy_pros_players.append(player)

#make df of player name and proj $ amt
proj_dollars_df = pd.DataFrame.from_dict(proj_dollar_dict, orient='index')
proj_dollars_df.rename(columns = {0:'ProjectedAuctionPrice'}, inplace = True)
proj_dollars_df['full_name'] = fantasy_pros_players
#print(proj_dollars_df)

final_df = pd.merge(league_draft_final, proj_dollars_df, how='inner', left_on='fullName', right_on = 'full_name')
#print(final_df)

file_path=os.path.join('D:', os.sep, 'python_data')
file_name = 'keeper_values.csv'
file_path_name = os.path.join(file_path, file_name)

final_df.to_csv(file_path_name, index=False)

