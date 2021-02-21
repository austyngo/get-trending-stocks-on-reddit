# get-trending-stocks-on-reddit
Scrape Reddit submissions to get the most mentioned stocks within a time frame and return a dataframe using the Reddit API (PRAW) and the Yahoo Finance API (yfinance).

Returns a Dataframe with the following features:
* Symbol
* Number of mentions
* Company Name
* Industry
* Current Price
* Day Change %
* Week Change %
