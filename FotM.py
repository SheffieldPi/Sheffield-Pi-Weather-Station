####THIS PROGRAM IS ONLY FOR THE FESTIVAL OF THE MIND EXERCISES. THE MAIN PROGRAM WITH FULL FUNCTIONALITY IS CALLED THERMO_STATION.PY####

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
    
def Plotter(group):
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
        title=('Weather Readings from %s' % group),
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
    unique_url = py.plot(my_fig,filename=('Festival of the Mind Group %s' % group),auto_open=False,fileopt='extend')
    s = py.Stream(Stream_ID)
    q = py.Stream(Stream_ID_2)
    return s,q

def addvalue():
    #This is in case the login values have not been added already
    value = raw_input('What is your %s?' %name)
    parser.set(section,name,value)

#This checks that 
parser = SafeConfigParser()
parser.read('details.ini')

for section in ['MetWOW']:
    for name,value in parser.items(section):
        if value:
            continue
        else:
            addvalue()

#This writes the inputted values (if any) to the file
parser.write(open('details.ini','w'))

#This assigns the values to a format that the code can now access
AWSKey = parser.get('MetWOW','AWS_Key')
SiteID = parser.get('MetWOW','Site_ID')
APIKey = parser.get('Plotly','api_key')
Stream_ID = parser.get('Plotly','stream_id')
Username = parser.get('Plotly','username')
Stream_ID_2 = parser.get('Plotly','stream_id_2')

sensor = BMP085.BMP085()
softwaretype = "Sheffield-Pi-Weather-Station-0.1"

#Check for group number to create a unique plot
while True:
    group = raw_input("What group number are you? ")
    if group == "1" or group == "2" or group == "3":
        break
    else:
        print "Sorry, I don't know that group!\n"
        continue

#Read the data
temp= format(sensor.read_temperature())
pressure = format(sensor.read_pressure())
[Timeformat,Timenow] = Timeformatting(time.gmtime())
print "It's %s degrees Celcius where you are now!" % temp

#Make it semi-interactive so kids are actually interested
if 30> float(temp) >= 25:
    print "That's pretty warm!"
elif 15 <= float(temp) < 25:
    print "That's about average temperature!"
elif float(temp) >=30:
    print "That's really warm. Are you warming it up with your hand? Don't try to trick me!"
else:
    print "It's pretty chilly where you are!"

#Get the data in the right units to upload
Temp = tempfarenheit(temp)
Pres = presinches(pressure)
    
#Construct the URL to send the data to WOW
url = 'http://wow.metoffice.gov.uk/automaticreading?siteid=%s&siteAuthenticationKey=%s&dateutc=%s&tempf=%s&baromin=%.2f&softwaretype=%s' % (SiteID,AWSKey,Timeformat,Temp,Pres,softwaretype)

#Send the request to WOW and interpret response
request = urllib2.Request(url)
response = urllib2.urlopen(request).getcode()
if float(response) == 200:
    print "You've uploaded your data to WOW!"
else:
    print "There was an error connecting to WOW"

#Sign in to Plot.ly, upload the data, and close the graphs to preserve the data
py.sign_in(Username,APIKey)
s,q = Plotter(group)
s.open()
q.open()
x=0
while x<2:
    s.write(dict(x=Timenow,y=temp))
    q.write(dict(x=Timenow,y=pressure))
    x+=1
    time.sleep(3)
s.close()
q.close()
print "You've uploaded your data to Plot.ly as well!"
