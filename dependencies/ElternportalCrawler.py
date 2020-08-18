from bs4 import BeautifulSoup
import requests
from datetime import datetime
from dependencies.ConfigReader import config
from dependencies.Logger import write_log


class CrawledExam:
    def __init__(self, title, start_date, event_id=None):
        self.title = title
        self.start_date = start_date
        self.event_id = event_id


class Crawler:
    def __init__(self):
        self.url = "https://klengymuc.eltern-portal.org/"
        self.post_url = "https://klengymuc.eltern-portal.org/includes/project/auth/login.php"
        self.end_url = "https://klengymuc.eltern-portal.org/service/termine/liste"
        self.payload = {"username": config.email,
                        "password": config.password}

    def check_elternportal_logindata(self, response):
        if "Benutzername/Passwort inkorrekt." in response:
            print("Wrong login information")
            exit(0)

    def login(self, session):
        r = session.get(self.url)
        r = session.post(self.post_url, data=self.payload)
        self.check_elternportal_logindata(r.text)

    def fetch_soup(self):
        with requests.session() as session:
            self.login(session)
            r = session.get(self.end_url)
            soup = BeautifulSoup(r.text, "html.parser")
            return soup

    def format_date(self, date_str):
        return datetime.strptime(date_str, "%d.%m.%Y")

    def fetch_exams(self):
        soup = self.fetch_soup()
        exams = []

        for row in soup.find_all("tr"):
            if str(row).startswith("<tr><tr>") or "<h2>" in str(row) or "<h4>" in str(row):
                continue
            title = row.find_all("td")[-1].text.strip()
            date_str = row.find_all("td")[0].text.strip()
            start_date = self.format_date(date_str)
            exams.append(CrawledExam(title, start_date))

        exams.sort(key=lambda exam: (exam.title.lower(), exam.start_date))
        return exams


crawler = Crawler()
