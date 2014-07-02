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



sensor = BMP085.BMP085()
Temperature = []; Pressure = []; Time = []; X = 0
softwaretype = "Sheffield-Pi-Weather-Station-0.1"
n = raw_input("Would you like to stop after a certain amount of readings? If so, type the amount. If not, type 'n': ")
if float(n)>1 or n == "n":
	frequency = input('What time period between readings (in seconds) would you like: ')

#This allows user to input their WOW details
def wowdetails():
	while True:
		SiteID = raw_input("What is your Weather Observations Website Site Id? "); AWSKey = raw_input("What is your Weather Observations Site AWS Key? ")
		if float(SiteID) == True and float(AWSKey) == True:
			Siteid = SiteID, Key = AWSKey
			return Siteid,Key
			break
		else:
			print "Unknown intput, please try again."
			continue
				

[Siteid,Key] = wowdetails()

#These format the plot.ly graph
my_stream_id = rawinput("What is your Plot.ly stream ID? ")
my_stream = Stream(token = my_stream_id,
                   maxpoints=80)
my_data = Data([Scatter(x=[],
                        y=[],
                        mode = 'lines+markers',
                        stream = my_stream)])
my_layout = Layout(title='Temperature Readings from SheffieldPiStation')
my_fig = Figure(data = my_data,layout = my_layout)
unique_url = py.plot(my_fig,filename='Weather Data from the Pi Weather Station')
s=py.Stream(my_stream_id)

print "Press ctrl-C at any time to cancel the process"

while True:
    s.open()
    f = open("dtat.txt",'a')
    #Read the data
    temp= format(sensor.read_temperature())
    pressure = format(sensor.read_pressure())
    [Timeformat,Timenow] = Timeformatting(time.gmtime())
    print temp,pressure,Timenow
    #Get the data in the right units to upload
    Temp = tempfarenheit(temp)
    Pres = presinches(pressure)
    #Construct the URL to send the data to WOW
    url = 'http://wow.metoffice.gov.uk/automaticreading?siteid=%s&siteAuthenticationKey=%s&dateutc=%s&tempf=%s&baromin=%.2f&softwaretype=%s' % (Siteid,Key,Timeformat,Temp,Pres,softwaretype)
    #Send the request to WOW and interpret response
    request = urllib2.Request(url)
    response = urllib2.urlopen(request).getcode()
    if response == '200':
        print "Connection is ok, data has been uploaded to site %s" % Siteid
    else:
        print "Error connecting to site. Data was not uploaded at this time."
    #Write the values to s (for plot.ly which will be uploaded) and f (for the file that will be saved)
    s.write(dict(x=Timenow,y=temp))
    f.write('%s %7s *C %14s Pa\n %26s *F %13.2f inch Hg\n' % (Timenow,temp,pressure,Temp,Pres))
    #Prepare the code to run indefinitely or until required number of readings is reached
    if n != "n":
            X += 1
            if X >= float(n):
                break
    #Close the file to preserve changes
    f.close
    try:
        time.sleep(frequency)
    except:
        print "Process was terminated"
        break
