"""index file for storing revisions
"""
import argparse
import datetime as dt
from src.appConfig import getAppConfigDict
from src.storeRevisedForecast.revisedForecastStorage import storeRevisedForecast

configDict=getAppConfigDict()

currTime = dt.datetime.strftime(dt.datetime.now(), '%Y-%m-%d %H:%M:%S')
# currTime = "2021-01-29 00:10:40"
parser = argparse.ArgumentParser()
parser.add_argument('--curr_time', help="Enter Start time in yyyy-mm-dd HH:MM:SS format",
                    default = currTime)

args = parser.parse_args()
currTime = dt.datetime.strptime(args.curr_time, '%Y-%m-%d %H:%M:%S')

startTime = currTime.replace(hour=0, minute=0, second=0, microsecond=0)
endTime = startTime + dt.timedelta(hours= 1, minutes= 30)

#checking dt.now() falls in which revision
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


