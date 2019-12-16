import datetime 
import calendar 
from pytz import timezone
  
def findDay(date): 
    tz_BER = datetime.now(timezone('Europe/Berlin')).
    born = datetime.datetime.strptime(date, '%d %m %Y').weekday() 
    return (calendar.day_name[born]) 
  
# Driver program 
date = '14 12 2019'
print(findDay(date)) 