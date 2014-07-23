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

def TemPlot():
    my_stream = Stream(token = Stream_ID,
                       maxpoints=80)
    my_data = Data([Scatter(x=[],
                            y=[],
                            mode = 'lines+markers',
                            stream = my_stream,
                            name = 'Temperature Readings *C')])
    my_layout = Layout(title='Temperature Readings from SheffieldPiStation',
                        xaxis={'title':'Date and Time, GMT'},
                        yaxis={'title':'Temperature, *C'})
    my_fig = Figure(data = my_data,layout = my_layout)
    unique_url = py.plot(my_fig,filename='Temperature Data from the Pi Weather Station',auto_open=False)
    s = py.Stream(Stream_ID)
    return s

def PresPlot():
    my_stream = Stream(token = Stream_ID_2,
                       maxpoints=80)
    my_data = Data([Scatter(x=[],
                            y=[],
                            mode = 'lines+markers',
                            stream = my_stream,
                            name = 'Pressure Readings Pa')])
    my_layout = Layout(title='Pressure Readings from SheffieldPiStation',
                        xaxis={'title':'Date and Time, GMT'},
                        yaxis={'title':'Pressure, Pa'})
    my_fig = Figure(data = my_data,layout = my_layout)
    unique_url = py.plot(my_fig,filename='Pressure Data from the Pi Weather Station',auto_open=False)
    q = py.Stream(Stream_ID_2)
    return q

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
s = TemPlot()
if Stream_ID_2:
    q = PresPlot()

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
    s.open()
    s.write(dict(x=Timenow,y=temp))
    s.close()

    #Open the Plot.ly pressure stream (q) and write the values to be uploaded
    if Stream_ID_2:
        q.open()
        q.write(dict(x=Timenow,y=pressure))
        q.close()

    #Write the values to a saved file and then close that file
    f = open("data.txt",'a')
    f.write('%s %7s *C %14s Pa\n %26s *F %13.2f inch Hg\n' % (Timenow,temp,pressure,Temp,Pres))
    f.close

    #Wait for the required time period before repeating
    try:
        time.sleep(frequency)
    except:
        break
