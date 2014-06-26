import datetime
import sys
import os
import glob
import time
import Adafruit_BMP.BMP085 as BMP085
import plotly.plotly as py
from plotly.graph_objs import *
import urllib
import urllib2

def tempfarenheit(Temperature):
    Temp = (float(Temperature)*9/5)+32
    return Temp

def presinches(pressure):
    Pres = float(pressure) * 0.000295333727
    return Pres

sensor = BMP085.BMP085()
Temperature = []
Pressure = []
Time = []
X=0
t=0
frequency = 10
Siteid = 878216001
Key = 654789
softwaretype = "Sheffield-Pi-Weather-Station 0.1"
f = open("dtat.txt",'w')
F = []
while True:
    temp= format(sensor.read_temperature())
    pressure = format(sensor.read_pressure())
    Timenow = time.strftime('%Y-%m-%d+%H:%M:%S',time.gmtime())
    Timeformat = Timenow.replace(':','%3A')
    Temperature.append(temp)
    Pressure.append(pressure)
    Time.append(Timenow)
    print 'Temp = %s *C' % temp
    print 'Pressure = %s Pa' % pressure
    print 'Time = %s' % Timenow
    Temp = tempfarenheit(temp)
    Pres = presinches(pressure)
#    new = str(datetime.datetime.now()).replace(':','%3A').replace(' ','+')
#    print new
    url = 'http://wow.metoffice.gov.uk/automaticreading?siteid=%s&siteAuthenticationKey=%s&dateutc=%s&tempf=%s&baromin=%.2f&softwaretype=%s' % (Siteid,Key,Timeformat,Temp,Pres,softwaretype)
    print url
    request = urllib2.Request(url)
    response = urllib2.urlopen(request).getcode()
    if response == '200':
        print "Connection is ok, data has been uploaded to %s
    X += 1
    if X >= 3:
        print Temperature
        print Pressure
        print Time
        break
    t += frequency
    f.write('%s %6s *C %15s Pa\n %26s *F %13.2f inch Hg\n' % (Timenow,temp,pressure,Temp,Pres))
    try:
        time.sleep(frequency)
    except:
        print "Data could not be handled at this time"
        break
f.close

def format_time(Time):
    C=[]
    for integer in Time:
        new = str(integer).replace('datetime.datetime','').replace('(','').replace(')','').replace(',','').replace(':','%3A').replace(' ','+')
        new = new[:-7]
        C.append(new)
    return C

#def presinches(pressure):
#    Pres = float(pressure) * 0.000295333727
#    return Pres

#def tempfarenheit(Temperature):
#    if len(Temperature)) >=1:
#        Temp = []
#        for c in Temperature:
#            Temp.append((float(c)*9/5)+32)
#    else:
#    Temp = (float(Temperature)*9/5)+32
#    return Temp 

#f = open("dtat.txt",'w')
#F = []
#for i in range(len(Temperature)):
 #   F.append(Temperature[i])
#    F.append(Pressure[i])
#    F.append(Time[i])
#for n in range(len(F)):
#    f.write('%s\n' % (F[n]))
#f.close

