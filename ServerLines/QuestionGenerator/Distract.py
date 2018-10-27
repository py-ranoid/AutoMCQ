from dateutil.parser import parse
from random import sample , randint
import re
from Constants import *
from YetAnotherException import ServerError
import traceback
TIME_ENTITIES = ["Year", "Month", "Day", "Week", "Decade", "Millenium"]

YEAR_CONSTANT = 'YEAR'
DATE_CONSTANT = 'DATE'
MONTH_CONSTANT = 'MONTH'
CENT_CONSTANT = 'CENT'
S_YEAR_REGEX = r'([12][0-9]{3})s'
YEAR_REGEX = r'[12][0-9]{3}'
DATE_REGEX = r'[12]?[0-9]|3[01]'
YEAR_REGEX = r'[12][0-9]{3}'
TH_YEAR_REGEX = r'([0-9]{2})th'
ZERO = '0'
ONE = '1'

short_months = [ x[:3] for x in MONTH_LIST ]
MONTH_REGEX = r'(' + "|".join(MONTH_LIST) + "|" + ("|".join(MONTH_LIST)).lower() + "|" + "|".join(short_months) + "|" + ("|".join(short_months)).lower() + ')'


def removeTrailingSpace(content):
    content = content[:-1] if content[-1] == ' ' else content
    return content

def normalDateDistract(answer):
    try:


        date = answer

        yearValue = re.findall(YEAR_REGEX, date)

        parsedDate = parse(date)

        DATE_REGEX = r'[12]?[0-9]|3[01]'

        short_months = [x[:3] for x in MONTH_LIST]
        MONTH_REGEX = r'(' + "|".join(MONTH_LIST) + "|" + ("|".join(MONTH_LIST)).lower() + "|" + "|".join(
            short_months) + "|" + ("|".join(short_months)).lower() + ')'

        # There is a single date that must be modified
        date = re.sub(YEAR_REGEX, YEAR_CONSTANT, date)
        yearFlag = True if len(yearValue) > 0 else False

        monthValue = re.findall(MONTH_REGEX, date)
        date = re.sub(MONTH_REGEX, MONTH_CONSTANT, date)

        dateValue = re.findall(DATE_REGEX, date)
        date = re.sub(DATE_REGEX, DATE_CONSTANT, date)

        monthFlag = True if len(monthValue) > 0 else False
        dateFlag = True if len(dateValue) > 0 else False

        option1 = date
        option2 = date

        print(date)

        if (dateFlag):
            random1, random2 = -1, -1
            while random1 == random2:
                random1, random2 = sample(range(1, 29), 2)

            option1 = option1.replace(DATE_CONSTANT, str(random1))
            option2 = option2.replace(DATE_CONSTANT, str(random2))

        if (monthFlag):
            actual = int(parsedDate.month)
            random1, random2 = actual, actual

            while random1 == random2 or random1 == actual or random2 == actual:
                random1, random2 = sample(range(0, 12), 2)

            option1 = option1.replace(MONTH_CONSTANT, MONTH_LIST[random1])
            option2 = option2.replace(MONTH_CONSTANT, MONTH_LIST[random2])

        if (yearFlag):
            lowerMonth = 1
            upperMonth = 4
            actual = int(parsedDate.year)
            if (monthFlag):
                random1 = randint(0, 1)
                random2 = -1 * randint(0, 1)
                option1 = option1.replace(YEAR_CONSTANT, str(random1 + actual))
                option2 = option2.replace(YEAR_CONSTANT, str(random2 + actual))


            else:

                random1, random2 = randint(lowerMonth, upperMonth), randint(lowerMonth, upperMonth)
                op = -1 * random1 if randint(0, 4) < 3 else random1
                option1 = option1.replace(YEAR_CONSTANT, str(actual+op))
                op = -1 * random2 if randint(0, 4) < 3 else random2
                option2 = option2.replace(YEAR_CONSTANT, str(actual+op))

                print(option1  ,option2)

        return [removeTrailingSpace(answer), removeTrailingSpace(option1), removeTrailingSpace(option2)]

    except ValueError as ex:
        raise ex

