"""index file for RMSE, MAE, MAPE error creator
"""
import datetime as dt
from typing import List, Tuple
from src.revisionwiseErrorStorage.actualDemandFetch import ActualDemandFetchRepo
from src.revisionwiseErrorStorage.forecastedDemandFetch import ForecastedDemandFetchRepo
from src.revisionwiseErrorStorage.revisionwiseVariousErrorCalculation import calculateRevisionwiseErrors
from src.revisionwiseErrorStorage.revisionwiseErrorInsertion import RevisionwiseErrorInsertion


def createRevisionwiseError(startDate: dt.datetime, endDate: dt.datetime, configDict: dict) -> bool:
    """create revisionwise mean abs error, RMSE, MAE, MAPE between start and end dates

    Args:
        startDate (dt.datetime): start date
        endDate (dt.datetime): end date
        
        configDict (dict): application configuration
    Returns:
        bool: returns true if errror storage is successfull, else false
    """    

    con_string = configDict['con_string_mis_warehouse']
    obj_actualDemandFetchRepo = ActualDemandFetchRepo(con_string)
    obj_forecastedDemandFetchRepo = ForecastedDemandFetchRepo(con_string)
    obj_revisionwiseErrorInsertion = RevisionwiseErrorInsertion(con_string)

    currDate = startDate
    insertSuccessCount = 0
    revisionList = ['R0A', 'R0B', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15', 'R16']
    # revisionList = ['R0A']

    while currDate <= endDate:
        for revisionNo in revisionList:
            #fetch actual demand
            actualDemandDf = obj_actualDemandFetchRepo.fetchActualDemand(currDate, currDate)
            #fetch forecasted demand
            forecastedDemandDf = obj_forecastedDemandFetchRepo.fetchForecastedDemand(currDate, currDate, revisionNo)
            #calculate RMSE, MAE, MAPE
            data:List[Tuple] = calculateRevisionwiseErrors(actualDemandDf, forecastedDemandDf, revisionNo, currDate.date())
            #push errors to db
            isInsertionSuccess = obj_revisionwiseErrorInsertion.insertRevisionwiseError(data)

            if isInsertionSuccess:
                insertSuccessCount = insertSuccessCount + 1


        # update currDate
        currDate += dt.timedelta(days=1)

    numOfDays = (endDate-startDate).days
    if insertSuccessCount == 18*(numOfDays +1) :
        return True
    else:
        return False