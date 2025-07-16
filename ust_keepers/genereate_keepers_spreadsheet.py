import sys
import os
import pandas as pd


#paste in fantasy pros projected auction dollar amt from https://www.fantasypros.com/nfl/auction-values/calculator.php
#paste into DC:\python_data\paste_from_fp.txt
def get_auction_values_from_fantasy_pros():

    #dict to update names to ESPN naming standards
    name_change = {
        'Patrick Mahomes II': 'Patrick Mahomes',
        'Deebo Samuel Sr.': 'Deebo Samuel',
        'Hollywood Brown': 'Marquise Brown'
    }
    player_dollar_dict ={}

    #read file
    file_path=os.path.join('C:', os.sep, 'python_data')
    file_name = 'paste_from_fp.txt'
    f=open(os.path.join(file_path, file_name))

    for line in f:

        #read data lines, and parse out each piece of data
        data=line.split('\n')[0].split('\t')
        name=data[1].split('(')[0][:-1]
        if name in name_change:
            name = name_change[name]
        team = data[1].split('(')[1].split('-')[0][:-1]
        position = data[1].split('(')[1].split('-')[1][1:-1]
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

        player_dollar_dict[name] = auction_dollar
        #print(str(data) + name + team + position + str(auction_dollar)) 

    f.close()     

    return (player_dollar_dict)          

#manually copy/paste the names of keepers from last year into a list

file_path=os.path.join('C:', os.sep, 'python_data')
keepers_counter = 0

EAST_previous_keepers = ['Joe Burrow',
'Tony Pollard',
'Lamar Jackson',
'Justin Fields',
'Jalen Hurts',
'Rhamondre Stevenson',
'Daniel Jones',
'Travis Kelce',
'Nick Chubb',
'Trevor Lawrence',
'Deshaun Watson',
'Garrett Wilson',
'Tyreek Hill',
'Amon-Ra St. Brown',
'Dameon Pierce',
'DeVonta Smith',
'Patrick Mahomes',
'Chris Olave',
'Miles Sanders',
'Alexander Mattison']

WEST_previous_keepers = ['Tony Pollard',
'Justin Fields',
'Joe Burrow',
'Rhamondre Stevenson',
'Patrick Mahomes',
'Lamar Jackson',
'Travis Kelce',
'Nick Chubb',
'Jalen Hurts',
'Garrett Wilson',
'Chris Olave',
'Breece Hall',
'Trevor Lawrence',
'Jaylen Waddle',
'T.J. Hockenson',
'Tyreek Hill',
'Dallas Goedert',
'Austin Ekeler']

##UPDATE for east/west
past_keepers = WEST_previous_keepers
file_name = 'WEST_espn_draft_copy_paste.txt'

#get fantasy pros data for auction values
player_dollar_dict = get_auction_values_from_fantasy_pros()

#read in file
f=open(os.path.join(file_path, file_name),'r')
draft_results = f.read()
f.close

#create columns for pandas data frame
col_names = {'fullName':[], 'position':[], 'teamName':[], 'auctionPriceLastYear':[], 'keptYears':[], 'priceToKeep':[], 'projectedAuctionPrice':[], 'projectedSavings':[]}
df = pd.DataFrame([], columns=col_names)

draft_results = draft_results.split('OFFER AMOUNT')
#draft_results.pop(0)

#count through all 10 teams
for team_id in range (1,11):

    #team list is full list of all players and prices, split by new line character
    team_list=draft_results[team_id].split('\n')

    #list [2:3] returns
    #Miles Sanders Car, RB
    #$10

    #counting loop for 1 team's drafted players
    for i in range (0,48,3):

        #reset each loop
        keptYears = 0

        #parse the rows for each piece of data
        player_pos = team_list[i+2].split(',')[1][1:]
        player_price = int(team_list[i+3][1:])
        player_name_team = team_list[i+2].split(',')[0]

        if player_name_team[-4]==' ':
            #3 letter team name.
            player_team = player_name_team[-3:]
            player_name = player_name_team[:-3:][:-1]
        elif player_name_team[-3]==' ':
            #2 letter team name.
            player_team = player_name_team[-2:]
            player_name = player_name_team[:-2:][:-1]

        #update kept years and price to keep this year
        if player_name in past_keepers:
            keepers_counter = keepers_counter + 1
            keptYears = 1
        if keptYears == 1:
            price_to_keep = player_price + 10 #this is only 10 because 5 was already added last year so a total of $15
        else:
            price_to_keep = player_price + 5

        #add in projected auction price this year
        if player_name in player_dollar_dict:
            auction_price = int(player_dollar_dict[player_name])
        else:
            auction_price = 0
            print("didn't exist in FantasyPros top 300: " + player_name)
        projected_savings = auction_price - price_to_keep
        

        #create new dict to add to df
        df_new = {'fullName': player_name, 'position': player_pos, 'teamName': player_team, 
                  'auctionPriceLastYear': player_price, 'keptYears':keptYears, 'priceToKeep':price_to_keep, 
                  'projectedAuctionPrice':auction_price, 'projectedSavings':projected_savings}
        
        #append to dataframe
        df = df._append(df_new, ignore_index = True)
    
print("all the above players should be massive drop offs, since drafted last year but NOT in top 300 this year.  If a player doesn't fit that theme, investigate. Perhpas their name is different ESPN vs Fantasy Pros ")

if keepers_counter != 20:
    print('keepers counter was ' + str(keepers_counter) + '. Which is a problem, should be exactly 20 keepers from last year. 2/team' )

df.to_csv(os.path.join(file_path, (file_name.split('_')[0] + '_output_csv.csv')))
