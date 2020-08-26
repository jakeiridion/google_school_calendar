from dependencies.ElternportalCrawler import crawler
from dependencies.GoogleCalendar import calendar
from dependencies.Logger import write_log
from dependencies.ConfigReader import config
from dependencies.FirstCheck import check
import time
import concurrent.futures


class App:
    def __add_exams_to_calendar(self, exams):
        for exam in exams:
            calendar.create_event(exam.title, exam.start_date)

    def __is_calendar_empty(self, previous_exams):
        if len(previous_exams) == 0:
            return True
        return False

    def __title_counter(self, exams, title):
        counter = 0
        for exam in exams:
            if exam.title == title:
                counter += 1
        return counter

    def __safe_list_get(self, exams, index):
        try:
            return exams[index]
        except IndexError:
            return None

    def __longest_list(self, exams, previous_exams):
        if len(previous_exams) > len(exams):
            return previous_exams
        return exams

    def __check_for_updates(self, exams, previous_exams):
        exam_shift = 0
        previous_exam_shift = 0
        index = 0
        # The "+ (exam_shift + previous_exam_shift)" in the next line is making it so that if there are two wrong
        # entries checking each other that the list is extended by one so that the program can find both the errors and
        # correct them. That only works if the two wrong entries checking themselves happen to be the last ones and if
        # exactly as many events get deleted as created.
        while index < len(self.__longest_list(exams, previous_exams)) + (exam_shift + previous_exam_shift):
            exam = self.__safe_list_get(exams, index - exam_shift)
            previous_exam = self.__safe_list_get(previous_exams, index - previous_exam_shift)

            if exam is None and previous_exam is None:
                break
            elif exam is None:
                write_log("Outdated Exam detected.")
                calendar.delete_event(previous_exam.event_id)
            elif previous_exam is None:
                write_log("New Exam detected.")
                calendar.create_event(exam.title, exam.start_date)
            elif exam.title == previous_exam.title and exam.start_date != previous_exam.start_date:
                write_log("Exam date change detected")
                calendar.update_event(previous_exam.event_id, exam.title, exam.start_date)
            elif exam.title != previous_exam.title:
                if self.__title_counter(exams, exam.title) > self.__title_counter(previous_exams, exam.title):
                    write_log("New Exam detected.")
                    calendar.create_event(exam.title, exam.start_date)
                    previous_exam_shift += 1
                elif self.__title_counter(exams, previous_exam.title) < self.__title_counter(previous_exams, previous_exam.title):
                    write_log("Outdated Exam detected.")
                    calendar.delete_event(previous_exam.event_id)
                    exam_shift += 1
            index += 1

    def run(self):
        while True:
            try:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(crawler.fetch_exams)
                    previous_exams = calendar.fetch_events()
                    exams = future.result()
                    executor.shutdown()
                if self.__is_calendar_empty(previous_exams):
                    self.__add_exams_to_calendar(exams)
                else:
                    write_log("Checking for updates")
                    self.__check_for_updates(exams, previous_exams)
                write_log(f"Waiting for {config.wait_between_check} seconds before continuing.")
                time.sleep(config.wait_between_check)
            except KeyboardInterrupt:
                write_log("Application terminated.")
                exit(0)
            except Exception as exception:
                try:
                    write_log("An Error Occurred.", exception,
                              f"Waiting for {config.wait_between_error} seconds before continuing.")
                    time.sleep(config.wait_between_error)
                except KeyboardInterrupt:
                    write_log("Application terminated.")
                    exit(0)


if __name__ == "__main__":
    write_log("Application started.")
    if check.do_the_check():
        app = App()
        app.run()
    write_log("Application terminated.")
