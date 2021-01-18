
from dateutil.parser import *
from dateutil.relativedelta import *
from datetime import *
import requests
import xml.etree.ElementTree as ET
import os

class Check_News():

    def __init__(self,
                 url: str = 'http://cdn-nfs.faireconomy.media/ff_calendar_thisweek.xml',
                 update_in_minutes: int = 240,
                 minutes_before_news: int = 480,
                 minutes_after_news: int = 60,
                 gmt_offset: int = 2):

        """
        Class for checking Forex Factory(FF) news calendar.
            Args:
                url: url string for downloading news calendar from
                update_in_minutes: update interval for retrieving news calendar from FF, every 4 hours isOK
                minutes_before news: start of time window before news happens
                minutes_after_news: end of time window after news happened

            Remarks:
                The FF calendar will be saved in an XML file in subfolder ./News/       !!! take care
                If ./News does not exists, it will be created
        """
        self.url = url
        self.update_in_minutes = update_in_minutes
        self.minutes_before_news = minutes_before_news
        self.minutes_after_news = minutes_after_news
        self.lastUpdate = datetime.now()
        self.base_date = 0
        self.quote_date = 0
        self.currency_date = 0
        self.titles = []
        self.countries = []
        self.dates = []
        self.times = []
        self.impacts = []
        self.news_items = []
        self.gmt_offset = gmt_offset
        self.retrieveUrl()

    # this routine will be called internally
    def retrieveUrl(self):

        # check if news directory exists
        isdir = os.path.isdir('./News')  
        if (isdir == False):
            os.makedirs('./News')
        
        myfile = requests.get(self.url)
        xmlFile = './News/news_' + str(self.lastUpdate.day) + '.xml'
        open(xmlFile, 'wb').write(myfile.content)

        self.titles.clear()
        self.countries.clear()
        self.dates.clear()
        self.times.clear()
        self.impacts.clear()
        self.news_items.clear()

        tree = ET.parse(xmlFile)
        root = tree.getroot()
        for text in root.iter('title'):
            self.titles.append(text.text)
        for text in root.iter('country'):
            self.countries.append(text.text)
        for text in root.iter('date'):
            self.dates.append(text.text)
        for text in root.iter('time'):
            self.times.append(text.text)
        for text in root.iter('impact'):
            self.impacts.append(text.text)

        for index in range(0, len(self.titles), 1):
            # make date first
            date = parse(self.dates[index] + ' ' + self.times[index])
            date = date - relativedelta(hours=-self.gmt_offset)
            self.news_items.append((self.countries[index], date, self.titles[index], self.impacts[index]))

        self.lastUpdate = datetime.now()

    def check_currency(self,
                        currency: str = 'EUR'):
        
        """
            Check comming news for a currency.

            Args:
                currency:   currency name to check for
                            AUD|CAD|CHF|EUR|GBP|JPY|NZD|USD
            Returns:
                bool: True(if news in defined periode), else False
                title: description of news item
                impact: news impact on currency (high, medium or low)
        """
        # check for updating the calendar`
        diff = datetime.now() - self.lastUpdate
        diff = diff.total_seconds()
        if (diff > self.update_in_minutes*60):
            self.retrieveUrl()
        
        for index in range (0, len(self.news_items), 1):
            if (self.news_items[index][0] == currency):
                # check time 
                if (datetime.now().timestamp() > (self.news_items[index][1].timestamp() - self.minutes_before_news * 60)\
                        and datetime.now().timestamp() < (self.news_items[index][1].timestamp() + self.minutes_after_news*60)):
                    self.currency_date = self.news_items[index][1].timestamp() - self.minutes_before_news * 60
                    return True, str(self.news_items[index][2]), str(self.news_items[index][3])
        
        return False, '', ''

    def check_instrument(self,
                            instrument: str = 'EURUSD'):
        """
            Check comming news for an instrument.

            Args:
                instrument: instrument name to check for
                            28 basic instruments
            Returns:
                bool: True(if news in defined period), else False
                title: description of news item
                impact: news impact on currency (high, medium or low)
        """
        # check for updating the calendar`
        diff = datetime.now() - self.lastUpdate
        diff = diff.total_seconds()
        if (diff > self.update_in_minutes*60):
            self.retrieveUrl()

        # split instrument in the two currencies
        if (len(instrument) < 6):
            return False, '', ''
        if (len(instrument) > 6):
            instrument = instrument[0:6]

        currency_1 = instrument[0:3]
        currency_2 = instrument[3:6]

        result_1, title_1, impact_1 = self.check_currency((currency_1))
        self.base_date = self.currency_date
        result_2, title_2, impact_2 = self.check_currency((currency_2))
        self.quote_date = self.currency_date
        if (result_1 == False and result_2 == False):
            return False, '', '' 

        if (result_1 == True and result_2 == False):
            return result_1, title_1, impact_1
            
        if (result_1 == False and result_2 == True):
            return result_2, title_2, impact_2

        if (result_1 == True and result_2 == True):
            if (impact_1 == 'High' and (impact_2 == 'Low' or impact_2 == 'Medium' or impact_2 == 'Holiday')):
                return True, title_1, impact_1
            if (impact_1 == 'Medìum' and (impact_2 == 'Low' or impact_2 == 'Holiday')):
                return True, title_1, impact_1
            if (impact_2 == 'High' and (impact_1 == 'Low' or impact_1 == 'Medium' or impact_1 == 'Holiday')):
                return True, title_2, impact_2
            if (impact_2 == 'Medium' and (impact_1 == 'Low' or impact_1 == 'Holiday')):
                return True, title_2, impact_2
            if ((self.base_date < self.quote_date) and impact_1 != 'Holiday' and impact_1 != 'Holiday'):
                return True, title_1, impact_1
            else:
                return True, title_2, impact_2

        return False, '', ''
    
    def get_next_x_news_items(self,
                                number_of_items: int = 5) -> dict:

        self.number_of_items = number_of_items
        if(self.number_of_items > 10): self.number_of_items = 10
        
        """
            Create dictionary with next x news items.

            Args:
                number_of_items: number of items to retrieve, limited to 10

            Returns:
                dictionary: last x news items, format 'index': ['country', 'date', 'title', 'impact']
                                                        index '0' --> 'number_of_items'
        """
        # check for updating the calendar`
        diff = datetime.now() - self.lastUpdate
        diff = diff.total_seconds()
        if (diff > self.update_in_minutes*60):
            self.retrieveUrl()

        # loop through news_items list
        news_items = {}
        _date = datetime.now()
        counter = 0
        for index in range (0, len(self.news_items)-1, 1):
            if (counter >= self.number_of_items): break
            if (self.news_items[index][1] > _date):
                news_items[str(counter)+':'] = [str(self.news_items[index][0]), str(self.news_items[index][1]), str(self.news_items[index][2]), str(self.news_items[index][3])]
                counter = counter + 1

        return news_items

