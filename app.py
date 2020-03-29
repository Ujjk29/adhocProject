from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_simple_geoip import SimpleGeoIP
from urllib import request as rs
from textblob import TextBlob
from geopy.geocoders import Nominatim
from geoip import geolite2
from serpapi.google_search_results import GoogleSearchResults
from bs4 import BeautifulSoup
from ip2geotools.databases.noncommercial import DbIpCity
import json
import sys
import re
import tweepy
import COVID19Py
import covid19_data


app = Flask(__name__)


#### web-scrapping
url = 'https://en.wikipedia.org/wiki/Machine_learning'
htmldata = rs.urlopen(url)
soup = BeautifulSoup(htmldata, 'html.parser')
###end of scrapping


#######geolocation
geolocator = Nominatim(user_agent="app")
#########


#######covidpy lib
covid19 = COVID19Py.COVID19()


#####twitter api
consumer_key = "NnXZ9s4iZJAyx4kAwUN56tyaa"
consumer_sec = "AqvqkEkqLP2xRlgs6mhv2ByiHfX8HDIk10sSNmlAX7V6yO2sVN"
# access details
access_key = "207914472-wyE27bRbnqiGtHmTDprlki2NC3hJJYoU5OehxN4o"
access_sec = "iuG8VwxulyHQUPl9y5GS9gLVN72lirk8h26rOfzTqgSIV"

first_auth = tweepy.OAuthHandler(consumer_key, consumer_sec)
first_auth.set_access_token(access_key, access_sec)

storage_api_connect = tweepy.API(first_auth)

# class CustomStreamListener(tweepy.StreamListener):
#     def on_error(self, status_code):
#         print >> sys.stderr, 'Encountered error with status code:', status_code
#         return True # Don't kill the stream

#     def on_timeout(self):
#         print >> sys.stderr, 'Timeout...'
#         return True # Don't kill the stream
############end twitter

#################
# def getplace(lat, lon):
#     url = "http://maps.googleapis.com/maps/api/geocode/json?"
#     url += "latlng=%s,%s&sensor=false" % (lat, lon)
#     v = rs.urlopen(url).read()
#     j = json.loads(v)
#     components = j['results'][0]['address_components']
#     country = town = None
#     for c in components:
#         if "country" in c['types']:
#             country = c['long_name']
#         if "postal_town" in c['types']:
#             town = c['long_name']
#     return town, country
#################


@app.route('/')
def index():    
    return render_template('index.html')


