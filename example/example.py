from jikangai import (
    Agreement36, CompanyProfile, Validator, LegalHoliday, AttendanceFactory
)
from datetime import datetime
import pandas as pd

# Load attendance data from a csv file
df = pd.read_csv('example/attendance.csv')
attendance_of_an_employee = AttendanceFactory.create_from_dataframe(
    df, 'start', 'start of break', 'end of break', 'end', '%m/%d/%Y %H:%M'
)

# Validate attendance
profile = CompanyProfile(
    LegalHoliday.of_every_sunday(), Agreement36(datetime(2024, 1, 1))
)
result = Validator(profile).validate(attendance_of_an_employee)
print(result)
