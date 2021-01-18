from ff_news import *


# create instance with default values
# the downloaded news information will be stored in a news sub folder
# if the folder does not exit it will be created
news = Check_News(url='http://cdn-nfs.faireconomy.media/ff_calendar_thisweek.xml', 
                        update_in_minutes=240, 
                        minutes_before_news=480, 
                        minutes_after_news = 60)

# check for news for a currency
currency_result = news.check_currency(currency='EUR')
print(currency_result)
print('')

# check for news for an instrument
instrument_result = news.check_instrument(instrument='EURUSD')
print(instrument_result)
print('')

# get the next x news items
news_items = news.get_next_x_news_items(5)
print(news_items)
print('')
