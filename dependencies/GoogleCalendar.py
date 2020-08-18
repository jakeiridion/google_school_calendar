import pickle
import os
from dependencies.Logger import write_log
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from datetime import datetime
from dependencies.ConfigReader import config
from dependencies.ElternportalCrawler import CrawledExam


class Calendar:
    def __init__(self):
        self.__scopes = ["https://www.googleapis.com/auth/calendar"]
        self.__calendar_name = config.calendar_name
        self.__client_secret_path = config.client_secret_path
        self.dependencies_path = os.path.dirname(__file__)
        self.__token_path = os.path.join(self.dependencies_path, "token.pkl")
        self.__calendar_id_path = os.path.join(self.dependencies_path, "calendarID.txt")

    # if the token is already saved returns true else returns false
    def __is_already_authenticated(self):
        if os.path.isfile(self.__token_path):
            return True
        return False

    # unpickle the token.pkl file
    def __load_credentials(self):
        with open(self.__token_path, "rb") as file:
            return pickle.load(file)

    # saves credentials
    def __save_credentials(self, credentials):
        with open(self.__token_path, "wb") as file:
            pickle.dump(credentials, file)
            write_log("authorization token saved in " + self.__token_path)
            print("")
            print("The token has been created. You can now exit the app and run it with:")
            print("sudo nohup python3 main.py &")
            print("Or wait until the rest of the calendar was updated")
            print("Read the log for information on the current process")
            print("")

    # return the token credentials or creates new ones
    def __google_authentication(self):
        if self.__is_already_authenticated() is True:
            return self.__load_credentials()
        else:
            try:
                write_log("Authorizing the application.")
                flow = InstalledAppFlow.from_client_secrets_file(self.__client_secret_path, scopes=self.__scopes)
                flow.run_console(access_type='offline')
                self.__save_credentials(flow.credentials)
                return flow.credentials
            except InvalidGrantError:
                write_log("Invalid authorization code.")
                exit()

    # creates a service with the token
    def __create_sevice(self):
        credentials = self.__google_authentication()
        service = build("calendar", "v3", credentials=credentials)
        return service

    # saves the calendar id in a text file
    def __save_calendar_id(self, id):
        with open(self.__calendar_id_path, "w") as file:
            file.write(id)

    # loads the calendar id from the text file
    def __load_calendar_id(self):
        with open(self.__calendar_id_path, "r") as file:
            return file.readline().strip()

    # checks if the calendar id file exists
    def __does_calendar_id_file_exist(self):
        if os.path.isfile(self.__calendar_id_path) is True:
            return True
        return False

    # creates a new calendar with the specified timezone and the name HLTV CSGO Events
    def __create_new_calendar(self):
        service = self.__create_sevice()
        calendar_body = {
            'summary': self.__calendar_name,
        }
        created_calendar = service.calendars().insert(body=calendar_body).execute()
        calendar_id = created_calendar["id"]
        self.__save_calendar_id(calendar_id)
        write_log("Created new Calendar.", "Calendar-ID: " + calendar_id,
                  "Calendar-ID has been stored in " + self.__calendar_id_path)
        return calendar_id

    # returns the calendar_id either from the file or from a newly created calendar
    def __get_calendar_id(self):
        if self.__does_calendar_id_file_exist() is True:
            return self.__load_calendar_id()
        return self.__create_new_calendar()

    # creates a new event
    def create_event(self, title, start_time):
        service = self.__create_sevice()
        calender_id = self.__get_calendar_id()

        event = {
            'summary': title,
            'start': {
                'date': start_time.strftime("%Y-%m-%d"),
            },
            'end': {
                'date': start_time.strftime("%Y-%m-%d"),
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 1440},
                ],
            },
        }

        event = service.events().insert(calendarId=calender_id, body=event).execute()
        event_id = event["id"]
        write_log("Event created.", "Event-ID: " + event_id)
        return event_id

    # fetches all events on the google calendar
    def fetch_events(self):
        calendar_events = []
        page_token = None
        service = self.__create_sevice()
        while True:
            events = service.events().list(calendarId=self.__get_calendar_id(), pageToken=page_token).execute()
            for event in events['items']:
                title = event["summary"]
                start_time = self.__turn_into_date_obj(event['start']["date"])
                event_id = event["id"]
                calendar_events.append(CrawledExam(title, start_time, event_id))
            page_token = events.get('nextPageToken')
            if not page_token:
                break
        write_log("Crawling all events from the google calendar.")

        calendar_events.sort(key=lambda exam: (exam.title.lower(), exam.start_date))
        return calendar_events

    def delete_event(self, event_id):
        service = self.__create_sevice()
        calendar_id = self.__get_calendar_id()
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        write_log("Event deleted.", "Deleted-Event-ID: " + event_id)

    # this update method first deletes and than creates a new event
    def update_event(self, event_id, new_title, new_start_time):
        self.delete_event(event_id)
        new_event_id = self.create_event(new_title, new_start_time)
        return new_event_id

    # turns a str into a datetime object
    def __turn_into_date_obj(self, date_str):
        return datetime.strptime(date_str, "%Y-%m-%d")


calendar = Calendar()
