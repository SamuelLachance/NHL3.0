import numpy as np
import pandas as pd

import webdriver_manager
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

import requests
from bs4 import BeautifulSoup
import re
import json
import unicodedata

from datetime import date

import seaborn as sns
import matplotlib.pyplot as plt

# ----- Global variables ------------------------------------------------------------
curr_games_played = [80]
past_games_played = [10, 40, 80]

today = str(date.today())

# WebDriver Options
opts = Options()
opts.add_argument("--headless")
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_experimental_option('useAutomationExtension', False)


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii

# =============================================== [--- Downloading data ---] ===============================================
def downloadData(fromSeason, thruSeason, today, games_played):
    global curr_data_home_GF, curr_data_home_GA, curr_data_away_GF, curr_data_away_GA
    print("Downloading data...")
    curr_data_home = []
    curr_data_away = []
    counter = 1
    
    for gps in games_played:
        # urls to access current data
        urlAway = f"https://www.naturalstattrick.com/teamtable.php?fromseason={fromSeason}&thruseason={thruSeason}&stype=2&sit=5v5&score=all&rate=y&team=all&loc=A&gpf=c&gp={gps}&fd=&td={today}"
        urlHome = f"https://www.naturalstattrick.com/teamtable.php?fromseason={fromSeason}&thruseason={thruSeason}&stype=2&sit=5v5&score=all&rate=y&team=all&loc=H&gpf=c&gp={gps}&fd=&td={today}"

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = opts) # downloads and sets newest chromedriver
        params = {'behavior': 'allow', 'downloadPath': r'currentData'}
        driver.execute_cdp_cmd('Page.setDownloadBehavior', params) # download behaviour set to this directory

        driver.get(urlAway) # driver launches
        
        filterButton = driver.find_element(By.ID, 'colfilterlb')
        filterButton.click()
        buttons = driver.find_elements(By.CSS_SELECTOR, '[class*="\\\\buttonspan"]')
        button_order = [7, 8, 10, 12, 13, 14, 15, 16, 17]

        for i in button_order:
            buttons[i].click()

        saveButton = driver.find_elements(By.TAG_NAME, "input")[29] # save button
        saveButton.click()
        time.sleep(3)
        
        curr_data_away.append(pd.read_csv('currentData/games.csv', usecols = ["Team","GP","TOI/GP","W","L","OTL","ROW","Points","Point %","CF/60","CA/60","CF%","FF/60","FA/60","FF%","SF/60","SA/60","SF%","GF/60","GA/60","GF%","xGF/60","xGA/60","xGF%","SCF/60","SCA/60","SCF%","SCSF/60","SCSA/60","SCSF%","SCGF/60","SCGA/60","SCGF%","SCSH%","SCSV%","HDCF/60","HDCA/60","HDCF%","HDSF/60","HDSA/60","HDSF%","HDGF/60","HDGA/60","HDGF%","HDSH%","HDSV%","MDCF/60","MDCA/60","MDCF%","MDSF/60","MDSA/60","MDSF%","MDGF/60","MDGA/60","MDGF%","MDSH%","MDSV%","LDCF/60","LDCA/60","LDCF%","LDSF/60","LDSA/60","LDSF%","LDGF/60","LDGA/60","LDGF%","LDSH%","LDSV%","SH%","SV%","PDO"], header = 0))
        
        print("(" + str(counter) +  ")" + "done away: " + str(gps) + " games played.") # i.e. (1) done away: 10 games played
        
        driver.close()
        driver.quit()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = opts) # downloads and sets newest chromedriver
        params = {'behavior': 'allow', 'downloadPath': r'currentData'}
        driver.execute_cdp_cmd('Page.setDownloadBehavior', params) # download behaviour set to this directory
        
        driver.get(urlHome)
        
        filterButton = driver.find_element(By.ID, 'colfilterlb')
        filterButton.click()
        buttons = driver.find_elements(By.CSS_SELECTOR, '[class*="\\\\buttonspan"]')

        for i in button_order:
            buttons[i].click()

        saveButton = driver.find_elements(By.TAG_NAME, "input")[29] # save button
        saveButton.click()
        time.sleep(3)
        
        curr_data_home.append(pd.read_csv('currentData/games.csv', usecols = ["Team","GP","TOI/GP","W","L","OTL","ROW","Points","Point %","CF/60","CA/60","CF%","FF/60","FA/60","FF%","SF/60","SA/60","SF%","GF/60","GA/60","GF%","xGF/60","xGA/60","xGF%","SCF/60","SCA/60","SCF%","SCSF/60","SCSA/60","SCSF%","SCGF/60","SCGA/60","SCGF%","SCSH%","SCSV%","HDCF/60","HDCA/60","HDCF%","HDSF/60","HDSA/60","HDSF%","HDGF/60","HDGA/60","HDGF%","HDSH%","HDSV%","MDCF/60","MDCA/60","MDCF%","MDSF/60","MDSA/60","MDSF%","MDGF/60","MDGA/60","MDGF%","MDSH%","MDSV%","LDCF/60","LDCA/60","LDCF%","LDSF/60","LDSA/60","LDSF%","LDGF/60","LDGA/60","LDGF%","LDSH%","LDSV%","SH%","SV%","PDO"], header = 0))

        print("(" + str(counter) +  ")" + "done home: " + str(gps) + " games played.") # i.e. (2) done home: 10 games played
        counter = counter + 1
        
        driver.close()
        driver.quit()
    
    # return home data, and away data
    return curr_data_home, curr_data_away

