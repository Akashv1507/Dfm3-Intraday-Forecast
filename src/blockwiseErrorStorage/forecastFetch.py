import cx_Oracle
import pandas as pd
import datetime as dt
from typing import List, Tuple, TypedDict


class ForecastedDemandFetchRepo():
    """fethc actual demand data for a day 
    """

    def __init__(self, con_string):
        """initialize connection string
        Args:
            con_string ([type]): connection string 
        """
        self.connString = con_string

    def fetchForecastedDemand(self, startDate:dt.datetime, endDate:dt.datetime, revisionNo : str) ->pd.core.frame.DataFrame:
        """fetch forecasted demand of a particular revision on a day

        Args:
            startDate (dt.datetime): start date
            endDate (dt.datetime): end date
            revsionNo(str): revsion number

        Returns:
            pd.core.frame.DataFrame: dataframe that contains forecasted demand
        """         

        start_time_value = startDate
        end_time_value = endDate + dt.timedelta(hours=23, minutes= 59)
        try:
            connection = cx_Oracle.connect(self.connString)

        except Exception as err:
            print('error while creating a connection', err)
        else:
            try:
                cur = connection.cursor()
                fetch_sql = "SELECT time_stamp, entity_tag, forecasted_demand_value FROM dfm3_forecast_revision_store WHERE time_stamp BETWEEN TO_DATE(:start_time,'YYYY-MM-DD HH24:MI:SS') and TO_DATE(:end_time,'YYYY-MM-DD HH24:MI:SS') and revision_no = :rNo and (entity_tag='WRLDCMP.SCADA1.A0047000' ) ORDER BY entity_tag, time_stamp"
                cur.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' ")
                forecastedDemandDf = pd.read_sql(fetch_sql, params={
                                 'start_time': start_time_value, 'end_time': end_time_value, 'rNo': revisionNo}, con=connection)

            except Exception as err:
                print('error while creating a cursor', err)
            else:
                connection.commit()
        finally:
            cur.close()
            connection.close()
        return forecastedDemandDf