import time
import Adafruit_BMP.BMP085 as BMP085
import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import *
import urllib
import urllib2
sensor = BMP085.BMP085()
def tempfarenheit(Temperature):
    Temp = (float(Temperature)*9/5)+32
    return Temp
def pressureinches(Pressure):
    Pres = float(Pressure)*0.000295333727
    return Pres
def Timeformatting(theTime):
    Timenow = time.strftime('%Y-%m-%d %H:%M:%S',theTime)
    Timeformat = Timenow.replace(':','%3A').replace(' ','+')]
    return Timeformat,Timenow
SiteID = 000000000; AWSKey = 000000; softwaretype = "my_software"
API_Key = 000000, Username = MyUsername, Stream_ID = 00000aaaaa
py.sign_in(Username,APIKey)
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
n = raw_input("No of readings (n for infinite): ")
if float(n)>1 or n == "n":
frequency = input('Frequency: ')
while True:
    temperature = format(sensor.read_temperature())
    pressure = format(sensor.read_pressure())
    Timenow = time.gmtime()
    print temperature, pressure, Timenow
    f = open("datafile.txt",'a')
    f.write('%s %7s *C %14s Pa' % Timenow, temperature, pressure)
    f.close
    url = 'http://wow.metoffice.gov.uk/automaticreading?siteid=%s&siteAuthenticationKey=%s&dateutc=%s&tempf=%s&baromin=%.2f&softwaretype=%s' % (SiteID,AWSKey,Timeformat,Temp,Pres,softwaretype)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request).getcode()
    if float(response) == 200:
        print "Data upload OK"
    else:
        print "Data upload error"
    s.write(dict(x=Timenow,y=temp))
    q.write(dict(x=Timenow,y=pressure))
    if n != "n":
        X += 1
        if X >= float(n):
            s.close()
            q.close()
            break
    try:
        time.sleep(frequency)
    except:
        print "Process was terminated"
        break