def get_elo():
    url = 'https://projects.fivethirtyeight.com/2023-nhl-predictions/'
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'html.parser')
    
    # get the table (id = standings-table)
    table = soup.find('table', attrs={'id':'standings-table'})
    
    # go into the table body
    table_body = table.find('tbody')
    
    # every row in the table, get the team name and the spi rating
    rows = table_body.find_all('tr')
    elo = {}
    for row in rows:
        # remove the number at the end of the team name (there is no space between the name and the number)
        elo[re.split('(\d+)', row.find('td', attrs={'class':'name'}).text)[0]] = row.find('td', attrs={'class':'elo'}).text
        
    # elo rating are currently between 1400 and 1700 change it to be between 0 and 1
    for key in elo:
        elo[key] = (float(elo[key]) - 1300) / 300
    
    return elo

def downloadCurrentData():
    curr_home_data, curr_away_data = downloadData(20222023, 20222023, today, curr_games_played)
    
    # convert to dataframes
    curr_home_data_df = pd.concat(curr_home_data)
    curr_away_data_df = pd.concat(curr_away_data)
    
    # save to csv
    curr_home_data_df.to_csv('currentData/home.csv', index = False)
    curr_away_data_df.to_csv('currentData/away.csv', index = False)

def downloadPastData():
    seasons = [
        [20212022, 20222023],
        [20192020, 20202021],
        [20182019, 20192020],
        [20172018, 20182019],
        [20162017, 20172018],
        [20152016, 20162017],
        [20142015, 20152016],
        [20132014, 20142015],
        [20122013, 20132014],
        [20112012, 20122013],
        [20102011, 20112012],
        [20092010, 20102011],
    ]
    
    all_away_data = []
    all_home_data = []
    
    for season in seasons:
        print("Downloading data for season: " + str(season[0]) + "-" + str(season[1]))
        home_data, away_data = downloadData(season[0], season[1], today, past_games_played)
        
        # convert to dataframes
        home_data_df = pd.concat(home_data)
        away_data_df = pd.concat(away_data)
        
        # append to list of dataframes
        all_away_data.append(away_data_df)
        all_home_data.append(home_data_df)
        
    # concatenate all dataframes
    all_away_df = pd.concat(all_away_data)
    all_home_df = pd.concat(all_home_data)
    
    print("Saving data to csv")
    all_away_df.to_csv('pastData/all_away_data.csv', index = False)
    all_home_df.to_csv('pastData/all_home_data.csv', index = False)
    
def add_elo(df, elo):
    # convert elo values to floats
    elo = {key: float(value) for key, value in elo.items()}
    df['ELO'] = df.index.map(lambda x: elo[get_team_from_team_name(elo, x)])
    return df

def get_team_from_team_name(elo, team):
    for key in elo:
        if key in team:
            return key
        
    return "Devils"

#downloadPastData() # if you want to download past data again
downloadCurrentData() # if you want to download current data again

# ---------- Get Data ----------

