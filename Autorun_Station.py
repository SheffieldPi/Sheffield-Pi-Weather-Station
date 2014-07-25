#!/usr/bin/env python
#These are the imports needed to get the data from the sensor.
import time
import Adafruit_BMP.BMP085 as BMP085

#These access the WOW site to upload data
import urllib
import urllib2

#Import the plot.ly data
import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import *

#Import the config data
from ConfigParser import SafeConfigParser
import sys

def tempfarenheit(Temperature):
    #WOW requires the temperature to be uploaded in Farenheit, so this will convert our values from Celcius
    Temp = (float(Temperature)*9/5)+32
    return Temp

def presinches(pressure):
    #WOW requires the pressure to be uploaded in inches of mercury, so this will convert our values from Pascals
    Pres = float(pressure) * 0.000295333727
    return Pres

def Timeformatting(aTime):
    #returns the time in both normal format and WOW format
    Timenow = time.strftime('%Y-%m-%d %H:%M:%S',aTime)
    Timeformat = Timenow.replace(':','%3A').replace(' ','+')
    return Timeformat,Timenow

def Plotter():
    trace1 = Scatter(
    x=[],
    y=[],
    name = 'Temperature Readings *C',
    stream = Stream(token = Stream_ID,
        maxpoints=80)
    )
    trace2 = Scatter(
    x=[],
    y=[],
    name = 'Pressure Readings Pa',
    yaxis = 'y2',
    stream = Stream(token = Stream_ID_2,
        maxpoints=80)
    )
    my_data = Data([trace1, trace2])
    my_layout = Layout(
        title='Temperature Readings from SheffieldPiStation',
        xaxis={'title':'Date and Time, GMT'},
        yaxis=YAxis(title='Temperature, *C',
                    range = [23,25]
        ),
        yaxis2=YAxis(
            title = 'Pressure, Pa',
            range = [100500,100600],
            titlefont={'color':'rgb(148,103,189'},
            tickfont=Font(
                color='rgb(148,103,189)'
            ),
            side = 'right',
            overlaying = 'y'
        )
    )
    my_fig = Figure(data = my_data,layout = my_layout)
    unique_url = py.plot(my_fig,filename='Weather Data from the Pi Weather Station',auto_open=False,fileopt='extend')
    s = py.Stream(Stream_ID)
    q = py.Stream(Stream_ID_2)
    return s,q

#This checks the user details
parser = SafeConfigParser()
parser.read('home/pi/Sheffield-Pi-Weather-Station/details.ini')

#This assigns the values to a format that the code can now access
AWSKey = parser.get('MetWOW','aws_key')
SiteID = parser.get('MetWOW','site_id')
APIKey = parser.get('Plotly','api_key')
Stream_ID = parser.get('Plotly','stream_id')
Username = parser.get('Plotly','username')
try:
    Stream_ID_2 = parser.get('Plotly','stream_id_2')
except:
    pass

sensor = BMP085.BMP085()
softwaretype = "Sheffield-Pi-Weather-Station-0.1"
frequency = 900

#These format the plot.ly graph and login to the site
py.sign_in(Username,APIKey)
s,q = Plotter()
s.open()
q.open()

while True:
    #Read the data
    temp= format(sensor.read_temperature())
    pressure = format(sensor.read_pressure())
    [Timeformat,Timenow] = Timeformatting(time.gmtime())
    
    #Get the data in the right units to upload
    Temp = tempfarenheit(temp)
    Pres = presinches(pressure) 

    #Construct the URL to send the data to WOW
    url = 'http://wow.metoffice.gov.uk/automaticreading?siteid=%s&siteAuthenticationKey=%s&dateutc=%s&tempf=%s&baromin=%.2f&softwaretype=%s' % (SiteID,AWSKey,Timeformat,Temp,Pres,softwaretype)

    #Send the request to WOW
    request = urllib2.Request(url)
    response = urllib2.urlopen(request).getcode()

    #Open the Plot.ly temperature stream (s) and write the values to be uploaded
    s.write(dict(x=Timenow,y=temp))
    q.write(dict(x=Timenow,y=pressure))

    #Write the values to a saved file and then close that file
    f = open("data.txt",'a')
    f.write('%s %7s *C %14s Pa\n %26s *F %13.2f inch Hg\n' % (Timenow,temp,pressure,Temp,Pres))
    f.close

    #Wait for the required time period before repeating
    try:
        time.sleep(frequency)
    except:
        s.close()
        q.close()
        break
