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
import ConfigParser
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

def plotpressure():
    while True:
        check = raw_input("would you like to stream pressure to Plot.ly? y/n: ")
        if check == "y":
            value = raw_input('What is your %s?  ' %name)
            parser.set(section,name,value)
            return
        elif check == "n":
            Stream_ID_2 = False
            return Stream_ID_2
        else:
            print "Sorry, invalid input."
            plotpressure();
            return
            
def addvalue():
    #This is in case the login values have not been added already
    if name == "stream_id_2":
        Stream_ID_2 = plotpressure()
        return Stream_ID_2
    else:
        value = raw_input('What is your %s?  ' %name)
        parser.set(section,name,value)

def TemPlot():
    #Formats the temperature Plot.ly graph
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
    #Formats the pressure Plot.ly graph
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

#This checks that user details exist and prompts for them if not
parser = ConfigParser.SafeConfigParser(allow_no_value=True)
parser.read('details.ini')

for section in [ 'MetWOW', 'Plotly' ]:
    for name,value in parser.items(section):
        if value:
            Stream_ID_2 = True
            continue
        else:
            Stream_ID_2 = addvalue()

#This writes the inputted values (if any) to the file
parser.write(open('details.ini','w'))

#This assigns the values to a format that the code can now access
AWSKey = parser.get('MetWOW','aws_key')
SiteID = parser.get('MetWOW','site_id')
APIKey = parser.get('Plotly','api_key')
Stream_ID = parser.get('Plotly','stream_id')
Username = parser.get('Plotly','username')
if Stream_ID_2 != False:
    Stream_ID_2 = parser.get('Plotly','stream_id_2')

sensor = BMP085.BMP085()
X = 0
softwaretype = "Sheffield-Pi-Weather-Station-0.1"
n = raw_input("Would you like to stop after a certain amount of readings? If so, type the amount. If not, type 'n': ")
if float(n)>1 or n == "n":
	frequency = input('What time period between readings (in seconds) would you like: ')

#Use the functions to format the plot.ly graph and login to the site
py.sign_in(Username,APIKey)
s = TemPlot()
if Stream_ID_2:
    q = PresPlot()

print "Press ctrl-C at any time to cancel the process"

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

    #Send the request to WOW and interpret response
    request = urllib2.Request(url)
    response = urllib2.urlopen(request).getcode()
    if float(response) == 200:
        print "Connection is ok, data has been uploaded to Weather Observations Website %s" % SiteID
    else:
        print "Error connecting to WOW site. Data was not uploaded at this time."

    #Open the Plot.ly temperature stream (s) and write the values to be uploaded
    s.open()
    s.write(dict(x=Timenow,y=temp))
    s.close()

    #Open the Plot.ly pressure stream (q) and write the values to be uploaded if there is a stream ID
    if Stream_ID_2:
        q.open()
        q.write(dict(x=Timenow,y=pressure))
        q.close()

    #Write the values to a saved file and then close that file
    f = open("data.txt",'a')
    f.write('%s %7s *C %14s Pa\n %26s *F %13.2f inch Hg\n' % (Timenow,temp,pressure,Temp,Pres))
    f.close
    
    #Prepare the code to run indefinitely or until required number of readings is reached
    if n != "n":
            X += 1
            if X >= float(n):
                break

    #Wait for the required time period before repeating
    try:
        time.sleep(frequency)
    except:
        print "Process was terminated"
        break

