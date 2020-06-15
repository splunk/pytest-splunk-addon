from datetime import timedelta, datetime
import math


class time_parse():
    
    def __init__(self):
        pass
    
    def convert_to_time(self, sign, num, unit):
        '''
        converts splunk time into datetime format for earliest and latest
        input -> sign to increase or decrease time
              -> num : time value  
              -> unit : unit of time eg: seconds,minuits etc

        output -> returns datetime formated time         
        '''
        num = int(num)
        unittime = None
        if unit in ('s', 'sec', 'secs', 'second', 'seconds'):
            unittime = timedelta(seconds=int(num))
        elif unit in ('m', 'min', 'minute', 'minutes'):
            unittime = timedelta(minutes=int(num))
        elif unit in ('h', 'hr', 'hrs', 'hour', 'hours'):
            unittime = timedelta(hours=int(num))
        elif unit in ('d', 'day', 'days'):
            unittime = timedelta(days=int(num))
        elif unit in ('w', 'week', 'weeks'):
            unittime = timedelta(days=(int(num) * 7))
        elif unit in ('mon', 'month', 'months') or unit in ('q', 'qtr', 'qtrs', 'quarter', 'quarters') or \
                unit in ('y', 'yr', 'yrs', 'year', 'years'):
            if unit in ('q', 'qtr', 'qtrs', 'quarter', 'quarters'):
                num *= 3
            elif unit in ('y', 'yr', 'yrs', 'year', 'years'):
                num = num * 12
                
            unittime = datetime.now()
            monthnum = int(num) * -1 if sign == '-' else int(num)
    
            if int(abs(monthnum) / 12) > 0:
                # if months are more than 12 than increase or decrease the year based on the sign value
                yearnum = int(
                    math.floor(abs(monthnum) / 12) * -1 if sign == '-' else int(math.floor(abs(monthnum) / 12)))
                monthnum = int((abs(monthnum) % 12) * -1 if sign == '-' else int((abs(monthnum) % 12)))
                unittime = datetime(unittime.year + yearnum, unittime.month + monthnum, unittime.day, unittime.hour, unittime.minute,
                                        unittime.second, unittime.microsecond)
            elif monthnum > 0:
                if unittime.month + monthnum > 12:
                    # if 
                    unittime = datetime(unittime.year + 1, ((unittime.month + monthnum) % 12), unittime.day, unittime.hour, unittime.minute,
                                            unittime.second, unittime.microsecond)
                else:
                    unittime = datetime(unittime.year, unittime.month + monthnum, unittime.day, unittime.hour, unittime.minute, unittime.second,
                                            unittime.microsecond)
            elif monthnum <= 0:
                if unittime.month + monthnum <= 0:
                    unittime = datetime(unittime.year - 1, (12 - abs(unittime.month + monthnum)), unittime.day, unittime.hour,
                                            unittime.minute, unittime.second, unittime.microsecond)
                else:
                    unittime = datetime(unittime.year, unittime.month + monthnum, unittime.day, unittime.hour, unittime.minute, unittime.second,
                                            unittime.microsecond)
            return unittime                          
        random_time = datetime.now()
        if sign == '-':
            random_time = random_time - unittime
        else:
            random_time = random_time + unittime

        return random_time
