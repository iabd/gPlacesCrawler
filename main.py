import pdb
import crawler
import pandas as pd
import requests
import pprint
import urllib
import json
import os
from geopy import geocoders
from bs4 import BeautifulSoup
import functools
from copy import deepcopy
import urllib.request
import json
import ssl
key = "AIzaSyASmGMElEZthlsMGEN-p3Nw1NInctWoXTk"
types="restaurant"
radius="1000"
fields="name, formatted_address,rating"
inputString="pizzeria"

crawl=crawler.crawler(types=types, inputString=inputString,radius=radius,key=key)

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
        getattr(crawl, 'get{}'.format(wid))()
        locDF=getattr(crawl, wid)
        locDF.to_csv('italy{}.csv'.format(wid), index=False)
        print('Location fetched and saved as italy{}.csv. Time to crawl!'.format(wid))

    locationList=locDF.cods
    firstTime=True
    if os.path.exists('crawl{}.csv'.format(wid)):
        print('Locations acquired from {} already exist, and saved as crawl{}.csv Loading data..'.format(wid, wid))
    else:
        print('Crawling for {} started.'.format(wid))
        for idx, location in enumerate(locationList):
            tempData=crawl.fetchPlaces(location)
            print("'\r{} \  {}".format(idx, len(locDF)), end='')
            if firstTime:
                tempCSV=tempData
                firstTime=False
            else:
                tempCSV=tempCSV.append(tempData)
        tempCSV.to_csv('crawl{}.csv'.format(wid), index=False)
        print('crawl file saved as crawl{}.csv successfully!'.format(wid))
 
if choices[int(option)]:
    print('initiating...')
    initiate(choices[int(option)])
else:
    print('Invalid response! Exiting...')

    
        
