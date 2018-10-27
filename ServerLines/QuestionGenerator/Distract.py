from dateutil.parser import parse
from random import sample , randint
import re
from Constants import *

TIME_ENTITIES = ["Year", "Month", "Day", "Week", "Decade", "Millenium"]

def removeTrailingSpace(content):
    content = content[:-1] if content[-1] == ' ' else content
    return content


def datesDistract(date):

    try:
        parse(date)

        YEAR_REGEX = r'[12][0-9]{3}'
        DATE_REGEX = r'[12]?[0-9]|3[01]'
        short_months = [x[:3] for x in MONTH_LIST]
        MONTH_REGEX = r'(' + "|".join(MONTH_LIST) + "|" + ("|".join(MONTH_LIST)).lower() + "|" + "|".join(
            short_months) + "|" + ("|".join(short_months)).lower() + ')'

        yearValue = re.findall(YEAR_REGEX , date)
        yearFlag = True if len(yearValue) > 0 else False

        if(yearFlag):
            # print(yearValue)
            date = re.sub(YEAR_REGEX , '' , date)
            # print(date)

        monthValue = re.findall(MONTH_REGEX , date)
        dateValue = re.findall(DATE_REGEX , date)

        # print(yearValue , monthValue , dateValue)
        monthFlag = True if len(monthValue) > 0 else False
        dateFlag = True if len(dateValue) > 0 else False

        # print(dateValue)

        finalString = ''
        option1 = ''
        option2 = ''
        if(dateFlag):
            finalString += dateValue[0] + ' '

            random1, random2 = sample(range(1 , 29) , 2)

            option1 += str(random1) + ' '
            option2 += str(random2)+ ' '

        if (monthFlag):
            finalString += monthValue[0] + ' '

            actual = monthValue[0]
            random1, random2 = actual, actual

            while random1 == random2 or random1 == actual or random2 == acutal:
                random1 , random2 = sample(range(0, 12), 2)

            option1 += str(MONTH_LIST[random1]) + ' '
            option2 += str(MONTH_LIST[random2]) + ' '

        if (yearFlag):
            finalString += yearValue[0] + ' '
            lowerMonth = 1
            upperMonth = 4

            if(monthFlag):
                actual = yearValue[0]
                random1 = randint(0 , 1)
                random2 = -1 * randint(0 , 1)
                option1 += str(int(actual) + random1) + ' '
                option2 += str(int(actual) + random2) + ' '

            else:
                actual = yearValue[0]
                random1, random2 = randint(lowerMonth, upperMonth), randint(lowerMonth, upperMonth)

                op = -1 * random1 if randint(0,4) < 2 else random1

                option1 += str(int(actual) + op) + ' '

                op = -1 * random2 if randint(0,4) < 2 else random2

                option2 += str(int(actual) + op) + ' '

        # print([finalString, option1, option2])
        return [removeTrailingSpace(finalString) , removeTrailingSpace(option1) , removeTrailingSpace(option2)]

    except ValueError as ex:
        date = date.lower()
        S_YEAR_REGEX = r'([12][0-9]{3})s'

        yearValue = re.findall(S_YEAR_REGEX , date)
        yearFlag = True if len(yearValue) > 0 else False

        if(yearFlag):
            index = re.search(S_YEAR_REGEX, date).start()
            date = re.sub(S_YEAR_REGEX, '', date)

            actual = int(yearValue[0])
            finalString = date[:index] + ' ' + str(actual) + 's' + ' ' + date[index:]

            random1 = randint(1 , 3)
            op = -1 if randint(0 , 4) < 2 else 1
            option1 = date[:index] + ' ' + str(actual + op*random1*10) + 's' + ' ' + date[index:]

            random2 = randint(1, 3)
            op = -1 if randint(0 , 4) < 2 else 1
            option2 = date[:index] + ' ' + str(actual + op*random2*10) + 's' + ' ' + date[index:]

        return [removeTrailingSpace(finalString), removeTrailingSpace(option1), removeTrailingSpace(option2)]

        # TH_YEAR_REGEX = r'([0-9]{2})th'
        # yearValue = re.findall(TH_YEAR_REGEX, date)
        # yearFlag = True if len(yearValue) > 0 else False
        #
        # if (yearFlag):
        #     index = re.search(TH_YEAR_REGEX, date).start()
        #     date = re.sub(TH_YEAR_REGEX, '', date)
        #
        #     actual = int(yearValue[0])
        #     finalString = date[:index] + ' ' + str(actual) + 'th' + ' ' + date[index:]
        #
        #     random1 = randint(1, 3)
        #     op = -1 if randint(0, 4) < 2 else 1
        #     option1 = date[:index] + ' ' + str(actual + op * random1) + 'th' + ' ' + date[index:]
        #
        #     random2 = randint(1, 3)
        #     op = -1 if randint(0, 4) < 2 else 1
        #     option2 = date[:index] + ' ' + str(actual + op * random2) + 'th' + ' ' + date[index:]
        # # print([finalString , option1 , option2])
        #     return [removeTrailingSpace(finalString), removeTrailingSpace(option1), removeTrailingSpace(option2)]

    except Exception as ex:
        raise ex
