from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class LegalHoliday:
    def __init__(self, week_number_of_4weeks: int, weekday: int = 7):
        self._week_number_of_4weeks = week_number_of_4weeks
        self._weekday = weekday

    @property
    def weekday(self) -> int:
        """This value ranges from 1 to 7.
        """
        return self._weekday

    @property
    def week_number_of_4weeks(self) -> int:
        """This value ranges from 1 to 4.
        """
        return self._week_number_of_4weeks

    @staticmethod
    def of_every_sunday() -> List['LegalHoliday']:
        return [LegalHoliday(1), LegalHoliday(2), LegalHoliday(3), LegalHoliday(4)]

class BreakTime:
    def __init__(self, start: datetime, end: datetime):
        if not end >= start:
            raise ValueError("end must be greater than or equal to start")

        self._start = start
        self._end = end

    @property
    def start(self) -> datetime:
        return self._start

    @property
    def end(self) -> datetime:
        return self._end

    def value(self) -> timedelta:
        return self._end - self._start

class WorkingDate:
    def __init__(self, start: datetime, end: datetime, break_time_list: List[BreakTime]):
        if not end >= start:
            raise ValueError("end must be greater than or equal to start")

        for item in break_time_list:
            if not item.start >= start:
                raise ValueError("break time start must be greater than or equal to start")
            elif not item.end <= end:
                raise ValueError("break time end must be less than or equal to end")

        self._start = start
        self._end = end
        self._break_time_list = break_time_list

    def break_time(self) -> timedelta:
        total_break_time = timedelta()
        for item in self._break_time_list:
            total_break_time += item.value()
        return total_break_time

    def isocalendar(self):
        return self._start.isocalendar()

    def is_legal_holiday(self, legal_holidays: List[LegalHoliday]) -> bool:
        _, week_number, weekday = self.isocalendar()
        week_number_of_4weeks = week_number % 4
        return any(week_number_of_4weeks == holiday.week_number_of_4weeks and weekday == holiday.weekday for holiday in legal_holidays)

    def date_components(self) -> Tuple[int, int, int]:
        """Returns the components of the start date.

        Returns:
            Tuple[int, int, int]: A tuple containing the year, month, and day components.
        """
        return (self._start.year, self._start.month, self._start.day)

    def overtime_work_hours(self, legal_working_hours: timedelta) -> timedelta:
        return max(self.working_hours() - legal_working_hours, timedelta())

    def working_hours(self) -> timedelta:
        return self._end - self._start - self.break_time()