current_home_df = pd.read_csv('currentData/home.csv', usecols = ["Team","GP","TOI/GP","W","L","OTL","ROW","Points","Point %","CF/60","CA/60","CF%","FF/60","FA/60","FF%","SF/60","SA/60","SF%","GF/60","GA/60","GF%","xGF/60","xGA/60","xGF%","SCF/60","SCA/60","SCF%","SCSF/60","SCSA/60","SCSF%","SCGF/60","SCGA/60","SCGF%","SCSH%","SCSV%","HDCF/60","HDCA/60","HDCF%","HDSF/60","HDSA/60","HDSF%","HDGF/60","HDGA/60","HDGF%","HDSH%","HDSV%","MDCF/60","MDCA/60","MDCF%","MDSF/60","MDSA/60","MDSF%","MDGF/60","MDGA/60","MDGF%","MDSH%","MDSV%","LDCF/60","LDCA/60","LDCF%","LDSF/60","LDSA/60","LDSF%","LDGF/60","LDGA/60","LDGF%","LDSH%","LDSV%","SH%","SV%","PDO"], header = 0)
current_away_df = pd.read_csv('currentData/away.csv', usecols = ["Team","GP","TOI/GP","W","L","OTL","ROW","Points","Point %","CF/60","CA/60","CF%","FF/60","FA/60","FF%","SF/60","SA/60","SF%","GF/60","GA/60","GF%","xGF/60","xGA/60","xGF%","SCF/60","SCA/60","SCF%","SCSF/60","SCSA/60","SCSF%","SCGF/60","SCGA/60","SCGF%","SCSH%","SCSV%","HDCF/60","HDCA/60","HDCF%","HDSF/60","HDSA/60","HDSF%","HDGF/60","HDGA/60","HDGF%","HDSH%","HDSV%","MDCF/60","MDCA/60","MDCF%","MDSF/60","MDSA/60","MDSF%","MDGF/60","MDGA/60","MDGF%","MDSH%","MDSV%","LDCF/60","LDCA/60","LDCF%","LDSF/60","LDSA/60","LDSF%","LDGF/60","LDGA/60","LDGF%","LDSH%","LDSV%","SH%","SV%","PDO"], header = 0)

past_home_df = pd.read_csv('pastData/all_home_data.csv', usecols = ["Team","GP","TOI/GP","W","L","OTL","ROW","Points","Point %","CF/60","CA/60","CF%","FF/60","FA/60","FF%","SF/60","SA/60","SF%","GF/60","GA/60","GF%","xGF/60","xGA/60","xGF%","SCF/60","SCA/60","SCF%","SCSF/60","SCSA/60","SCSF%","SCGF/60","SCGA/60","SCGF%","SCSH%","SCSV%","HDCF/60","HDCA/60","HDCF%","HDSF/60","HDSA/60","HDSF%","HDGF/60","HDGA/60","HDGF%","HDSH%","HDSV%","MDCF/60","MDCA/60","MDCF%","MDSF/60","MDSA/60","MDSF%","MDGF/60","MDGA/60","MDGF%","MDSH%","MDSV%","LDCF/60","LDCA/60","LDCF%","LDSF/60","LDSA/60","LDSF%","LDGF/60","LDGA/60","LDGF%","LDSH%","LDSV%","SH%","SV%","PDO"], header = 0)
past_away_df = pd.read_csv('pastData/all_away_data.csv', usecols = ["Team","GP","TOI/GP","W","L","OTL","ROW","Points","Point %","CF/60","CA/60","CF%","FF/60","FA/60","FF%","SF/60","SA/60","SF%","GF/60","GA/60","GF%","xGF/60","xGA/60","xGF%","SCF/60","SCA/60","SCF%","SCSF/60","SCSA/60","SCSF%","SCGF/60","SCGA/60","SCGF%","SCSH%","SCSV%","HDCF/60","HDCA/60","HDCF%","HDSF/60","HDSA/60","HDSF%","HDGF/60","HDGA/60","HDGF%","HDSH%","HDSV%","MDCF/60","MDCA/60","MDCF%","MDSF/60","MDSA/60","MDSF%","MDGF/60","MDGA/60","MDGF%","MDSH%","MDSV%","LDCF/60","LDCA/60","LDCF%","LDSF/60","LDSA/60","LDSF%","LDGF/60","LDGA/60","LDGF%","LDSH%","LDSV%","SH%","SV%","PDO"], header = 0)

