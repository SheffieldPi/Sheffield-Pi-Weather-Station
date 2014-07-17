Sheffield Pi Weather Station

To download Adafruit files to detect sensor, run code 

        git clone https://github.com/adafruit/Adafruit_Python_BMP.git
        
To download the Plot.ly software, run code

        sudo pip install plotly
        
============================

The file Thermo_Station.py is the full code which will upload the data to the Weather Observations Website (WOW), stream it to graphing site Plot.ly, and write the data to file. It requires an account with the Met Office (go to http://wow.metoffice.gov.uk/ to sign up) and with Plot.ly (go to https://plot.ly/ to sign up)

The file FotM.py is a reduced-function version of the code that will only upload data to WOW and print it on screen. It is intended to be used as an activity at the Festival of the Mind in Sheffield

The files beginning with Autorun_"Station are created to run the weather station at start up without user input. Please visit http://sheffieldpistation.wordpress.com/auto-running-the-weather-station-at-startup/ to set the automatic station up.

For more information on setting up the Raspberry Pi Weather Station, including a how-to guide with the programs needed to install, visit http://sheffieldpistation.wordpress.com/
