import os
import datetime
from tqdm import tqdm
from datetime import timedelta, date
from collections import Counter
import humanize


def makedir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print("Directory ", dir_name, " Created ")
    else:
        print("Directory ", dir_name, " already exists")


def decorator_timeit(func):
    def wrapper():
        start_time = datetime.datetime.today()
        print(start_time.strftime("%H:%M:%S"))

        func()

        end_time = datetime.datetime.today()
        print(end_time.strftime("%H:%M:%S"))
        print(humanize.naturaltime(end_time - start_time))

    return wrapper
