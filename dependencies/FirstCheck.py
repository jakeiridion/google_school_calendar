import requests
from dependencies.ConfigReader import config
from dependencies.Logger import write_log


class Check:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:79.0) Gecko/20100101 "
                                      "Firefox/79.0"}

    # checks if you can connect to the internet
    def check_internet_connection(self):
        try:
            requests.get("https://www.google.de", timeout=10, headers=self.headers)
        except requests.exceptions.ConnectionError:
            return False
        return True

    def check_elternportal_logindata(self):
        with requests.session() as s:
            login_data = {"username": config.email,
                          "password": config.password}

            r = s.get(config.url, timeout=10, headers=self.headers)
            r = s.post(config.post_url, data=login_data, timeout=10, headers=self.headers)

            if "Benutzername/Passwort inkorrekt." in r.text:
                return False
            return True

    # checks if we get the 200 respond code
    def check_response_code(self):
        code = requests.get(config.url, timeout=10, headers=self.headers)
        if "200" in str(code):
            return True
        return False

    def do_the_check(self):
        try:
            if self.check_internet_connection() is False:
                print("There appears to be no internet connection!")
                return False
            if self.check_response_code() is False:
                print("Elternportal could not be reached.")
                return False
            if self.check_elternportal_logindata() is False:
                print("The login data for the elternportal website is wrong.")
                return False
            return True
        except Exception as e:
            print("An Error Occurred.")
            print(e)
            return False


check = Check()
