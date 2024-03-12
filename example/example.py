from jikangai import (
    Agreement36, CompanyProfile, Validator, LegalHoliday, AttendanceFactory
)
from datetime import datetime, timedelta
import pandas as pd

# Load attendance data from a csv file
df = pd.read_csv('example/attendance.csv')
attendance_of_an_employee = AttendanceFactory.create_from_dataframe(
    df, 'start', 'start of break', 'end of break', 'end', '%m/%d/%Y %H:%M'
)

# Validate attendance
agreement36 = Agreement36(starting_date=datetime(2024, 1, 1), valid_period=timedelta(days=364), daily_overtime_limit=timedelta(hours=5))
profile = CompanyProfile(
    legal_holidays=LegalHoliday.of_every_sunday(), agreement36=agreement36
)
result = Validator(profile).validate(attendance_of_an_employee)
print(result)
