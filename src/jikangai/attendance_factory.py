from datetime import datetime
from pandas import DataFrame
from .jikangai import Attendance, BreakTime, WorkingDate

class AttendanceFactory:
    @staticmethod
    def create_from_dataframe(
        dataframe: DataFrame,
        start_column_name: str,
        start_of_break_column_name: str,
        end_of_break_column_name: str,
        end_column_name: str,
        date_format: str) -> Attendance:

        dates = []
        for index, row in dataframe.iterrows():
            try:
                start = datetime.strptime(row[start_column_name], date_format)
                end = datetime.strptime(row[end_column_name], date_format)
                break_time = BreakTime(
                    datetime.strptime(row[start_of_break_column_name], date_format),
                    datetime.strptime(row[end_of_break_column_name], date_format)
                )
                date = WorkingDate(start, end, [break_time])
            except ValueError as e:
                error_message = f'{e}\ncheck line {index}:\n{row}'
                raise ValueError(error_message)
            dates.append(date)
        return Attendance(dates)