class Attendance:
    def __init__(self, dates: List[WorkingDate]):
        self._dates = dates

        isocalendar_based_dates = {}
        for date in dates:
            year, week_number, weekday = date.isocalendar()
            isocalendar_based_dates.setdefault((year, week_number), {})[weekday] = date
        self._isocalendar_based_dates = isocalendar_based_dates

        monthly_based_dates = {}
        for date in dates:
            year, month, day = date.date_components()
            monthly_based_dates.setdefault((year, month), {})[day] = date
        self._monthly_based_dates = monthly_based_dates

    @property
    def isocalendar_based_dates(self) -> Dict[Tuple[int, int], Dict[int, WorkingDate]]:
        return self._isocalendar_based_dates

    def _dates_of_holidays_and_non_holidays(self, dates, legal_holidays) -> Tuple[List[WorkingDate], List[WorkingDate]]:
        dates_of_holidays = [date for date in dates if date.is_legal_holiday(legal_holidays)]
        dates_of_non_holidays = [date for date in dates if not date.is_legal_holiday(legal_holidays)]
        return (dates_of_holidays, dates_of_non_holidays)

    def _sum_overtime_work_hours(self, dates, working_hours_per_day) -> timedelta:
        return sum([date.overtime_work_hours(working_hours_per_day) for date in dates], timedelta())
        
    def daily_overtime_work_hours(self, working_hours_per_day, legal_holidays) -> Tuple[List[timedelta], List[timedelta]]:
        dates_of_holidays, dates_of_non_holidays = self._dates_of_holidays_and_non_holidays(self._dates, legal_holidays)
        return ([date.overtime_work_hours(working_hours_per_day) for date in dates_of_holidays],
                [date.overtime_work_hours(working_hours_per_day) for date in dates_of_non_holidays])

    def weekly_overtime_work_hours(self, working_hours_per_day, legal_holidays) -> Dict[int, Dict[int, Tuple[timedelta, timedelta]]]:
        overtime_hours = {}
        for (year, week_number), week in self._isocalendar_based_dates.items():
            dates_of_holidays, dates_of_non_holidays = self._dates_of_holidays_and_non_holidays(week.values(), legal_holidays)
            overtime_hours.setdefault(year, {})[week_number] = (
                self._sum_overtime_work_hours(dates_of_holidays, working_hours_per_day),
                self._sum_overtime_work_hours(dates_of_non_holidays, working_hours_per_day)
            )
        return overtime_hours

    def monthly_overtime_work_hours(self, working_hours_per_day, legal_holidays) -> Dict[int, Dict[int, Tuple[timedelta, timedelta]]]:
        overtime_hours = {}
        for (year, month_number), month in self._monthly_based_dates.items():
            dates_of_holidays, dates_of_non_holidays = self._dates_of_holidays_and_non_holidays(month.values(), legal_holidays)
            overtime_hours.setdefault(year, {})[month_number] = (
                self._sum_overtime_work_hours(dates_of_holidays, working_hours_per_day),
                self._sum_overtime_work_hours(dates_of_non_holidays, working_hours_per_day)
            )
        return overtime_hours

    def yearly_overtime_work_hours(self, working_hours_per_day, legal_holidays) -> Dict[int, Dict[int, timedelta]]:
        overtime_hours = {}
        for (year, _), week in self._isocalendar_based_dates.items():
            dates_of_holidays, dates_of_non_holidays = self._dates_of_holidays_and_non_holidays(week.values(), legal_holidays)
            total_overtime_of_holidays, total_overtime_of_non_holidays = overtime_hours.get(year, (timedelta(), timedelta()))
            overtime_hours[year] = (
                total_overtime_of_holidays + self._sum_overtime_work_hours(dates_of_holidays, working_hours_per_day),
                total_overtime_of_non_holidays + self._sum_overtime_work_hours(dates_of_non_holidays, working_hours_per_day)
            )
        return overtime_hours

    def weekly_count_worked_on_legal_holidays(self, legal_holidays: List[LegalHoliday]) -> int:
        counts = {}
        for (year, week_number), week in self._isocalendar_based_dates.items():
            count = [date.is_legal_holiday(legal_holidays) for date in week.values()].count(True)
            counts.setdefault(year, {})[week_number] = count
        return counts

class LaborStandardsAct:
    def __init__(self):
        self._holidays_per_4weeks = 4
        self._working_hours_per_day = timedelta(hours=8)
        self._working_hours_per_week = timedelta(hours=40)

    @property
    def holidays_per_4weeks(self) -> int:
        return self._holidays_per_4weeks

    @property
    def working_hours_per_day(self) -> timedelta:
        return self._working_hours_per_day

    @property
    def working_hours_per_week(self) -> timedelta:
        return self._working_hours_per_week

