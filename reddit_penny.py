import pandas as pd 
import praw
import time
from datetime import datetime, date
from operator import attrgetter
import re
import yfinance as yf

clientid = 'XXXX'
secret = 'XXXX'
username = 'XXXX'
password = 'XXXX'
useragent = 'XXXX'

reddit = praw.Reddit(client_id= clientid, 
                    client_secret= secret,
                    user_agent = useragent,
                    username= username,
                    password= password)

# retrieving posts from a time frame -  inspired by gavin19 https://github.com/gavin19
def get_posts(subreddit):
    sub = reddit.subreddit(subreddit)
    posts = set() 
    posts.update(sub.new(limit=None))

    sorted(posts, key=attrgetter("created_utc")) # sort by newest first
    return posts

def userDate(tstamp):
    return datetime.utcfromtimestamp(tstamp).strftime('%Y-%m-%d %H:%M:%S')

#get anything that looks like a stock symbol in the retrieved posts
def get_symbol(text):
    tickers = re.findall(r"[A-Z]{3,6}", str(text)) #regex for consecutive capital letters
    return tickers

#count frequency of each unique symbol found    
def count_tickers(ticker_list):
    freq = {}
    for t in ticker_list:
        if t in freq:
            freq[t] += 1
        else:
            freq[t] = 1
    return freq

#retrieve stock information from Yahoo Finance
def get_info(symbols):
    symbol, name, count, indus, current_price, day_change, week_change = [],[],[],[],[],[],[]
    for s,c in symbols.items():
        ticker = yf.Ticker(s)
        try:
            print(ticker.info['longName']) #test if the symbol retrived exists on an exchange        
        except:
            continue #skip if doesnt exist
        else:
            print(f'Adding {s}')
            symbol.append(s)
            name.append(ticker.info['longName'])
            try:
                indus.append(ticker.info['industry'])
            except:
                indus.append('N/A')
            count.append(c)

            mo_data = ticker.history(period='1mo')
 
            if len(mo_data) > 1: #check if price info exists (eg. stock may be delisted)
                current_price.append(mo_data['Close'][-1])

                daychange = (mo_data['Close'][-1] - mo_data['Close'][-2]) / mo_data['Close'][-2] * 100 #calculate price change in the past day
                weekchange = (mo_data['Close'][-1] - mo_data['Close'][-6]) / mo_data['Close'][-6] * 100 #calculate price change in past week
 
                day_change.append(f'{round(daychange,2)}%')
                week_change.append(f'{round(weekchange,2)}%')
            
            else:
                current_price.append(0)
                day_change.append(0)
                week_change.append(0)
    
    #add to dataframe
    d = {'Mentions': count, 'Symbol': symbol, 'Company Name': name, 'Industry': indus, 'Price': current_price, 'Day Change': day_change, 'Week Change': week_change}
    df = pd.DataFrame(data= d)
    df = df.sort_values(by=['Mentions'], ascending=False)
    df['Date'] = date.today()

    return df         

def main():
    subreddit = input('Enter a subreddit >> ')
    print('Enter a time frame (days and hours).')
    days = int(input('Enter the number of days in your range  >> '))
    hours = int(input('Enter the number of hours in your range  >> '))
    tframe = (days * 86400) + (hours * 3600)
    start_time = time.time() - tframe  

    print("\nRetrieving submissions...")
    posts = get_posts(subreddit)
    matches = [p for p in posts if p.created_utc > start_time]

    print("\nFound " + str(len(matches)) + " matches\n")
    all_tickers = []
    
    for m in matches:
        print(m.title + " : " + userDate(m.created_utc))
        t_list = get_symbol(m.title)
        print(t_list)
        
        for t in t_list:
            all_tickers.append(t)
    
    dict_ = count_tickers(all_tickers)

    data = get_info(dict_)
    data.to_csv(f'{date.today()}_most_mentioned_stonks.csv')
    data.head()

main()