# =============================================== [--- Data Pre-Processing  ---] ===============================================

past_home_df = past_home_df.drop(columns = ['Team']) # drop team name
past_away_df = past_away_df.drop(columns = ['Team']) # drop team name

# =============================================== [--- Split Data  ---] ===============================================

# split data into training and testing
from sklearn.model_selection import train_test_split
X_train_home_gf, X_test_home_gf, y_train_home_gf, y_test_home_gf = train_test_split(past_home_df.drop(columns = ['GF/60']), past_home_df['GF/60'], test_size = 0.2, random_state = 42)
X_train_away_gf, X_test_away_gf, y_train_away_gf, y_test_away_gf = train_test_split(past_away_df.drop(columns = ['GF/60']), past_away_df['GF/60'], test_size = 0.2, random_state = 42)

X_train_home_ga, X_test_home_ga, y_train_home_ga, y_test_home_ga = train_test_split(past_home_df.drop(columns = ['GA/60']), past_home_df['GA/60'], test_size = 0.2, random_state = 42)
X_train_away_ga, X_test_away_ga, y_train_away_ga, y_test_away_ga = train_test_split(past_away_df.drop(columns = ['GA/60']), past_away_df['GA/60'], test_size = 0.2, random_state = 42)


# =============================================== [--- Ridge Regression  ---] ===============================================
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.svm import SVR

param_grid_xgb = {
    'max_depth': 3,
    'learning_rate': 0.1,
    'n_estimators': 1000,
    'gamma': 0
}

# ---- Build Models -----

ridge_home_gf = SVR(kernel='rbf', C=1e3, gamma='scale') #Ridge(alpha = 1.0) # create the model (goals for)
ridge_home_ga = SVR(kernel='rbf', C=1e3, gamma='scale') #Ridge(alpha = 1.0) # create the model (goals against)

ridge_away_gf = SVR(kernel='rbf', C=1e3, gamma='scale') #Ridge(alpha = 1.0) create the model (goals for)
ridge_away_ga = SVR(kernel='rbf', C=1e3, gamma='scale') #Ridge(alpha = 1.0) # create the model (goals against)

# ---- Fit Models -----

ridge_home_gf.fit(X_train_home_gf, y_train_home_gf) # fit the model
ridge_home_ga.fit(X_train_home_ga, y_train_home_ga) # fit the model

ridge_away_gf.fit(X_train_away_gf, y_train_away_gf) # fit the model
ridge_away_ga.fit(X_train_away_ga, y_train_away_ga) # fit the model

# ---- Predict -----

y_pred_home_gf = ridge_home_gf.predict(X_test_home_gf) # predict the goals for
y_pred_home_ga = ridge_home_ga.predict(X_test_home_ga) # predict the goals against

y_pred_away_gf = ridge_away_gf.predict(X_test_away_gf) # predict the goals for
y_pred_away_ga = ridge_away_ga.predict(X_test_away_ga) # predict the goals against

mse_home_gf = mean_squared_error(y_test_home_gf, y_pred_home_gf)
mse_home_ga = mean_squared_error(y_test_home_ga, y_pred_home_ga)
mse_away_gf = mean_squared_error(y_test_away_gf, y_pred_away_gf)
mse_away_ga = mean_squared_error(y_test_away_ga, y_pred_away_ga)

print("Home Mean Squared Error Goals For: " + str(mse_home_gf))
print("Home Mean Squared Error Goals Against: " + str(mse_home_ga))
print("Away Mean Squared Error Goals For: " + str(mse_away_gf))
print("Away Mean Squared Error Goals Against: " + str(mse_away_ga))


# =============================================== [--- Predict on Current Data  ---] ===============================================
# create a dataframe to hold the predictions
predictions_df = pd.DataFrame(columns = ['Team', 'Home Goals For', 'Away Goals For', 'Home Goals Against', 'Away Goals Against'])

predictions_df['Team'] = current_home_df['Team'] # add the team names
predictions_df = predictions_df.set_index('Team')

