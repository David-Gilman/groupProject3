import calendar
import re
from datetime import datetime
from timeit import default_timer as timer
import json


def main():
    while True:
        try:
            fo = open("http_access_log", "r")
            print("Searching log...")
            break
        except IOError:
            import urllib.request
            print("Log not found")
            print("Downloading log...")
            urllib.request.urlretrieve("https://s3.amazonaws.com/tcmg412-fall2016/http_access_log", "http_access_log")
            print("Log retrieved\n")

    start = timer()
    months_list = []
    '''for i in range(1, 13):
        months_list.append(datetime.date(2017, i, 1).strftime('%B'))'''
    requests, fail, redirect, bad = 0, 0, 0, 0
    files, weekday, week, month = {}, {}, {}, {}
    for i in range(0, 7):
        weekday[i] = 0
    for i in range(0, 52):
        week[i] = 0
    for i in range(0, 12):
        month[i] = 0
    conv = dict((v, k) for k, v in enumerate(calendar.month_abbr))
    reg = re.compile('.*\[([^:]*):(.*) -\d{3,4}\].*')

    for line in fo:
        try:
            if line.split()[8][0] == "4":
                fail += 1
            elif line.split()[8][0] == "3":
                redirect += 1
            if line.split()[6] in files:
                files[line.split()[6]] += 1
            else:
                files[line.split()[6]] = 1
            requests += 1
            event = datetime.strptime(reg.match(line).groups()[0], '%d/%b/%Y')
            weekday[event.weekday()] += 1
            week[event.isocalendar()[1] - 1] += 1
            month[event.month - 1] += 1
            with open(calendar.month_name[event.month]+".log", "a+") as curr:
                curr.write(line)
                curr.close()


        except IndexError:
            bad += 1
            pass

    fo.close()

    f = open('weeks.json', 'w+')
    f.truncate()
    f.write(json.dumps(week))
    f.close()

    f = open('orphans.txt', 'w+')
    f.truncate()
    for fi in files:
        if files[fi] == 1:
            f.write(fi + ', ')
    f.close()

    end = timer()
    print(str(round(end - start)) + " Seconds for processing\n")
    print("Invalid log entries: " + str(bad) + " representing " + str(round((bad / (bad + requests)), 4) * 100) + "%\n")
    print("1. Total requests: " + str(requests))
    print("2. Requests per day: ")
    for i in range(7):
        print('\t' + str(calendar.day_abbr[i]) + ': ' + str(weekday[i]))
    print("Requests per week are saved in json file \"weeks.JSON\"")
    print("Requests per month: ")
    for i in range(12):
        print('\t' + str(calendar.month_abbr[i + 1]) + ': ' + str(month[i]))
    print("3. Unsuccessful requests: " + str(round((fail / requests), 4) * 100) + "%")
    print("4. Redirected requests: " + str(round((redirect / requests), 4) * 100) + "%")
    print("5. Most requested file: " + max(files, key=files.get))
    print("6. Files requested only once are stored in orphans.txt")
    print("See this directory for 12 .log files, each storing the data for the proper month\n")


if __name__ == '__main__':
    main()
# iremote - - [13/Feb/1995:10:48:26 -0700] "GET index.html HTTP/1.0" 200 9902
