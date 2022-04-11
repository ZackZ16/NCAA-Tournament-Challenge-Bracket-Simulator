import pandas as pd
import bracketology
import random

'''
 Column Keys: 
        TEAM: Team Name
        CONF: Conference
        G: Number of Games Played
        W: Number of Wins
        ADJOE: Adjusted Offensive Efficiency
        ADJDE: Adjusted Defensive Efficiency
        BARTHAG: Power Level (Chance of Beating Div 1 Team)
        EFG_O: Field Goal Percentage
        EFG_D: Percentage of Field Goals Allowed 
        TOR: Turnover Rate
        TORD: Steal Rate
        ORB: Offensive Rebound Rate
        DRB: Offensive Rebound Rate Allowed
        FTR: Free Throw Rate (How Often the Team Shoots Free Throws)
        FTRD: Free Throw Rate Allowed
        2P_O: Two-Point Shooting Percentage
        2P_D: Two-Point Shooting Percentage Allowed
        3P_O: Three-Point Shooting Percentage
        3P_D: Three-Point Shooting Percentage Allowed
        ADJ_T: Adjusted Tempo (Possesions in 40 Minutes against an Avg Div 1 Team)
        WAB: Wins Above Bubble (Above the Cutoff)
        POSTSEASON: Round the Team got Knocked Out (ex. R64, R32 ... Champion)
        SEED: Seed in the Tournament 
        YEAR: Year of the Tournament
'''

# dataframe for all college basketball stats from 2013 - 2019
cbb1319 = pd.read_csv('cbb.csv')

# assign numerical vals to postseason var to compute correlations
cbb1319.POSTSEASON = cbb1319.POSTSEASON.replace('R68', -1)
cbb1319.POSTSEASON = cbb1319.POSTSEASON.replace('R64', 0)
cbb1319.POSTSEASON = cbb1319.POSTSEASON.replace('R32', 1)
cbb1319.POSTSEASON = cbb1319.POSTSEASON.replace('S16', 2)
cbb1319.POSTSEASON = cbb1319.POSTSEASON.replace('E8', 3)
cbb1319.POSTSEASON = cbb1319.POSTSEASON.replace('F4', 4)
cbb1319.POSTSEASON = cbb1319.POSTSEASON.replace('2ND', 5)
cbb1319.POSTSEASON = cbb1319.POSTSEASON.replace('Champions', 6)

# replace team names that don't allign with the bracket team names
# probably could use a regex expression after examining patterns in misnamed values
# most commmon inconsistencies include periods, apostrophes, and acronyms
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('UCF', 'Central Florida')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('Saint Louis', 'St Louis')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('Mississippi', 'Ole Miss')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('Saint Mary\'s', 'St Marys')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('North Carolina St.', 'NC State')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('Miami FL', 'Miami')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('Saint Joseph\'s', 'St Josephs')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('Milwaukee', 'Wisconsin Milwaukee')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('Stephen F. Austin', 'Stephen F Austin')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('UC Irvine', 'Cal Irvine')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('St. John\'s', 'St Johns')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('Green Bay', 'Wisconsin Green Bay')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('Cal St. Bakersfield', 'Cal St Bakersfield')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('Middle Tennessee', 'Middle Tennessee St')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('Mount St. Mary\'s', 'Mount St Marys')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('St. Bonaventure', 'St Bonaventure')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('Cal St. Fullerton', 'Cal St Fullerton')
cbb1319['TEAM'] = cbb1319.loc[:, 'TEAM'].replace('Penn', 'Pennsylvania')

# dataframe of correlations for every variable in the dataframe
# not related to the simulator just cool to look at to become familiar with the data
winCorr = cbb1319.corr()

years = [2013,2014,2015,2016,2017,2018,2019]
brackets = []

# create bracket objects for years 2013 - 2019
for year in years:
    brackets.append(Bracket(year))
    
# init year var to slice dataframe by year
year = 2013