def specialYearsDistract(answer):
    date = answer

    yearValue = re.findall(S_YEAR_REGEX, date)
    yearFlag = True if len(yearValue) > 0 else False

    centValue = re.findall(TH_YEAR_REGEX, date)
    centFlag = True if len(centValue) > 0 else False

    if (yearFlag):
        date = re.sub(YEAR_REGEX, YEAR_CONSTANT , date)

        actual = int(yearValue[0])
        option1 = date
        option2 = date

        random1 , random2 = -1 , -1
        while random1 == random2:
            random1 = -1 * randint(1 , 4) if randint(0,4) < 3 else randint(1 , 3)
            random2 = -1 * randint(1 , 4) if randint(0,4) < 3 else randint(1 , 3)

        random1 = str(actual + (random1 * 10))
        random2 = str(actual + (random2 * 10))

        option1 = option1.replace(YEAR_CONSTANT , random1)
        option2 = option2.replace(YEAR_CONSTANT , random2)

        return [removeTrailingSpace(answer), removeTrailingSpace(option1), removeTrailingSpace(option2)]


    elif(centFlag):
        date = re.sub(DATE_REGEX, CENT_CONSTANT, date)

        actual = int(centValue[0])
        option1 = date
        option2 = date

        random1, random2 = -1, -1
        while random1 == random2:
            random1 = -1 * randint(1, 3) if randint(0, 4) < 3 else randint(1, 3)
            random2 = -1 * randint(1, 3) if randint(0, 4) < 3 else randint(1, 3)

        random1 = str(actual + (random1))
        random2 = str(actual + (random2))

        option1 = option1.replace(CENT_CONSTANT, random1)
        option2 = option2.replace(CENT_CONSTANT, random2)


        return [removeTrailingSpace(answer), removeTrailingSpace(option1), removeTrailingSpace(option2)]

    else:
        raise ServerError("Special year case not covered: " + answer)


def rangeYearDistract(answer):
    date = answer

    YEAR_0 = YEAR_CONSTANT + ZERO
    YEAR_1 = YEAR_CONSTANT + ONE

    yearValue = re.findall(YEAR_REGEX, date)

    year0 = int(yearValue[0])
    year1 = int(yearValue[1])

    date = re.sub(YEAR_REGEX, YEAR_0, date , count= 1)
    date = re.sub(YEAR_REGEX, YEAR_1, date , count= 1)

    opt11, opt12 = -1, -1
    opt21, opt22 = -1, -1


    while opt11+opt21 >= opt12+opt22:

        while opt11 == opt12:
            opt11 = -1 * randint(1, 4) if randint(0, 4) < 2 else randint(1, 4)
            opt12 = -1 * randint(1, 4) if randint(0, 4) < 2 else randint(1, 4)

        opt11 += year0
        opt12 += year1

        while opt21 == opt22:
            opt21 = -1 * randint(1, 4) if randint(0, 4) < 2 else randint(1, 4)
            opt22 = -1 * randint(1, 4) if randint(0, 4) < 2 else randint(1, 4)

        opt21 += year0
        opt22 += year1


    option1 , option2 = date , date
    option1 = option1.replace(YEAR_0 , str(opt11))
    option1 = option1.replace(YEAR_1 , str(opt12))
    option2 = option2.replace(YEAR_0 , str(opt21))
    option2 = option2.replace(YEAR_1 , str(opt22))

    return [removeTrailingSpace(answer), removeTrailingSpace(option1), removeTrailingSpace(option2)]



def datesDistract(answer):
    date = answer
    yearValue = re.findall(YEAR_REGEX, date)

    if (len(yearValue) <= 1):
        try:
            print('Date try')
            options = normalDateDistract(date)
            return options
        except ValueError as ex:
            #The input could be like 1990s etc
            print('Special Year try')
            options = specialYearsDistract(date)
            return options
        except Exception as ex:
            traceback.print_exc()
            raise ServerError(NEW_ERROR + str(ex))

    elif (len(yearValue) == 2):
        #There is a range and that must be replaced
        options = rangeYearDistract(date)
        return options


def datesDistract2(date):

    try:
        parse(date)

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
            random1 , random2 = -1 , -1
            while random1 == random2:
                random1, random2 = sample(range(1 , 29) , 2)

            option1 += str(random1) + ' '
            option2 += str(random2)+ ' '

        if (monthFlag):
            finalString += monthValue[0] + ' '

            actual = monthValue[0]
            random1, random2 = actual, actual

            while random1 == random2 or random1 == actual or random2 == actual:
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
