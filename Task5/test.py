import datetime

timestart = datetime.datetime.strptime('181013123123', "%H%M%S%f")
new_time = datetime.datetime.strptime('181028123123', "%H%M%S%f")

diff = new_time - timestart

if timestart == new_time:
    exit(0)

if diff.microseconds == 0:
    print('T = 1')

if diff.microseconds == 0 and diff.seconds % 5 == 0:
    print('T = 5')

if diff.microseconds == 0 and diff.seconds % 15 == 0:
    print('T = 15')

if diff.microseconds == 0 and diff.seconds % 30 == 0:
    print('T = 30')

if diff.microseconds == 0 and diff.seconds == 0:
    print('T = 60')