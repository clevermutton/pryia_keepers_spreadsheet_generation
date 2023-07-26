import sys, os

#paste in fantasy pros projected auction dollar amt from https://www.fantasypros.com/nfl/auction-values/calculator.php
#delete Kicker and defense lines
#see file path and file name below

#returns a dict of playername:projected dollar amt

file_path=os.path.join('D:', os.sep, 'python_data')
file_name = 'paste_from_fp.txt'

player_dollar_dict ={}

#read in file
f=open(os.path.join(file_path, file_name))

for line in f:
    #only get lines with $ amount >= 5 in them
    if not line.startswith('#'):
        if '$' in line:
            tmp=str(line)
            if int(tmp.split('$')[-1]) > 3:
                player_name = tmp.split('.')[1]
                player_name = player_name.split(',')[0]
                player_name = player_name.split('\t')[-1]
                dollar_amt = tmp.split('$')[-1]
                dollar_amt = dollar_amt.split('\n')[0]
                player_dollar_dict[player_name] = dollar_amt
                
f.close()     

print (player_dollar_dict)           

