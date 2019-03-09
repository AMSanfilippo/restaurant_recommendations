# get data for analysis of Eater NY "Restaurants to Try This Weekend"

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import datetime
import json

# function to get yelp data for a recommended restaurant
def get_yelp(name,address,api_key):
    
    print('getting yelp info for ' + name)
        
    # format restaurant name for yelp api search        
    cardinal_dict = {'East': 'E', 'North': 'N', 'South': 'S', 'West': 'W'}
    address_abbr = address
    for c in cardinal_dict.keys():
        if c in address:
            address_abbr = address_abbr.replace(c,cardinal_dict[c])
    url_name = '%20'.join([''.join(filter(str.isalpha, s)) for s in name.split(' ')])
    
    yelp_url = 'https://api.yelp.com/v3/businesses/search?term=' + url_name + '&location=new%20york'
    yelp_resp = requests.get(yelp_url,headers={'Authorization':'Bearer ' + api_key})
    yelp_json = json.loads(yelp_resp.text)['businesses']
    
    entry = {}
    for y in yelp_json:
        if (y['location']['address1'] == address) or (y['location']['address1'] == address_abbr):
            entry = y
        
    try:
        price = entry['price']
    except:
        price = ''
        
    try:
        rating = entry['rating']
    except:
        rating = np.nan
        
    try:
        cuisine = entry['categories'][0]['title']
    except:
        cuisine = ''
        
    try:
        latitude = entry['coordinates']['latitude']
    except:
        latitude = np.nan
        
    try:
        longitude = entry['coordinates']['longitude']
    except:       
        longitude = np.nan
        
    return [price,rating,cuisine,latitude,longitude]

# function to pull data for a single "five to try" post
def get_post(url,yelp_api_key):

    # initialize empty dataframe to hold output for this post:
    # rows = unique recommended restaurants in the post
    # columns = restaurant/recommendation characteristics
    post_df = pd.DataFrame()

    # get the date when the given page was originally published from the url
    post_date = datetime.datetime.strptime(' '.join(url.split('/')[3:6]),'%Y %m %d')
    post_year = post_date.year
    post_month= post_date.month

    # get the page html
    resp = requests.get(url)
    resp_text = resp.text

    # parse html
    soup = BeautifulSoup(resp_text, 'html.parser')
        
    # get the unique recommendations in this post      
    rec_pgps = soup.find_all('p')
    
    for pgp in rec_pgps:
        if pgp.get('id') is not None and len(pgp.find_all('strong')) != 0:
            # try to get recommendation name
            try:
                rec_name = pgp.find_all('strong')[1].string.strip()
            except:
                rec_name = ''
                    
            # try to get recommendation address       
            try:
                rec_address = pgp.find_all('em')[-1].string.split('\u2014')[0].split(',')[0].replace('.','').strip()
            except:
                rec_address = ''
            
            # try to get recommender
            try:
                rec_giver = pgp.find_all('em')[-1].string.split('\u2014')[1].split(',')[0].strip()
            except:
                rec_giver  = ''
    
            # try to get rec date from sibling header element
            rec_date = ''
            try:
                siblings = pgp.previous_siblings
                for sib in siblings:
                    if rec_date == '':
                        if sib.name == 'h2' or sib.name == 'h3':
                            month_str = sib.string.split(' ')[0]
                            day_str = sib.string.split(' ')[1].replace(',','')
                            year_str = str(post_year)
                            dt = datetime.datetime.strptime(month_str + ' ' + day_str + ' ' + year_str,'%B %d %Y')
                            
                            # if entry was published in "new" year wrt. original publication date
                            if dt.month < post_month:
                                dt = datetime.datetime.strptime(month_str + ' ' + day_str + ' ' + str(int(year_str)+1),'%B %d %Y')
                            
                            rec_date = dt
            except:
                rec_date = ''
    
            # get price, rating, cuisine, and geolocation information from yelp 
            if len(rec_name)>0 and len(rec_address)>0:
                
                yelp_data = get_yelp(rec_name,rec_address,yelp_api_key)
                
                # if we were able to get decent data, add it to the result df
                if yelp_data[0] != '' or yelp_data[2] != '' or not np.isnan(yelp_data[1]) or not np.isnan(yelp_data[3]) or not np.isnan(yelp_data[4]):
                    rec_df = pd.DataFrame({'name':rec_name,'location_str':rec_address,
                                           'latitude':yelp_data[3],'longitude':yelp_data[4],
                                           'price':yelp_data[0],'rating':yelp_data[1],
                                           'cuisine':yelp_data[2],'recommender':rec_giver,
                                           'date':rec_date,},index = [0])
                    post_df = post_df.append(rec_df)
    
    return post_df

# function to get all of the eater ny "five to try" posts
def get_ftt(url,yelp_api_key):

    ftt_df = pd.DataFrame()
    
    # get page html
    resp = requests.get(url)
    resp_text = resp.text
    
    # parse html
    soup = BeautifulSoup(resp_text,'html.parser')
    
    # get the posts associated with seasonal "five to try" lists
    anchors = soup.find_all('a',{'class':'c-entry-box--compact__image-wrapper'})
    
    # get post-level data
    for anchor in anchors:
        post_url = anchor.get('href')
        post_df = get_post(post_url,yelp_api_key)
        ftt_df = ftt_df.append(post_df)
        
    ftt_df = ftt_df.reset_index(drop=True)
    
    return ftt_df

###

url = 'https://ny.eater.com/things-to-do-nyc'
api_key = 'your_yelp_api_key'

ftt_df = get_ftt(url,api_key)

# clean up a few small typos in the recommender names
ftt_df.loc[ftt_df['recommender'] == 'Robert Siestema','recommender'] = 'Robert Sietsema'
ftt_df.loc[ftt_df['recommender'] == 'SD','recommender'] = 'Serena Dai'
ftt_df.loc[ftt_df['recommender'] == '','recommender'] = 'N/A'

# get neighborhood information for recommended restaurants using mapbox api
def get_neighborhood(mb_api_key,latitude,longitude):
    
    url = 'https://api.mapbox.com/geocoding/v5/mapbox.places/' + str(longitude) + ',' + str(latitude) + '.json?types=neighborhood&access_token=' + mb_api_key
    neighborhood_resp = requests.get(url)
    neighborhood_json = json.loads(neighborhood_resp.text)
    neighborhood = neighborhood_json['features'][0]['text']
    
    return neighborhood

# use the mapbox api (free for small numbers of api calls)
mb_api_key = 'your_mapbox_api_key'

ftt_df['neighborhood'] = ftt_df.apply(lambda row: get_neighborhood(mb_api_key,row['latitude'], row['longitude']), axis=1)

# save recommendation data
ftt_df.to_csv('data/recommendations.csv',index=False)
