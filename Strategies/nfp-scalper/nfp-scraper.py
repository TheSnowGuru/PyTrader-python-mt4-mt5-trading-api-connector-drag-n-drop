#Library
import requests
from xml.dom import minidom
import json
import datetime

#Variables
URL = "https://www.cashbackforex.com/DesktopModules/Chart/HistoricalEventFigures.ashx"

#Settings
params = {'inst': '10351840', 'timezone': '12', 'vtl': '0', 'c': '1', 'vtr': '2', 'currency': 'USD', 'symbold': 'EURUSD'}
response = requests.get(URL, params = params)

dates = []
times = []
currencys = []
reportnames = []
impacts = []
actuals = []
forecasts = []
deviations = []
eventids = []
reportdatetimes = []

xml = minidom.parseString(response.content)

outfile = open('NFP_Events.csv', 'w')

for date in xml.getElementsByTagName('Date'):
    date = date.childNodes[0].data
    date = datetime.datetime.strptime(date, '%d %b %Y').strftime('%Y-%m-%d')
    dates.append(date)

for time in xml.getElementsByTagName('Time'):
    time = time.childNodes[0].data
    times.append(time)

for currency in xml.getElementsByTagName('Currency'):
    currency = currency.childNodes[0].data
    currencys.append(currency)

for reportname in xml.getElementsByTagName('ReportName'):
    reportname = reportname.childNodes[0].data
    reportnames.append(reportname)

for impact in xml.getElementsByTagName('Impact'):
    impact = impact.childNodes[0].data
    if impact == 'images/highimp.png':
       impact = 'High Impact'
       impacts.append(impact)

for actual in xml.getElementsByTagName('Actual'):
    actual = actual.childNodes[0].nodeValue
    actuals.append(actual)

for forecast in xml.getElementsByTagName('Forecast'):
    forecast = forecast.childNodes[0].nodeValue
    forecasts.append(forecast)

for deviation in xml.getElementsByTagName('Deviation'):
    deviation = deviation.childNodes[0].nodeValue
    deviations.append(deviation)

for reportdatetime in xml.getElementsByTagName('ReportDateTime'):
    reportdatetime = reportdatetime.childNodes[0].nodeValue
    reportdatetimes.append(reportdatetime)

for index in range(len(times)):
    time = times[index]
    date = dates[index]
    currency = currencys[index]
    reportname = reportnames[index]
    impact = impacts[index]
    actual = actuals[index]
    forecast = forecasts[index]
    deviation = deviations[index]

    outfile.write('{}, {}, {}, {}, {}, {}, {}, {}\n'.format(date, time, currency, reportname, impact, actual, forecast, deviation))

outfile.close()
