from dependencies.ElternportalCrawler import crawler
from dependencies.GoogleCalendar import calendar
from dependencies.Logger import write_log
from dependencies.ConfigReader import config
import time


class App:
    def add_exams_to_calendar(self, exams):
        for exam in exams:
            calendar.create_event(exam.title, exam.start_date)

    def do_first_run(self, previous_exams):
        if len(previous_exams) == 0:
            return True
        return False

    def title_counter(self, exams, title):
        counter = 0
        for exam in exams:
            if exam.title == title:
                counter += 1
        return counter

    def safe_list_get(self, exams, index):
        try:
            return exams[index]
        except IndexError:
            return None

    def longest_list(self, exams, previous_exams):
        if len(previous_exams) > len(exams):
            return previous_exams
        return exams

    def check_for_updates(self, exams, previous_exams):
        exam_shift = 0
        previous_exam_shift = 0
        index = 0
        # The "+ (exam_shift + previous_exam_shift)" in the next line is making it so that if there are two wrong
        # entries checking each other that the list is extended by one so that the program can find both the errors and
        # correct them. That only works if the two wrong entries checking themselves happen to be the last ones.
        while index < len(self.longest_list(exams, previous_exams)) + (exam_shift + previous_exam_shift):
            exam = self.safe_list_get(exams, index - exam_shift)
            previous_exam = self.safe_list_get(previous_exams, index - previous_exam_shift)

            if exam is None and previous_exam is None:
                break
            elif exam is None:
                calendar.delete_event(previous_exam.event_id)
            elif previous_exam is None:
                calendar.create_event(exam.title, exam.start_date)
            elif exam.title == previous_exam.title and exam.start_date != previous_exam.start_date:
                calendar.update_event(previous_exam.event_id, exam.title, exam.start_date)
            elif exam.title != previous_exam.title:
                if self.title_counter(exams, exam.title) > self.title_counter(previous_exams, exam.title):
                    calendar.create_event(exam.title, exam.start_date)
                    previous_exam_shift += 1
                elif self.title_counter(exams, previous_exam.title) < self.title_counter(previous_exams, previous_exam.title):
                    calendar.delete_event(previous_exam.event_id)
                    exam_shift += 1
            index += 1

    def loop(self):
        while True:
            exams = crawler.fetch_exams()
            previous_exams = calendar.fetch_events()

            if self.do_first_run(previous_exams):
                self.add_exams_to_calendar(exams)
            else:
                self.check_for_updates(exams, previous_exams)
            time.sleep(config.wait_between_check)

    def run(self):
        try:
            self.loop()
        except KeyboardInterrupt:
            exit(0)
        except Exception as exception:
            try:
                time.sleep(config.wait_between_error)
            except KeyboardInterrupt:
                exit(0)


if __name__ == "__main__":
    app = App()
    app.run()