class Agreement36:
    LEGAL_MAX_DAILY_OVERTIME_LIMIT = timedelta(hours=24) - LaborStandardsAct().working_hours_per_day
    LEGAL_MAX_MONTHLY_OVERTIME_LIMIT = timedelta(hours=45)
    LEGAL_MAX_YEARLY_OVERTIME_LIMIT = timedelta(hours=360)

    def __init__(self,
                  starting_date: datetime,
                  valid_period: timedelta,
                  daily_overtime_limit: timedelta = LEGAL_MAX_DAILY_OVERTIME_LIMIT, 
                  monthly_overtime_limit: timedelta = LEGAL_MAX_MONTHLY_OVERTIME_LIMIT, 
                  yearly_overtime_limit: timedelta = LEGAL_MAX_YEARLY_OVERTIME_LIMIT):

        if not daily_overtime_limit <= self.LEGAL_MAX_DAILY_OVERTIME_LIMIT:
            raise ValueError(f"daily_overtime_limit must be less than or equal to {self.LEGAL_MAX_DAILY_OVERTIME_LIMIT}")

        if not monthly_overtime_limit <= self.LEGAL_MAX_MONTHLY_OVERTIME_LIMIT:
            raise ValueError(f"monthly_overtime_limit must be less than or equal to {self.LEGAL_MAX_MONTHLY_OVERTIME_LIMIT}")

        if not yearly_overtime_limit <= self.LEGAL_MAX_YEARLY_OVERTIME_LIMIT:
            raise ValueError(f"yearly_overtime_limit must be less than or equal to {self.LEGAL_MAX_YEARLY_OVERTIME_LIMIT}")

        self._starting_date = starting_date
        self._ending_date = starting_date + valid_period
        self._daily_overtime_limit = daily_overtime_limit
        self._monthly_overtime_limit = monthly_overtime_limit
        self._yearly_overtime_limit = yearly_overtime_limit

    @property
    def daily_overtime_limit(self) -> timedelta:
        return self._daily_overtime_limit

    @property
    def monthly_overtime_limit(self) -> timedelta:
        return self._monthly_overtime_limit

    @property
    def yearly_overtime_limit(self) -> timedelta:
        return self._yearly_overtime_limit

    def available_monthly_overtime(self, overtime: timedelta) -> timedelta:
        return self._monthly_overtime_limit - overtime

    def available_yearly_overtime(self, overtime: timedelta) -> timedelta:
        return self._yearly_overtime_limit - overtime

    def validate_daily_overtime(self, overtime: timedelta) -> bool:
        return overtime <= self._daily_overtime_limit

    def validate_monthly_overtime(self, overtime: timedelta) -> bool:
        return overtime <= self._monthly_overtime_limit

    def validate_yearly_overtime(self, overtime: timedelta) -> bool:
        return overtime <= self._yearly_overtime_limit

class CompanyProfile:
    def __init__(self, legal_holidays: List[LegalHoliday], agreement36: Agreement36 = None):
        self._agreement36 = agreement36
        self._legal_holidays  = legal_holidays

    @property
    def agreement36(self) -> Agreement36:
        return self._agreement36

    @property
    def legal_holidays(self) -> List[LegalHoliday]:
        return self._legal_holidays

    def has_agreement36(self) -> bool:
        return self._agreement36 != None

class Result:
    def __init__(self,
                 violations,
                 weekly_overtime_work_hours: Dict[int, Dict[int, timedelta]],
                 monthly_overtime_work_hours: Dict[int, Dict[int, timedelta]],
                 yearly_overtime_work_hours: Dict[int, timedelta],
                 weekly_count_worked_on_legal_holidays: Dict[int, Dict[int, int]]):
        self._violations = violations
        self._weekly_overtime_work_hours = weekly_overtime_work_hours
        self._monthly_overtime_work_hours = monthly_overtime_work_hours
        self._yearly_overtime_work_hours = yearly_overtime_work_hours
        self._weekly_count_worked_on_legal_holidays = weekly_count_worked_on_legal_holidays

    def __str__(self):
        violations_str = '\n'.join([f'  {violation}' for violation in self._violations])

        weekly_overtime_work_hours_str = '\n'
        for year, week in self._weekly_overtime_work_hours.items():
            weekly_overtime_work_hours_str += (
                f'  {year}\n' +
                '\n'.join([f'    week {week_number}: in holidays: {self.format_timedelta(overtime_of_holidays)}, in non holidays: {self.format_timedelta(overtime_of_non_holidays)}' for week_number, (overtime_of_holidays, overtime_of_non_holidays) in week.items()])
            )

        monthly_overtime_work_hours_str = '\n'
        for year, month in self._monthly_overtime_work_hours.items():
            monthly_overtime_work_hours_str += (
                f'  {year}\n' +
                '\n'.join([f'    month {month_number}: in holidays: {self.format_timedelta(overtime_of_holidays)}, in non holidays: {self.format_timedelta(overtime_of_non_holidays)}' for month_number, (overtime_of_holidays, overtime_of_non_holidays) in month.items()])
            )

        yearly_overtime_work_hours_str = '\n'
        yearly_overtime_work_hours_str += (
            '\n'.join([f'  {year}: in holidays: {self.format_timedelta(overtime_of_holidays)}, in non holidays: {self.format_timedelta(overtime_of_non_holidays)}' for year, (overtime_of_holidays, overtime_of_non_holidays) in self._yearly_overtime_work_hours.items()])
        )

        weekly_count_worked_on_legal_holidays_str = '\n'
        for year, week in self._weekly_count_worked_on_legal_holidays.items():
            weekly_count_worked_on_legal_holidays_str += (
                f'  {year}\n' +
                '\n'.join([f'    week {week_number}: {count}' for week_number, count in week.items()])
            )

        return f"""violated: {self.violated()}
{violations_str}
weekly_overtime_work_hours: {weekly_overtime_work_hours_str}
monthly_overtime_work_hours: {monthly_overtime_work_hours_str}
yearly_overtime_work_hours: {yearly_overtime_work_hours_str}
weekly_count_worked_on_legal_holidays: {weekly_count_worked_on_legal_holidays_str}
"""

    def format_timedelta(self, td: timedelta) -> str:
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    def violated(self) -> bool:
        return len(self._violations) > 0

