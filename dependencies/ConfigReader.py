import configparser
import os
from dependencies.Logger import write_log


class Config:
    def __init__(self):
        try:
            # import Variables from the settings file
            cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "SETTINGS.ini")
            cfg = configparser.ConfigParser()
            cfg.read(cfg_path)

            self.calendar_name = str(cfg.get("Settings", "calendar_name"))
            self.email = str(cfg.get("Settings", "email"))
            self.password = str(cfg.get("Settings", "password"))
            self.client_secret_path = str(cfg.get("Settings", "client_secret.json_path"))
            self.wait_between_check = int(cfg.get("Settings", "wait_between_check"))
            self.wait_between_error = int(cfg.get("Settings", "wait_between_error"))

            # Is the email correct
            if "@" not in self.email:
                raise Exception("Email is incorrect.")

            # raises an exception if the path to the client secret file was entered incorrectly
            if os.path.isfile(self.client_secret_path) is False:
                raise Exception("No such file or directory: " + self.client_secret_path)

            # raises an exception if the time between the checks is negative or zero
            if self.wait_between_check <= 0 or self.wait_between_error <= 0:
                raise Exception("A Negative int or zero was set in the SETTINGS.ini file under the wait_between_... "
                                "section.")

            # raises an exception if the time is over a year = over 31622400 seconds
            if self.wait_between_check > 31622400 or self.wait_between_error > 31622400:
                raise Exception("The waiting time is over a year. It needs to be under, or 31622400 seconds.")

        except Exception as exception:
            print()
            print("An Error Occurred with your Settings:")
            print(exception)
            write_log("An Error Occurred with your Settings", exception)
            exit(0)


config = Config()
