import requests
from dependencies.ConfigReader import config
from dependencies.Logger import write_log


class Check:
    def __init__(self):
        self.__headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:79.0) Gecko/20100101 "
                                        "Firefox/79.0"}

    # checks if you can connect to the internet
    def __check_internet_connection(self):
        try:
            requests.get("https://www.google.de", timeout=10, headers=self.__headers)
        except Exception:
            return False
        return True

    def __check_elternportal_logindata(self):
        with requests.session() as s:
            login_data = {"username": config.email,
                          "password": config.password}

            r = s.get(config.url, timeout=10, headers=self.__headers)
            r = s.post(config.post_url, data=login_data, timeout=10, headers=self.__headers)

            if "Benutzername/Passwort inkorrekt." in r.text:
                return False
            return True

    # checks if we get the 200 respond code
    def __check_response_code(self):
        code = requests.get(config.url, timeout=10, headers=self.__headers)
        if "200" in str(code):
            return True
        return False

    # returns False if any of the checks fail. Else returns True.
    def do_the_check(self):
        try:
            if self.__check_internet_connection() is False:
                print("There appears to be no internet connection!")
                write_log("There appears to be no internet connection!")
                return False
            if self.__check_response_code() is False:
                print(f"{config.url} could not be reached.")
                write_log(f"{config.url} could not be reached.")
                return False
            if self.__check_elternportal_logindata() is False:
                print("The login data for the elternportal website is wrong.")
                write_log("The login data for the elternportal website is wrong.")
                return False
            return True
        except Exception as e:
            print("An Error Occurred.")
            print(e)
            write_log("An Error Occurred.", e, "Application terminated.")
            exit(0)


check = Check()
