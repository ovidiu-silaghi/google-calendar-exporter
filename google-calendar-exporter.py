# script assumes everything runs smoothly so minimal error handling was added

from __future__ import print_function

import csv
import datetime
import json
import os

import httplib2
from apiclient import discovery
from oauth2client.file import Storage
from oauth2client import client
from oauth2client import tools

from dateutil import parser

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
GC_SECRET_CREDENTIALS_FILE = 'gc-oauth-credentials.json'
APPLICATION_NAME = "Google Calendar Exporter"
GC_CALENDAR_ID = "primary"


def get_gc_credentials():

    def get_credentials_path():
        home_dir = os.path.expanduser('~')
        credentials_dir = os.path.join(home_dir, '.gc-credentials')
        if not os.path.exists(credentials_dir):
            os.makedirs(credentials_dir)
        return os.path.join(
            credentials_dir, 'google-calendar-credentials.json')

    credentials_path = get_credentials_path()

    store = Storage(credentials_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(
            GC_SECRET_CREDENTIALS_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('[INFO]: Storing GC credentials to ' + credentials_path)
    return credentials

def get_gc_api_service():
    credentials = get_gc_credentials()
    http = credentials.authorize(httplib2.Http())
    return discovery.build('calendar', 'v3', http=http)

def convert_to_datetime(datetime_str):
    return parser.parse(datetime_str)

def get_gc_events(start_date_str="2016-01-01",
                  end_date_str="2016-12-31"):
    events = []
    page_token = None
    # converting string->datetime->string, just for readability sake
    start_date = convert_to_datetime(start_date_str).isoformat() + "Z"
    end_date = convert_to_datetime(end_date_str).isoformat() + "Z"
    gc_service = get_gc_api_service()

    while True:
        # gc list method docs:
        # https://developers.google.com/resources/api-libraries/documentation/
        # calendar/v3/python/latest/calendar_v3.events.html#list
        calendar_list = gc_service.events().list(
            calendarId=GC_CALENDAR_ID, timeMin=start_date, timeMax=end_date,
            alwaysIncludeEmail=True, singleEvents=True, pageToken=page_token,
            orderBy="startTime").execute()
        events.extend(calendar_list["items"])
        page_token = calendar_list.get("nextPageToken")
        if not page_token:
            break
    return events

def display_info_on_written_data(nb_of_records, filename):
    print("[INFO]: {} google calendar events were written to file: {}"
          .format(nb_of_records, filename))

def drop_obj_to_json(obj, filename):
    with open(filename, "w") as json_file:
        json.dump(obj, json_file)
    display_info_on_written_data(len(obj), filename)

def drop_gc_events_to_csv(gc_events, filename):

    def create_csv_row(event):
        start_datetime = convert_to_datetime(
            event.get("start", "").get("dateTime", ""))
        end_datetime = convert_to_datetime(
            event.get("end", "").get("dateTime", ""))
        created_datetime = convert_to_datetime(
            event.get("created", "").encode("utf-8"))
        return {"summary": event.get("summary", ""),
                "creator email": event.get("creator", "").get("email", ""),
                "created date": created_datetime.date(),
                "created time": created_datetime.time(),
                "start date": start_datetime.date(),
                "start time": start_datetime.time(),
                "end date": end_datetime.date(),
                "end time": end_datetime.time(),
                "nb of attendees": len(event.get("attendees", "")),
                "location": event.get("location", ""),
                "status": event.get("status", ""),
                "description": event.get("description", "").encode("utf-8")}

    header_names = ["summary", "creator email", "created date", "created time",
                    "start date", "start time", "end date", "end time",
                    "nb of attendees", "location", "status", "description"]

    with open(filename, "w") as csv_file:
        writer = csv.DictWriter(csv_file, header_names)
        writer.writeheader()
        for event in gc_events:
            try:
                writer.writerow(create_csv_row(event))
            except UnicodeEncodeError as exc:
                print("[ERROR]: " + str(exc))
    display_info_on_written_data(len(gc_events), filename)

def main():
    all_events = get_gc_events()

    export_filename = "gc-meetings"
    drop_obj_to_json(all_events, export_filename + ".json")
    drop_gc_events_to_csv(all_events, export_filename + ".csv")

if __name__ == "__main__":
    main()








