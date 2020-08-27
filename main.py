from dependencies.ElternportalCrawler import crawler
from dependencies.GoogleCalendar import calendar
from dependencies.Logger import write_log
from dependencies.ConfigReader import config
from dependencies.FirstCheck import check
import time
import concurrent.futures


class App:
    # Adds all exams in a list to the google calendar.
    def __add_exams_to_calendar(self, exams):
        for exam in exams:
            calendar.create_event(exam.title, exam.start_date)

    # Checks if the calendar is empty.
    def __is_calendar_empty(self, previous_exams):
        if len(previous_exams) == 0:
            return True
        return False

    # Counts the titles in one of the lists
    def __title_counter(self, exams, title):
        counter = 0
        for exam in exams:
            if exam.title == title:
                counter += 1
        return counter

    # returns a value from a list if an error occurred it returns None.
    # Like .get from dictionary but for lists.
    def __safe_list_get(self, exams, index):
        try:
            return exams[index]
        except IndexError:
            return None

    # returns the longest list out of two.
    def __longest_list(self, exams, previous_exams):
        if len(previous_exams) > len(exams):
            return previous_exams
        return exams

    # Checks both list for updates.
    def __check_for_updates(self, exams, previous_exams):
        exam_shift = 0
        previous_exam_shift = 0
        index = 0
        # The "+ (exam_shift + previous_exam_shift)" in the next line is making it so that if there are two wrong
        # entries checking each other that the list is extended by one so that the program can find both the errors and
        # correct them. That only works if the two wrong entries checking themselves happen to be the last ones and if
        # exactly as many events get deleted as created.
        while index < len(self.__longest_list(exams, previous_exams)) + (exam_shift + previous_exam_shift):
            # The exam and previous exam shifts balance out the list if something new or old was found.
            # Because that means that if for example a new exam is inserted into the exam list the following exams will
            # be out of order by one.
            exam = self.__safe_list_get(exams, index - exam_shift)
            previous_exam = self.__safe_list_get(previous_exams, index - previous_exam_shift)

            # Whenever something is added or deleted the length of the list is expand by one.
            # When something is added and deleted the length stays the same but it will still continue counting.
            # So it breaks if both times nothing is returned.
            if exam is None and previous_exam is None:
                break

            # If the last part of the list contains a old exam but not a new one it gets deleted.
            # (Just if it is the last one in the list tough.)
            elif exam is None:
                write_log("Outdated Exam detected.")
                calendar.delete_event(previous_exam.event_id)

            # If the last part of the list contains a new exam but not a old one it gets created.
            # (Just if it is the last one in the list tough.)
            elif previous_exam is None:
                write_log("New Exam detected.")
                calendar.create_event(exam.title, exam.start_date)

            # If the titles are the same but the date changed, the date will be updated.
            elif exam.title == previous_exam.title and exam.start_date != previous_exam.start_date:
                write_log("Exam date change detected")
                calendar.update_event(previous_exam.event_id, exam.title, exam.start_date)

            # If the names don't madge each other it is either a new exam or a outdated one.
            elif exam.title != previous_exam.title:
                # If the number of titles in exams is bigger than the one in the previous exams it means that a new
                # exam must be created.
                if self.__title_counter(exams, exam.title) > self.__title_counter(previous_exams, exam.title):
                    write_log("New Exam detected.")
                    calendar.create_event(exam.title, exam.start_date)
                    # A new exam was detected so the previous exams need to be moved back by one so that everything
                    # stays the same
                    previous_exam_shift += 1

                # If the number of titles in exams is smaller than the one in the previous exams it means that an
                # old title was found and it must be deleted.
                elif self.__title_counter(exams, previous_exam.title) < self.__title_counter(previous_exams,
                                                                                             previous_exam.title):
                    write_log("Outdated Exam detected.")
                    calendar.delete_event(previous_exam.event_id)
                    # A old exam was detected so the exams need to be moved back by one so that everything stays the
                    # same
                    exam_shift += 1
            index += 1

    def run(self):
        while True:
            try:
                # Threading for elternportal crawling while doing the google calendar crawler in the main thread.
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(crawler.fetch_exams)
                    previous_exams = calendar.fetch_events()
                    exams = future.result()
                # If the calendar is empty it means that this is the first time creating it.
                # So it needs to add all the exams to the calendar
                if self.__is_calendar_empty(previous_exams):
                    self.__add_exams_to_calendar(exams)
                # Otherwise it checks for updates.
                else:
                    write_log("Checking for updates")
                    self.__check_for_updates(exams, previous_exams)
                write_log(f"Waiting for {config.wait_between_check} seconds before continuing.")
                # wait for the number of seconds specified in the settings before proceeding.
                time.sleep(config.wait_between_check)
            except KeyboardInterrupt:
                write_log("Application terminated.")
                exit(0)
            except Exception as exception:
                try:
                    write_log("An Error Occurred.", exception,
                              f"Waiting for {config.wait_between_error} seconds before continuing.")
                    # After an error occurred the app will wait for the specified number of seconds before proceeding
                    # and trying it again.
                    time.sleep(config.wait_between_error)
                except KeyboardInterrupt:
                    write_log("Application terminated.")
                    exit(0)


if __name__ == "__main__":
    write_log("Application started.")
    # Checks the login data and the internet connection before proceeding.
    if check.do_the_check():
        app = App()
        app.run()
    write_log("Application terminated.")