class Validator:
    def __init__(self, profile: CompanyProfile, labor_standards_act: LaborStandardsAct = LaborStandardsAct()):
        self._profile = profile
        self._labor_standards_act = labor_standards_act

    def validate(self, attendance: Attendance) -> Result:
        (daily_overtime_work_hours_of_holiday, daily_overtime_work_hours_of_non_holiday) = attendance.daily_overtime_work_hours(self._labor_standards_act.working_hours_per_day, self._profile.legal_holidays)
        weekly_overtime_work_hours = attendance.weekly_overtime_work_hours(self._labor_standards_act.working_hours_per_day, self._profile.legal_holidays)
        monthly_overtime_work_hours = attendance.monthly_overtime_work_hours(self._labor_standards_act.working_hours_per_day, self._profile.legal_holidays)
        yearly_overtime_work_hours = attendance.yearly_overtime_work_hours(self._labor_standards_act.working_hours_per_day, self._profile.legal_holidays)
        weekly_count_worked_on_legal_holidays = attendance.weekly_count_worked_on_legal_holidays(self._profile.legal_holidays)

        violations = []
        if not self._profile.has_agreement36():
            violated = any(
                overtime_of_holidays.total_seconds() != 0 or overtime_of_non_holidays.total_seconds() != 0 for _, (overtime_of_holidays, overtime_of_non_holidays) in yearly_overtime_work_hours.items()
            )
            if violated:
                violations.append('Must be no overtime')
        else:
            agreement36 = self._profile.agreement36
            violated = any(
                not agreement36.validate_daily_overtime(overtime_of_non_holidays) for overtime_of_non_holidays in daily_overtime_work_hours_of_non_holiday
            )
            if violated:
                violations.append(f'Daily overtime must be {agreement36.daily_overtime_limit} hours or less')

            violated = any(
                not agreement36.validate_monthly_overtime(overtime_of_non_holidays) for _, month in monthly_overtime_work_hours.items() for _, (_, overtime_of_non_holidays) in month.items()
            )
            if violated:
                violations.append(f'Montly overtime must be {agreement36.monthly_overtime_limit} hours or less')

            violated = any(
                not agreement36.validate_yearly_overtime(overtime_of_non_holidays) for _, (_, overtime_of_non_holidays) in yearly_overtime_work_hours.items()
            )
            if violated:
                violations.append(f'fYearly overtime must be {agreement36.yearly_overtime_limit} hours or less')

        return Result(violations, weekly_overtime_work_hours, monthly_overtime_work_hours, yearly_overtime_work_hours, weekly_count_worked_on_legal_holidays)
