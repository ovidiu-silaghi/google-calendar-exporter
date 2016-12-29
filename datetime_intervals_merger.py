from __future__ import print_function
from dateutil import parser

import csv
import datetime

def create_datetime_interval(date_str, start_time_str, end_time_str):
    start = parser.parse(date_str + " " + start_time_str)
    end = parser.parse(date_str + " " + end_time_str)
    return (start, end)

def import_intervals_from_csv(csv_filename):
    days_intervals = dict()
    with open(csv_filename) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            interval = create_datetime_interval(
                row["start date"], row["start time"], row["end time"])
            intervals = days_intervals.get(row["start date"], [])
            intervals.append(interval)
            days_intervals[row["start date"]] = intervals
    return days_intervals

def create_intervals():
    interval1 = create_datetime_interval("2016-01-01", "09:00", "09:30")
    interval2 = cpreate_datetime_interval("2016-01-01", "10:00", "10:30")
    interval3 = create_datetime_interval("2016-01-01", "10:30", "11:30")
    interval4 = create_datetime_interval("2016-01-01", "11:00", "11:30")
    interval5 = create_datetime_interval("2016-01-01", "11:15", "12:30")
    interval6 = create_datetime_interval("2016-01-01", "14:00", "15:00")
    interval7 = create_datetime_interval("2016-01-01", "15:00", "17:00")
    interval8 = create_datetime_interval("2016-01-01", "16:00", "17:00")
    interval9 = create_datetime_interval("2016-01-01", "16:30", "17:00")

    return [interval1, interval2, interval3, interval4, interval5, interval6,
           interval7, interval8, interval9]

def drop_dict_to_csv(input_dict, csv_filename):
    header_names = ["day", "total meetings duration"]
    with open(csv_filename, "w") as csv_file:
        writer = csv.DictWriter(csv_file, header_names)
        writer.writeheader()
        for day, duration in input_dict.iteritems():
            writer.writerow({"day": day, "total meetings duration": duration})

def main():
    days_intervals = import_intervals_from_csv("meetings-2016-gs-exported.csv")
    hours_per_days = dict()
    for day, intervals in days_intervals.iteritems():
        index = 0
        previous_end = None
        delta = datetime.timedelta(0)
        while (index < len(intervals)):
            start, end = intervals[index]
            if previous_end:
                delta_intervals = start - previous_end
                if delta_intervals.total_seconds() > 0:
                    delta += end - start
                else:
                    delta += end - previous_end
            else:
                delta += end - start
            previous_end = end
            index += 1
        hours_per_days[day] = delta.total_seconds()/60
    drop_dict_to_csv(hours_per_days, "2016 total meetings duration per day.csv")
    import ipdb; ipdb.set_trace()


if __name__ == "__main__":
    main()
