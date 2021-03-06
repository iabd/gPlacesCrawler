import pdb
import requests, pprint, json, urllib, os, functools, ssl, time
import pandas as pd
#from geopy import geocoders
from bs4 import BeautifulSoup
from copy import deepcopy
import ssl
import crawler
key = "AIzaSyASmGMElEZthlsMGEN-p3Nw1NInctWoXTk"
types="restaurant"
radius="1000"
fields="name,formatted_address,rating"
inputString="pizzeria"

crawl=crawler.crawler(types=types, inputString=inputString,radius=radius,key=key)
dataOfInterest={"name", "geometry", "place_id", "rating", "types", "vicinity", "reviews"}
manual = """
Hello!
Press 1 for crawling cities. [There are 144 cities in Italy]
Press 2 for crawling communes. [TIME CONSUMING!!! There are 8100 communes in Italy]
Default: Exit!
"""
choices=[None, 'Cities', 'Communes']
option=input(manual)

def initiate(wid):
    if os.path.exists('italy{}.csv'.format(wid)):
        print('File containing the names and coordinates of {} already exists. Loading..'.format(wid))
        locDF=pd.read_csv('italy{}.csv'.format(wid))
        print('Loaded successfully!')
    else:
        print('Fetching the list of {} and thier coordinates.'.format(wid))
        crawl.getLocations(wid)
       # pdb.set_trace()
        locDF=getattr(crawl, wid)
        locDF.to_csv('italy{}.csv'.format(wid), index=False)
        print('Location fetched and saved as italy{}.csv. Time to crawl!'.format(wid))

    locationList=list(locDF.cods)
    firstTime=True
    if os.path.exists('crawl{}.csv'.format(wid)):
        print('Locations acquired from {} already exist, and saved as crawl{}.csv Loading data..'.format(wid, wid))
        #data=pd.read_csv('crawl{}.csv'.format(wid))
    else:
        print('Crawling for {} started.'.format(wid))
        for idx, location in enumerate(locationList):
            tempData=crawl.getPlaces(location)
            #time.sleep(0.5)
            print("'\r{} \  {}".format(idx, len(locDF)), end='')
            if firstTime:
                tempCSV=tempData
                firstTime=False
            else:
                tempCSV=tempCSV.append(tempData)
        #    pdb.set_trace()
       # breakpoint()
        tempCSV.to_csv('crawl{}.csv'.format(wid), index=False)
        print('\nCrawl file saved as crawl{}.csv successfully!'.format(wid))
 
if choices[int(option)]:
    print('initiating...')
    initiate(choices[int(option)])
    df=pd.read_csv('crawl{}.csv'.format(choices[int(option)]))
else:
    print('Invalid response! Exiting...')
    sys.exit(0)

if os.path.exists('cleanedData.csv'):
    print('Cleaned data already exists. Loading and proceeding')
    cleanedData=pd.read_csv('cleanedData.csv')
else:
    print('Cleaning Data')
    cleanedData=crawl.cleanData(df, dataOfInterest)
    cleaned.to_csv('cleanedData.csv', index=False)
    print("data cleaned and saved as 'cleanedData.csv'")

#pdb.set_trace()
cleanedData['reviewers']="NA"
fields2="name,rating,reviews"
reviewersList=crawl.getReviewers(cleanedData.place_id, fields2, key)
#pdb.set_trace()
for idx, value in enumerate(reviewersList):
    cleanedData.reviewers[idx]=value
    cleanedData.to_csv('brokenFinalData.csv', index=False)
cleanedData.to_csv('finalData.csv', index=False)
