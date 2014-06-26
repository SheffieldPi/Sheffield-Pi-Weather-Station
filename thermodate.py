import datetime
import sys
import time
import Adafruit_BMP.BMP085 as BMP085
import urllib
import urllib2

#import plotly.plotly as py
#import plotly.tools as tls
#import numpy as np
#from plotly.graph_objs import *
#py.sign_in("SheffieldPiStation","s4o7a7yvuy",
#tls.set_credentials_file(stream_ids="zy7urkrmve")
#my_stream_ids = tls.get_credentials_file()['stream_ids']



def tempfarenheit(Temperature):
    Temp = (float(Temperature)*9/5)+32
    return Temp

def presinches(pressure):
    Pres = float(pressure) * 0.000295333727
    return Pres

def Timeformatting(aTime):
    Timenow = time.strftime('%Y-%m-%d+%H:%M:%S',aTime)
    Timeformat = Timenow.replace(':','%3A')
    return Timeformat,Timenow

sensor = BMP085.BMP085()
Temperature = []
Pressure = []
Time = []
X=0
t=0
frequency = 10
Siteid = 878216001
Key = 654789
softwaretype = "Sheffield-Pi-Weather-Station-0.1"
F = []
while True:
    f = open("dtat.txt",'a')
    temp= format(sensor.read_temperature())
    pressure = format(sensor.read_pressure())
    [Timeformat,Timenow] = Timeformatting(time.gmtime())
    print 'Temp = %s *C' % temp
    print 'Pressure = %s Pa' % pressure
    print 'Time = %s' % Timenow
    Temp = tempfarenheit(temp)
    Pres = presinches(pressure)
    url = 'http://wow.metoffice.gov.uk/automaticreading?siteid=%s&siteAuthenticationKey=%s&dateutc=%s&tempf=%s&baromin=%.2f&softwaretype=%s' % (Siteid,Key,Timeformat,Temp,Pres,softwaretype)
    print url
#    request = urllib2.Request(url)
#    response = urllib2.urlopen(request).getcode()
#    if response == '200':
#        print "Connection is ok, data has been uploaded to site %s" % Siteid
#    else:
#        print "Error connecting to site. Data was not uploaded at this time."
    t += frequency
    f.write('%s %7s *C %14s Pa\n %26s *F %13.2f inch Hg\n' % (Timenow,temp,pressure,Temp,Pres))
    X += 1
    if X >= 3:
        break
    f.close
    try:
        time.sleep(frequency)
    except:
        print "Process was terminated"
        break

#f = open("dtat.txt",'w')
#F = []
#for i in range(len(Temperature)):
 #   F.append(Temperature[i])
#    F.append(Pressure[i])
#    F.append(Time[i])
#for n in range(len(F)):
#    f.write('%s\n' % (F[n]))
#f.close

