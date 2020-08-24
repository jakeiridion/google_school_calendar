from datetime import datetime
import os


# returns the current date
def __get_date():
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return date


# Write a entry in the log.txt file
def write_log(*texts):
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log.txt")
    with open(log_path, "a") as log:
        log.write(__get_date() + ":\n")

        # For every paragraph a new line is written in the log
        for text in texts:
            log.write(str(text) + "\n")

        log.write("\n")
