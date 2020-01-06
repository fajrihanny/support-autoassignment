from datetime import datetime 
import calendar 
from pytz import timezone
  
def findDay():
    availTimezone = []
    timeBer = datetime.now(timezone('Europe/Berlin'))
    timeSF = datetime.now(timezone('America/Los_Angeles'))
    timeNZ = datetime.now(timezone('Pacific/Auckland'))
    tz_BER = timeBer.hour
    tz_SF = timeSF.hour
    tz_NZ = timeNZ.hour
    print (tz_BER)
    print (tz_SF)
    print (tz_NZ)
    isBerlinWeekday = datetime.isoweekday(timeBer)
    isSFWeekday = datetime.isoweekday(timeSF)
    isNZWeekday = datetime.isoweekday(timeNZ)

    if (isBerlinWeekday<6):
        availTimezone.append('Berlin')
    if (isSFWeekday<6):
        availTimezone.append('SF')
    if (isNZWeekday<6):
        availTimezone.append('NZ')

    print (isBerlinWeekday)
    print (isSFWeekday)
    print (isNZWeekday)
    print (availTimezone)
  
# Driver program 
findDay()