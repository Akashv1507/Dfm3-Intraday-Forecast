"""index file for blockwise Mw error creator
"""
import argparse
from datetime import datetime as dt
from datetime import timedelta
from src.appConfig import getAppConfigDict
from src.blockwiseErrorStorage.blockwiseErrorCreator import createBlockwiseError


configDict=getAppConfigDict()

endDate = dt.now() - timedelta(days=1)
startDate = endDate - timedelta(days=1)

revisionNo = 'R0A'

# get start, end dates and revision number from command line
parser = argparse.ArgumentParser()
parser.add_argument('--start_date', help="Enter Start date in yyyy-mm-dd format",
                    default=dt.strftime(startDate, '%Y-%m-%d'))
parser.add_argument('--end_date', help="Enter end date in yyyy-mm-dd format",
                    default=dt.strftime(endDate, '%Y-%m-%d'))
parser.add_argument('--revision_no', help="Enter revision no",
                    default = revisionNo)

args = parser.parse_args()
startDate = dt.strptime(args.start_date, '%Y-%m-%d')
endDate = dt.strptime(args.end_date, '%Y-%m-%d')
revisionNo = args.revision_no

startDate = startDate.replace(hour=0, minute=0, second=0, microsecond=0)
endDate = endDate.replace(hour=0, minute=0, second=0, microsecond=0)

print('startDate = {0}, endDate = {1}, revisionNo = {2}'.format(dt.strftime(
    startDate, '%Y-%m-%d'), dt.strftime(endDate, '%Y-%m-%d'), revisionNo))


# create blockwise mw error and percentage mw error  between start and end dates
isBlockwiseMwErrorCreationSuccess = createBlockwiseError(startDate, endDate, revisionNo, configDict)

if isBlockwiseMwErrorCreationSuccess:
    print('blockwise mw error creation done...')
else:
    print('blockwise mw error creation failure...')