import requests, pprint, json, urllib, os, functools, ssl, time
import pandas as pd
class crawler:
    Cities=[]
    places=[]
    Communes=[]
    
    def __init__(self, types, inputString, radius, key):
        self.types=types
        self.inputString=inputString
        self.radius=radius
        self.key=key
        self.country='it'

    def getCords(locationData):
        "Get the list of geographical coordinates from the name of given location"
        for loc in locationData:
            try:
                from urllib.parse import quote_plus
                loc = quote_plus(loc)
                print("\r{}".format(loc), end="")
                url = ('https://maps.googleapis.com/maps/api/geocode/json?address=%s&region=%s&key=%s') % (loc, self.country, self.key)
                #print(url)
                response = urllib.request.urlopen(url).read()
                jsonResponse = json.loads(response.decode('latin'))
                c = pd.DataFrame(jsonResponse['results'])
                cord = str(c.geometry[0]['location']['lat']) + ','+str(c.geometry[0]['location']['lng'])
                cords.append(cord)
            except Exception as e:
                print(e)

        return cords

    

    def getLocations(self, locID):
        "Get teh list of cities/communes of Italy"
        ssl._create_default_https_context = ssl._create_unverified_context
        if locID=="Communes":
            ssl._create_default_https_context=ssl._create_unverified_context
            page=urllib.request.urlopen('https://en.wikipedia.org/wiki/Alphabetical_list_of_comunes_of_Italy') 
            soup=BeautifulSoup(page)                                                        
            locationData=[]                                                                 
            for li_tag in soup.find_all('div', {'class':'div-col columns column-width'}):
                for list_tag in li_tag.find_all('li'):
                    loc = list_tag.find('a').text
                    locationData.append(loc)

            print('Fetched the list of communes! trying to get coordinates..')
            locationData=locationData[4:]
            cords=getCords(locationData)
            self.Communes=pd.DataFrame({'locs':locationData, 'cods':cords})
        if locID=="Cities":
            page=urllib.request.urlopen('https://en.wikipedia.org/wiki/List_of_cities_in_Italy').read()
            soup = BeautifulSoup(page)
            citiesData = []
            table = soup.find('table', attrs={'class':'wikitable sortable'})
            table_body = table.find('tbody')
            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                citiesData.append([ele for ele in cols if ele])
            cityData = pd.DataFrame(data = citiesData)
            locationData = cityData[cityData.columns[1:2]]
            locationData = listCities.drop(0, axis=0)
            cords=getCords(locationData)
            self.Cities=pd.DataFrame({'locs':locationData, 'cods':cords})

        return cords

    def getPlaces(self, location):
        "Get the list of places eg. Pizzeria, Museums etc. from the given location"
    
        ssl._create_default_https_context = ssl._create_unverified_context
        url = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json'
                   '?location=%s'
                   '&radius=%s'
                   '&type=%s'
                   '&keyword=%s&key=%s') % (location,self.radius,self.types, self.inputString, self.key)
        response = urllib.request.urlopen(url).read()
        jsonResponse = json.loads(response.decode('utf-8'))
        x = pd.DataFrame(jsonResponse['results'])
        if 'next_page_token' in jsonResponse:
            tempVar=jsonResponse['next_page_token']
            url=('https://maps.googleapis.com/maps/api/place/nearbysearch/json'
               '?location=%s'
               '&radius=%s'
               '&type=%s'
               '&keyword=%s&key=%s&pagetoken=%s') % (location, self.radius, self.types,self.inputString, self.key, tempVar)
            time.sleep(2)
            response = urllib.request.urlopen(url).read()
            jsonResponse = json.loads(response.decode('utf-8'))
            y=pd.DataFrame(jsonResponse['results'])
            z=pd.concat([x, y], ignore_index=True)
            self.places=z
            return z

        return x

    def cleanData(self, dataFrame, dataOfInterest):
        toBeDeleted=[temp for temp in list(dataFrame.columns) if temp not in dataOfInterest]
        data=dataFrame.drop(toBeDeleted, axis=1)
        print('Deleted items not in dataOfInterest')
        print('Fixing geometry')
        data['cords'] = 'NA'
        print("cleaning data...")
        for index in range(len(data)):
            temp=data.geometry[index]
            temp=temp.replace("'", "\"")
            temp=json.loads(temp)
            #     print(temp)
            data.cords[index] = str('{0:.6f}'.format(temp['location']['lat'])) + ',' + str('{0:.6f}'.format(temp['location']['lng']))
            print("\r{} / {}".format(index, len(data)), end='')
        return data
        
    def getReviews(self, placeIDs, fields, key):
        "Get the details of the places"
        reviewersList=[]
        for idx, placeID in enumerate(placeIDs):
            print("\r{} / {}".format(idx, len(placeIDs)), end='')
            tempReviewers=[]
            url="https://maps.googleapis.com/maps/api/place/details/json?placeid={}&fields={}&key={}".format(placeID, fields, key)
            response = urllib.request.urlopen(url).read()
            jsonResponse = json.loads(response.decode('utf-8'))
            result = jsonResponse['result']
            try: 
                reviewersTemp=[temp['author_name'] for temp in result['reviews']]
                for temp in reviewersTemp:
                    tempReviewers.extend(temp.split())
                reviewersList.append(tempReviewers)
            except:
                reviewersList.append(['Mr. Hoodoo'])
        return reviewersList
        