def pick_winning_team(game):
    
    # filter dataframe by year of the tournament 
    cbbyear = cbb1319.loc[:, 'YEAR'] == year
    
    # create a copy of the cbb1319 dataframe to avoid a SettingWithCopyWarning
    cbbyear = cbb1319[cbbyear].copy()
    
    # For some reason in 2019 the bracket obj switches from Cal Irvine 
    # to UC Irvine. In all other years it is called Cal Irvine.
    if year == 2019:
        cbbyear["TEAM"] = cbbyear.loc[:, 'TEAM'].replace('Cal Irvine', 'UC Irvine')
    
    # pull out both teams from the Game obj
    team1 = game.top_team
    team2 = game.bottom_team
    
    # set value of Team.stats if empty to improve runtime and avoid 
    # unnecessary dataframe lookups, this way the dataframe is referenced only
    # once for each team in each bracket
    if not team1.stats:
        t1 = cbbyear['TEAM'].str.strip('.') == team1.name
        t1 = cbbyear[t1]
        t1 = t1.to_dict()
        team1.stats = t1
    
    if not team2.stats:
        t2 = cbbyear['TEAM'].str.strip('.') == team2.name
        t2 = cbbyear[t2]
        t2 = t2.to_dict()
        team2.stats = t2
    
    """
    team1 and team2 are Team objects which contain a Team.stats object variable.
    The Team.stats variable contains a dictionary of team stats created from that team's
    row in the cbb1319 dataframe.
    The dictionary is organized as follows:
    
        Team.stats = {'column name from cbb dataframe': 
                          {cbb dataframe index # (int): value of the column}}
                                                         
    """
    teams = [team1,team2]
    res = []
    
    # loop through both teams and assign a numerical value for comparison
    for t in teams:
        
        t = t.stats
        
        # pull out the index # from the dict to properly extract stat value
        index = list(t['TEAM'].keys())[0]
        
        # sample algorithm using random math to calculate which team wins
        # you can do whatever you want here as long as you return a Team obj (expected winner)
        # res.append((((t['ADJOE'][index] + t['ADJDE'][index])/2) + 
        #         ((t['W'][index]/t['G'][index])*t['BARTHAG'][index]) +
        #         (t['EFG_O'][index] - t['EFG_D'][index]) +
        #         (t['TOR'][index] - t['TORD'][index]) +
        #         (t['ORB'][index]-t['DRB'][index]) + 
        #         (t['FTR'][index] - t['FTRD'][index]) +
        #         (t['2P_O'][index] - t['2P_D'][index]) +
        #         (t['3P_O'][index] - t['3P_D'][index]) +
        #         (t['ADJ_T'][index])))
        
        res.append(t['G'][index])
        
        
    if res[0] > res[1]:
        if game.round_number == 6:
            print('Predicted Winner:', team1.name)
            print('Predicted Championship:', team2.name, 'vs', team1.name)
        return team1
    else:
        if game.round_number == 6:
            print('Predicted Winner:', team2.name)
            print('Predicted Championship:', team2.name, 'vs', team1.name)
        return team2
            

# Initialize simulation parameters
# number of times to simulate through all years
# n_sims should only be > 1 if you incorporate some type of random probability
n_sims = 1 
total_sims = (n_sims * len(brackets))
scores = []
correct_games = []

# Loop through a each bracket n_sims times
def simulate():
    for i in range(n_sims):
        for bracket in brackets:
        
            # set the year of the bracket to slice the dataframe by year
            year = int(bracket.year)
            
            # Run the algorithm on the bracket
            # All you need is a function that takes in a game obj and returns
            # a Team obj to run the bracket simulation.
            print('Year:', bracket.year)
            print('Championship Actual:', bracket.result['championship'][0]['Team'], 'vs',
                                bracket.result['championship'][1]['Team'])
            print('Winner Actual:', bracket.result.get('winner')['Team'])
            
            bracket.score(sim_func=pick_winning_team, verbose = True)
            print()

            # Save the scoring results in a list
            scores.append(bracket.total_score)
            correct_games.append(bracket.n_games_correct)

    # Calculate the average across all simulations
    avg_score = round(sum(scores) / total_sims)
    avg_correct = round(sum(correct_games) / total_sims)

    # Print result

    return avg_score*10, avg_correct
    # return f"Average total score {avg_score*10}/1920\nAverage number of games guessed correctly {avg_correct}/64"
    # print(f"Average number of games guessed correctly {avg_correct}/64")
simulate()