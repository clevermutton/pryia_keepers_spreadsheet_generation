import sys
import os
import pandas as pd

'''
this creates a spreadsheet of all the player's auction values in fantasy pros
use this in auction_draft_setup.xlxs to keep a running total of people's bids and extra money out there
'''

#paste in fantasy pros projected auction dollar amt from https://www.fantasypros.com/nfl/auction-values/calculator.php
#paste into D:\python_data\paste_from_fp.txt
def get_auction_values_from_fantasy_pros():

    #dict to update names to ESPN naming standards
    name_change = {
        'Patrick Mahomes II': 'Patrick Mahomes',
        'Deebo Samuel Sr.': 'Deebo Samuel',
        'Hollywood Brown': 'Marquise Brown'
    }

    #read file
    file_path=os.path.join('D:', os.sep, 'python_data')
    file_name = 'paste_from_fp.txt'
    f=open(os.path.join(file_path, file_name))
    col_names = ['fullName', 'position', 'teamName', 'projectedAuctionPrice']
    players = [col_names]

    for line in f:

        #read data lines, and parse out each piece of data
        data=line.split('\n')[0].split('\t')
        name=data[1].split('(')[0][:-1]
        if name in name_change:
            name = name_change[name]
        team = data[1].split('(')[1].split('-')[0][:-1]
        position = data[1].split('INJ')[0].split('(')[1].split('-')[1][1:-1]
        auction_dollar = int(data[2].split('$')[1])
        #print(str(data) + name + team + position + str(auction_dollar)) 

        #adjust QB prices since flex makes it weird
        if position == 'QB':
            if auction_dollar > 19:
                multipler=2
            elif auction_dollar > 9:
                multipler = 3
            elif auction_dollar > 4:
                multipler = 4
            elif auction_dollar > 0:
                multipler = 6
            else:
                multipler = 1
            auction_dollar = multipler * auction_dollar

        players.append([name, team, position, auction_dollar])

    f.close()     

    return (players)          

#manually copy/paste the names of keepers from last year into a list

file_path=os.path.join('D:', os.sep, 'python_data')
file_name = 'formated_fp.txt'

#get fantasy pros data for auction values
players_list = get_auction_values_from_fantasy_pros()

#create columns for pandas data frame
col_names = {'fullName':[], 'teamName':[],'position':[], 'projectedAuctionPrice':[]}
df = pd.DataFrame(list(players_list))

print(df)
    
df.to_csv(os.path.join(file_path, 'draft_setup.csv')) 
