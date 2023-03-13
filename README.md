# NHL-Model-3.0
NHL2.0

A simple python prediction model I built for predicting NHL games.

The script first performs a correlation step for each team's past data, where it determines which data points are highly correlated and removes them. Then it performs a regression step where it undergoes a backward elimination procedure based on statistical significance.
The remaining data and coefficients are then used along with the current data scraped from online to make predictions for the expected goals for and against each team. The final step is to use these predictions to predict the outcome of upcoming games, derived from the odds api.

Dependencies:
pandas, json, requests, time, datetime, random, sklearn, statsmodels, scipy, selenium, webdriver_manager, bs4, twilio.rest, itertools, tweepy