current_home_gf = current_home_df.drop(columns = ['GF/60', 'Team'])
current_away_gf = current_away_df.drop(columns = ['GF/60', 'Team'])
current_home_ga = current_home_df.drop(columns = ['GA/60', 'Team'])
current_away_ga = current_away_df.drop(columns = ['GA/60', 'Team'])

# use the ridge models to predict the goals for and goals against
current_home_gf_pred = ridge_home_gf.predict(current_home_gf)
current_away_gf_pred = ridge_away_gf.predict(current_away_gf)
current_home_ga_pred = ridge_home_ga.predict(current_home_ga)
current_away_ga_pred = ridge_away_ga.predict(current_away_ga) 

# add the predictions to the dataframe
predictions_df['Home Goals For'] = current_home_gf_pred
predictions_df['Away Goals For'] = current_away_gf_pred
predictions_df['Home Goals Against'] = current_home_ga_pred
predictions_df['Away Goals Against'] = current_away_ga_pred

# add an average row at the bottom for each column
predictions_df.loc['Average'] = predictions_df.mean()

# create a attack strength and defense strength column (for home and away) (value between 0 and 1)
def calculate_attack_strength(goals_for, average_goals_for, elo):
    goal_based_strength = goals_for / average_goals_for
    return goal_based_strength * (1 - elo) + elo

def calculate_defense_strength(goals_against, average_goals_against, elo):
    goal_based_strength = goals_against / average_goals_against
    return goal_based_strength * (1 - elo) + elo

def normalize_series(series):
    min_value = series.min()
    max_value = series.max()
    return (series - min_value) / (max_value - min_value)

strengths_df = pd.DataFrame(columns = ['Home Attack Strength', 'Home Defense Strength', 'Away Attack Strength', 'Away Defense Strength'])
strengths_df['Team'] = predictions_df.index # add the team names
strengths_df = strengths_df.set_index('Team') # set the index to the team names

elo = get_elo()

# add elo to the strengths dataframe
strengths_df = add_elo(strengths_df, elo)

strengths_df['Home Attack Strength'] = predictions_df.apply(lambda row: calculate_attack_strength(row['Home Goals For'], predictions_df.loc['Average']['Home Goals For'], strengths_df.loc[row.name]['ELO']), axis = 1)
strengths_df['Home Defense Strength'] = predictions_df.apply(lambda row: calculate_defense_strength(row['Home Goals Against'], predictions_df.loc['Average']['Home Goals Against'], strengths_df.loc[row.name]['ELO']), axis = 1)
strengths_df['Away Attack Strength'] = predictions_df.apply(lambda row: calculate_attack_strength(row['Away Goals For'], predictions_df.loc['Average']['Away Goals For'], strengths_df.loc[row.name]['ELO']), axis = 1)
strengths_df['Away Defense Strength'] = predictions_df.apply(lambda row: calculate_defense_strength(row['Away Goals Against'], predictions_df.loc['Average']['Away Goals Against'], strengths_df.loc[row.name]['ELO']), axis = 1)


# Calculate the weighted overall strength
attack_weight = 0.5
defense_weight = 0.5
strengths_df['Overall Strength'] = strengths_df.apply(
    lambda row: (attack_weight * (row['Home Attack Strength'] + row['Away Attack Strength'])) -
                (defense_weight * (row['Home Defense Strength'] + row['Away Defense Strength'])),
    axis=1)

# Normalize the overall strength to the range [0, 1]
strengths_df['Overall Strength'] = normalize_series(strengths_df['Overall Strength'])

# =============================================== [--- Predict Games  ---] ===============================================
from scipy.stats import poisson
import xgboost as xgb

