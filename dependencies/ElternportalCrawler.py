from bs4 import BeautifulSoup
import requests
from datetime import datetime
from dependencies.ConfigReader import config
from dependencies.Logger import write_log


# A finished crawled exam object containing a title, a start date and an event id.
class CrawledExam:
    def __init__(self, title, start_date, event_id=None):
        self.title = title
        self.start_date = start_date
        self.event_id = event_id


class Crawler:
    def __init__(self):
        self.__payload = {"username": config.email,
                          "password": config.password}
        self.__headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:79.0) Gecko/20100101 "
                                        "Firefox/79.0"}

    # Using the session to login to elternportal.
    def __login(self, session):
        session.get(config.url, timeout=10, headers=self.__headers)
        session.post(config.post_url, data=self.__payload, timeout=10, headers=self.__headers)

    # returns the soup after the login and after it navigated to the exams list.
    def __fetch_soup(self):
        with requests.Session() as session:
            self.__login(session)
            r = session.get(config.end_url, timeout=10, headers=self.__headers)
            soup = BeautifulSoup(r.text, "html.parser")
            return soup

    # turns date string to datetime object.
    def __format_date(self, date_str):
        return datetime.strptime(date_str, "%d.%m.%Y")

    # returns the exams of the elternportal as a list containing CrawledExam objects.
    def fetch_exams(self):
        write_log("Crawling all exams from Elternportal.")
        soup = self.__fetch_soup()
        exams = []

        for row in soup.find_all("tr"):
            # Because the elternportal site contains "<tr><tr>" I need to ignore them.
            if str(row).startswith("<tr><tr>") or "<h2>" in str(row) or "<h4>" in str(row):
                continue
            title = row.find_all("td")[-1].text.strip()
            date_str = row.find_all("td")[0].text.strip()
            start_date = self.__format_date(date_str)
            exams.append(CrawledExam(title, start_date))

        # Sorts the list after the names first and then after the date.
        exams.sort(key=lambda exam: (exam.title.lower(), exam.start_date))
        return exams


crawler = Crawler()
