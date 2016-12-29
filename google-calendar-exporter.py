from __future__ import print_function

import csv
import datetime
import httplib2
import json
import os


from apiclient import discovery
from dateutil import parser
from oauth2client.file import Storage
from oauth2client import client
from oauth2client import tools

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'gc-oauth-credentials.json'
APPLICATION_NAME = "Google Calendar Exporter"
CALENDAR_ID = "primary"

def get_gc_credentials():
    home_dir = os.path.expanduser('~')
    credentials_dir = os.path.join(home_dir, '.gc-credentials')
    if not os.path.exists(credentials_dir):
        os.makedirs(credentials_dir)
    credentials_path = os.path.join(credentials_dir, 'google-calendar-credentials.json')

    store = Storage(credentials_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('[INFO]: Storing credentials to ' + credentials_path)
    return credentials

def create_date_obj(day, month, year):
    return datetime.datetime(year, month, day, 01, 01, 01, 0).isoformat() + 'Z'

def get_gc_api_service():
    credentials = get_gc_credentials()
    http = credentials.authorize(httplib2.Http())
    return discovery.build('calendar', 'v3', http=http)


def get_gc_events():
    ret = []
    page_token = None
    start_date = create_date_obj(01, 01, 2016)
    end_date = create_date_obj(31, 12, 2016)
    gc_service = get_gc_api_service()
    while True:
        # list method docs:
        # https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/calendar_v3.events.html#list
        calendar_list = gc_service.events().list(
            calendarId=CALENDAR_ID, timeMin=start_date, timeMax=end_date,
            alwaysIncludeEmail=True,singleEvents=True, orderBy="startTime",
            pageToken=page_token).execute()
        ret.extend(calendar_list["items"])
        page_token = calendar_list.get("nextPageToken")
        if not page_token:
            break
    return ret

def display_info_on_written_data(nb_of_records, filename):
    print("[INFO]: {} google calendar events were written to file: {}".format(
        nb_of_records, filename))

def drop_dict_to_json(input_dict, filename):
    with open(filename, "w") as file:
        json.dump(input_dict, file)
    display_info_on_written_data(len(input_dict), filename)

def convert_to_datetime(datetime_str):
    return parser.parse(datetime_str)

def drop_dict_to_csv(input_dict, filename):
    header_names=["summary", "creator email", "created date", "created time",
                  "start date", "start time", "end date", "end time", "nb of attendees",
                  "location", "status", "description"]
    with open(filename, "w") as file:
        writer = csv.DictWriter(file, header_names)
        writer.writeheader()
        for event in input_dict:
            try:
                start_datetime = convert_to_datetime(event.get("start", "").get("dateTime", ""))
                end_datetime = convert_to_datetime(event.get("end", "").get("dateTime", ""))
                created_datetime = convert_to_datetime(event.get("created", "").encode("utf-8"))
                writer.writerow(
                    {"summary": event.get("summary",""),
                     "creator email": event.get("creator", "").get("email", ""),
                     "created date": created_datetime.date(),
                     "created time": created_datetime.time(),
                     "start date": start_datetime.date(),
                     "start time": start_datetime.time(),
                     "end date": end_datetime.date(),
                     "end time": end_datetime.time(),
                     "nb of attendees": len(event.get("attendees","")),
                     "location": event.get("location", ""),
                     "status": event.get("status", ""),
                     "description": event.get("description", "").encode("utf-8"),
                    })
            except UnicodeEncodeError as e:
                print("[ERROR]: " + str(e))
    display_info_on_written_data(len(input_dict), filename)

def main():
    all_events = get_gc_events()

    export_filename = "gc-meetings"
    drop_dict_to_json(all_events, export_filename + ".json")
    drop_dict_to_csv(all_events, export_filename + ".csv")

if __name__ == "__main__":
    main()