def predict_game(home_team, away_team):
    home_team = remove_accents(home_team).decode("utf-8")
    away_team = remove_accents(away_team).decode("utf-8")
    home_attack_strength = strengths_df.loc[home_team]['Home Attack Strength']
    home_defense_strength = strengths_df.loc[home_team]['Home Defense Strength']
    home_overall_strength = strengths_df.loc[home_team]['Overall Strength']

    away_attack_strength = strengths_df.loc[away_team]['Away Attack Strength']
    away_defense_strength = strengths_df.loc[away_team]['Away Defense Strength']
    away_overall_strength = strengths_df.loc[away_team]['Overall Strength']

    # Define weights for overall strength
    overall_strength_weight = 0.5
    attack_defense_strength_weight = 1 - overall_strength_weight

    # Adjust the expected goals for with overall strength
    home_expected_gf = (home_attack_strength * away_defense_strength * predictions_df.loc['Average']['Home Goals For']) * attack_defense_strength_weight + (home_overall_strength * overall_strength_weight)
    away_expected_gf = (away_attack_strength * home_defense_strength * predictions_df.loc['Average']['Away Goals For']) * attack_defense_strength_weight + (away_overall_strength * overall_strength_weight)
    
    # Initialize probabilities
    home_prob = 0
    away_prob = 0
    tie_prob = 0

    # Use NumPy to create Poisson probability arrays
    home_poisson = poisson.pmf(np.arange(14), home_expected_gf)
    away_poisson = poisson.pmf(np.arange(14), away_expected_gf)

    # Calculate probabilities
    for i in range(14):
        for j in range(14):
            prob = home_poisson[i] * away_poisson[j]

            if i > j:
                home_prob += prob
            elif j > i:
                away_prob += prob
            else:
                tie_prob += prob

    # Distribute the tie probability evenly between the home and away win probabilities
    away_prob += tie_prob / 2
    home_prob += tie_prob / 2
                
    return home_prob, away_prob , home_expected_gf , away_expected_gf


# print a heatmap of the team's strengths
def illustrate_strengths():
    plt.figure(figsize = (13, 8))
    sns.heatmap(strengths_df.sort_values(by = 'ELO', ascending = False), annot = True)
    plt.show()

# =============================================== [--- Odds ---] ===============================================

api_key = '8be3ba1d05ea7d3cda1d4ec6953e78c9' #'74a13ca8f52c11c2476a5cc7db5d34d0' # api key for sports betting odds

def decimal_to_american(odds):
    if odds > 2:
        return int((odds - 1) * 100)
    else:
        return int(-100 / (odds - 1))

# returns the odds for the away team and the home team (decimal)
def get_odds(home_team, away_team):
    home_prob, away_prob , home_goals, away_goals = predict_game(home_team, away_team)
    
    away_odds = round(1 / away_prob, 2)
    home_odds = round(1 / home_prob , 2)
    
    return home_odds , away_odds , home_goals , away_goals

def clean_odds(date):
    odds_api_key = '8be3ba1d05ea7d3cda1d4ec6953e78c9'
    odds_endpoint = 'https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds'

    params = {
        'regions': 'us',
        'oddsFormat': 'american',
        'dateFormat': 'iso',
        'apiKey': odds_api_key,
        'sport': 'icehockey_nhl',
        'date': date, 
        'Markets' : 'h2h', 
        'Bookmakers' : 'fanduel'
    }

    response_odds = requests.get(odds_endpoint, params=params)
    data_odds = response_odds.json()
    simple_odds = []
    for game in data_odds:
        away_team = game['away_team']
        home_team = game['home_team']

        if game['bookmakers'][0]['markets'][0]['outcomes'][0]['name'] == home_team :
          home_odds = game['bookmakers'][0]['markets'][0]['outcomes'][0]['price']
        else:
          home_odds = game['bookmakers'][0]['markets'][0]['outcomes'][1]['price']
        
        if game['bookmakers'][0]['markets'][0]['outcomes'][0]['name'] == away_team :
          away_odds = game['bookmakers'][0]['markets'][0]['outcomes'][0]['price']
        else:
           away_odds = game['bookmakers'][0]['markets'][0]['outcomes'][1]['price']
        
        simple_odds.append([home_team, away_team, home_odds, away_odds])
        
    return simple_odds

def calculate_picks(odds):
    for game in odds:
        given_home_odds = game[2]
        given_away_odds = game[3]
        home_team = game[0]
        away_team = game[1]
        
        my_home_odds, my_away_odds , home_goals , away_goals = get_odds(game[0], game[1])
        
        print(away_team, "vs", home_team)
        print("Away Score :" , away_goals , "away vegas odds : ", given_away_odds, "My odds :", decimal_to_american(my_away_odds))
        print("Home Score : ", home_goals , "home vegas odds : ", given_home_odds, "My odds :", decimal_to_american(my_home_odds))
        
        
odds = clean_odds(today)
calculate_picks(odds)

print("Code Completed.")
