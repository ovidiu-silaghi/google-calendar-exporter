# script assumes everything runs smoothly, so no error handling added

from __future__ import print_function

import csv
import datetime

from dateutil import parser

def create_datetime_interval(date_str, start_time_str, end_time_str):
    start = parser.parse(date_str + " " + start_time_str)
    end = parser.parse(date_str + " " + end_time_str)
    return (start, end)

def import_intervals_from_csv(csv_filename):
    days_intervals = dict()
    with open(csv_filename) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            # assuming start date equals end date
            interval = create_datetime_interval(
                row["start date"], row["start time"], row["end time"])
            intervals = days_intervals.get(row["start date"], [])
            # assuming intervals from a specific day are ordered by start time
            intervals.append(interval)
            days_intervals[row["start date"]] = intervals
    return days_intervals

def merge_intervals_per_day(days_intervals):
    hours_per_days = dict()
    for day, intervals in days_intervals.iteritems():
        index = 0
        previous_end = None
        delta = datetime.timedelta(0)
        while index < len(intervals):
            start, end = intervals[index]
            if previous_end: # if not first interval
                delta_of_intervals = start - previous_end
                if delta_of_intervals.total_seconds() > 0:
                    delta += end - start
                else:
                    delta += end - previous_end
            else: # if first interval
                delta += end - start
            previous_end = end
            index += 1
        hours_per_days[day] = delta.total_seconds() / 60
    return hours_per_days

def drop_merged_intervals_to_csv(merged_intervals, csv_filename):
    header_names = ["day", "total meetings duration"]
    with open(csv_filename, "w") as csv_file:
        writer = csv.DictWriter(csv_file, header_names)
        writer.writeheader()
        for day, duration in merged_intervals.iteritems():
            writer.writerow({
                "day": day,
                "total meetings duration": duration})


def main():
    days_intervals = import_intervals_from_csv("sorted_days_intervals.csv")
    merged_intervals = merge_intervals_per_day(days_intervals)
    drop_merged_intervals_to_csv(
        merged_intervals, "merged_intervals_per_day.csv")

if __name__ == "__main__":
    main()
