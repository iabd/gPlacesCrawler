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

    def getCommunes(self):
        import ssl, urllib, json, pandas as pd
        from bs4 import BeautifulSoup
        ssl._create_default_https_context=ssl._create_unverified_context
        page=urllib.request.urlopen('https://en.wikipedia.org/wiki/Alphabetical_list_of_comunes_of_Italy') 
        soup=BeautifulSoup(page)                                                        
        communesData=[]                                                                 
        for li_tag in soup.find_all('div', {'class':'div-col columns column-width'}):
            for list_tag in li_tag.find_all('li'):
                commune = list_tag.find('a').text
                communesData.append(commune)

        print('Fetched the list of communes! trying to get coordinates..')
        communesData=communesData[4:]
        cords=[]
        for commune in communesData:
            try:
                from urllib.parse import quote_plus
                commune = quote_plus(commune)
                print("\r{}".format(commune), end="")
                url = ('https://maps.googleapis.com/maps/api/geocode/json?address=%s&region=%s&key=%s') % (commune, self.country, self.key)
                #print(url)
                response = urllib.request.urlopen(url).read()
                jsonResponse = json.loads(response.decode('latin'))
                c = pd.DataFrame(jsonResponse['results'])
                cord = str(c.geometry[0]['location']['lat']) + ','+str(c.geometry[0]['location']['lng'])
                cords.append(cord)
            except Exception as e:
                print(e)

        self.Communes=pd.DataFrame({'locs':communesData, 'cods':cords})
        return cords
    

    def getCities(self):
        ssl._create_default_https_context = ssl._create_unverified_context
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
        listCities = cityData[cityData.columns[1:2]]
        listCities = listCities.drop(0, axis=0)
        listCities = listCities[1]
        print('Fetched the cities! Trying to get coordinates..')
        gn = geocoders.GeoNames(username='abdw')
        cords = []
        cord = 'NA'
        for cities in listCities:
            try:
 #               print('Getting coordinates for "\r{} out of "\r{} cities..'.format (listCities.index[cities], len(listCities)), end='')
                city = gn.geocode(cities)
                cord = str(city.latitude) + ',' + str(city.longitude)
            except Exception as e:
                print(e)
                break
            cords.append(cord)
        self.Cities = pd.DataFrame({'locs': listCities,'cods': cords})
        #print(self.Cities)
        return cords

    def fetchPlaces(self, location):
        import urllib, json
        import ssl
        import urllib
        from bs4 import BeautifulSoup
        import pandas as pd
        from geopy import geocoders
        import time
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

    
        
        