@app.route('/main/', methods=['POST','GET'])
def main():
    if request.method == 'POST':
        name = request.form['g_name']
        location = request.form['g_loc']
        # ip_addr = request.form['g_ip']
                
        head = soup.find('h3').text

        if all(x.isalpha() or x.isspace() for x in location):
            #######geolocation
            locat = geolocator.geocode(location)
            lat = locat.latitude
            lon = locat.longitude
            address1 = geolocator.reverse(str(lat)+","+str(lon))
            address2 = address1.raw["address"]
            country = address2["country"]
            try:
                city = address2["city"]
            except:
                city = country

            
            box = address1.raw["boundingbox"];        
            covid_data_country = covid19_data.dataByName(country)
            #######end

        ########using coordinates
        else:
            locat= location.split(",")
            lon = locat[0]
            lat = locat[1]
            address1 = geolocator.reverse(location)
            address2 = address1.raw["address"]
            city = address2["city"]
            country = address2["country"]  
            box = address1.raw["boundingbox"];      
            covid_data_country = covid19_data.dataByName(country)
        ###############    

        # if ip_addr:
        #     match = geolite2.lookup(ip_addr)
        #     country = match.country
        #     city = country
        #     locat = geolocator.geocode(str(country))
        #     lat = locat.latitude
        #     lon = locat.longitude
        #     covid_data_country = covid19_data.dataByName(country)
    
        
        ########################twitter sentiment analysis######################################

        def clean_tweet(tweet):
            return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


        def get_tweet_sentiment( tweet):
            # create TextBlob object of passed tweet text
            analysis = TextBlob(clean_tweet(tweet))
            # set sentiment
            if analysis.sentiment.polarity > 0:
                return 'positive'
            elif analysis.sentiment.polarity == 0:
                return 'neutral'
            else:
                return 'negative'


        # empty list to store parsed tweets
        
        search_data=["corona "+city]
        tweets = []
        # sapi = tweepy.streaming.Stream(first_auth, CustomStreamListener())    
        # sapi.filter(locations= [float(box[0]),float(box[1]),float(box[2]),float(box[3])])
        
        fetched_tweets = tweepy.Cursor(storage_api_connect.search,q=search_data[0]+"  -filter:retweets",lang='en',result_type='recent').items(10)
        for tweet in fetched_tweets:            
            parsed_tweet = {}
            parsed_tweet['text'] = tweet.text
            # saving sentiment of tweet
            parsed_tweet['sentiment'] = get_tweet_sentiment(tweet.text)
            if tweet.retweet_count > 0:
                if parsed_tweet not in tweets:
                    tweets.append(parsed_tweet)
            else:
                tweets.append(parsed_tweet)
                            
        # twe = tweepy.Cursor(storage_api_connect.search,q=search_data[0]+"  -filter:retweets",lang='en',result_type='recent').items(10)
        ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
        ptweetper = 100*len(ptweets)/len(tweets)
        ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
        ntweetper = 100*len(ntweets)/len(tweets)
        neutper = 100-(ptweetper + ntweetper)


        #####################################   Hospitals     ##################################################
        htweets = []
        hfetched_tweets = tweepy.Cursor(storage_api_connect.search,q="hospital "+city+"  -filter:retweets",lang='en',result_type='recent').items(10)
        for htweet in hfetched_tweets:            
            hparsed_tweet = {}
            hparsed_tweet['text'] = htweet.text
            # saving sentiment of tweet
            hparsed_tweet['sentiment'] = get_tweet_sentiment(htweet.text)
            if htweet.retweet_count > 0:
                if hparsed_tweet not in htweets:
                    htweets.append(hparsed_tweet)
            else:
                htweets.append(hparsed_tweet)
                         
        phtweets = [htweet for htweet in htweets if htweet['sentiment'] == 'positive']
        phtweetper = 100*len(phtweets)/len(htweets)
        nhtweets = [htweet for htweet in htweets if htweet['sentiment'] == 'negative']
        nhtweetper = 100*len(nhtweets)/len(htweets)
        hneutper = 100-(phtweetper + nhtweetper)

        #google maps scraping
        params = {
        "engine": "google_maps",
        "q": "shop",
        "google_domain": "google.com",
        "type": "search",
        "ll": "@"+str(lat)+","+str(lon)+",15z",}

        client = GoogleSearchResults(params)
        data = client.get_dict()

        
        # for result in data['local_results']:
            

        #####################################   end
        #####################################   Restaurants     ##################################################
        rtweets = []
        rfetched_tweets = tweepy.Cursor(storage_api_connect.search,q="restaurant "+city+"  -filter:retweets",lang='en',result_type='recent').items(10)
        for rtweet in rfetched_tweets:            
            rparsed_tweet = {}
            rparsed_tweet['text'] = rtweet.text
            # saving sentiment of tweet
            rparsed_tweet['sentiment'] = get_tweet_sentiment(rtweet.text)
            if rtweet.retweet_count > 0:
                if rparsed_tweet not in rtweets:
                    rtweets.append(rparsed_tweet)
            else:
                rtweets.append(rparsed_tweet)
                         
        prtweets = [rtweet for rtweet in rtweets if rtweet['sentiment'] == 'positive']
        prtweetper = 100*len(prtweets)/len(rtweets)
        nrtweets = [rtweet for rtweet in rtweets if rtweet['sentiment'] == 'negative']
        nrtweetper = 100*len(nrtweets)/len(rtweets)
        rneutper = 100-(prtweetper + nrtweetper)
        #####################################   end
        #####################################   shops     ##################################################
        stweets = []
        sfetched_tweets = tweepy.Cursor(storage_api_connect.search,q="shop "+city+"  -filter:retweets",lang='en',result_type='recent').items(10)
        for stweet in sfetched_tweets:            
            sparsed_tweet = {}
            sparsed_tweet['text'] = stweet.text
            # saving sentiment of tweet
            sparsed_tweet['sentiment'] = get_tweet_sentiment(stweet.text)
            if stweet.retweet_count > 0:
                if sparsed_tweet not in stweets:
                    stweets.append(sparsed_tweet)
            else:
                stweets.append(sparsed_tweet)
                         
        pstweets = [stweet for stweet in stweets if stweet['sentiment'] == 'positive']
        pstweetper = 100*len(pstweets)/len(stweets)
        nstweets = [stweet for stweet in stweets if stweet['sentiment'] == 'negative']
        nstweetper = 100*len(nstweets)/len(stweets)
        sneutper = 100-(pstweetper + nstweetper)
        #####################################   end

        return render_template('result.html',**locals() )

    else:        
        return render_template('main.html')


            

if __name__ == "__main__":
    app.run(debug=True)   



