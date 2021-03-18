"""index file for manual intraday revision 
"""
import argparse
import datetime as dt
from src.appConfig import getAppConfigDict
from src.intraDayRevisionManual.intradayRevisionCreator import doIntradayRevision
from src.storeRevisedForecast.revisedForecastStorage import storeRevisedForecast

def manualStoreRevisedForecast(startTime: dt.datetime, endTime: dt.datetime)->None:
    
    x = 11 # x should be in range 1 to 15, stimulating dt.now()
    currTime = endTime+dt.timedelta(minutes=x)
    configDict=getAppConfigDict()

    startTime = currTime.replace(hour=0, minute=0, second=0, microsecond=0)
    endTime = startTime + dt.timedelta(hours= 1, minutes= 30)

    #checking dt.now() i.e currTime falls in which revision
    revisionNo = 0 
    for i in range(1,17):
        if startTime <= currTime < endTime:
            revisionNo = i
            break
        else:
            startTime = startTime + dt.timedelta(hours= 1, minutes= 30)
            endTime = endTime + dt.timedelta(hours= 1, minutes= 30)

    startTime = currTime.replace(hour=0, minute=0, second=0, microsecond=0)
    endTime = startTime + dt.timedelta(hours= 23, minutes= 59)

    revisionNoStr = "R" + str(revisionNo)
    isRevisionStorageSuccess = storeRevisedForecast(startTime, endTime, revisionNoStr, configDict)
    if isRevisionStorageSuccess:
        print(f'revision number {revisionNoStr} storage successfull')
    else:
        print(f'revision number {revisionNoStr} storage unsuccessfull')


configDict=getAppConfigDict()
count =0
endDate = dt.datetime.now() - dt.timedelta(days=2)
startDate = endDate 

# get start, end dates from command line
parser = argparse.ArgumentParser()
parser.add_argument('--start_date', help="Enter Start date in yyyy-mm-dd format",
                    default=dt.datetime.strftime(startDate, '%Y-%m-%d'))
parser.add_argument('--end_date', help="Enter end date in yyyy-mm-dd format",
                    default=dt.datetime.strftime(endDate, '%Y-%m-%d'))


args = parser.parse_args()
startDate = dt.datetime.strptime(args.start_date, '%Y-%m-%d')
endDate = dt.datetime.strptime(args.end_date, '%Y-%m-%d')

startDate = startDate.replace(hour=0, minute=0, second=0, microsecond=0)
endDate = endDate.replace(hour=0, minute=0, second=0, microsecond=0)

startTime = startDate-dt.timedelta(hours=1.5)
endTime = endDate + dt.timedelta(hours=22, minutes=30)
while (startTime < endTime):
    currRevisionStartTime= startTime
    currRevisionEndTime = startTime + dt.timedelta(hours=1, minutes=29)
    print(currRevisionStartTime, currRevisionEndTime)
    isRevisionSuccess = doIntradayRevision(currRevisionStartTime, currRevisionEndTime, configDict)
    # isRevisionSuccess=True
    if isRevisionSuccess:
        count= count+1
        manualStoreRevisedForecast(currRevisionStartTime, currRevisionEndTime)
    startTime= startTime + dt.timedelta(hours=1, minutes=30)

noOfDays = (endDate-startDate).days

if count==(noOfDays+1)*16:
    print(f" revision successfull between {startDate} and {endDate} ")
else:
    print(f" revision unsuccessfull between {startDate} and {endDate} ")
