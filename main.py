# Paper - Digital Attendance Management System
#     Copyright (C) 2021-2023  Saurabh Kumar
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact: Saurabh Kumar <developer.saurabh@outlook.com>
#


import os.path
import subprocess

from csv import writer
from sys import exit
from time import strftime

try:
    import mysql.connector as server
    from PyQt6 import QtWidgets, QtCore, uic, QtGui
    from pyqtgraph import *

except ImportError:
    from tkinter import Tk, messagebox

    root = Tk()
    root.attributes("-topmost", True)
    root.overrideredirect(True)
    root.withdraw()

    messagebox.showerror(title="Paper - Cannot run app",
                         message="One or all of the following modules required to run the app were not found:\n\n"
                                 "PyQt6\n"
                                 "pyqtgraph\n"
                                 "mysql.connector\n\n"
                                 "If Python is added to Path, type: pip install <module> in your terminal " \
                                 "to install the modules.")
    exit()

data_server = server.connect(
    host="localhost",
    username="root",
    password="password"
)
data_server.autocommit = True
data_cursor = data_server.cursor(buffered=True)


def create_information_database():
    """Creates database to store all the information used by the app."""
    create_query = "CREATE DATABASE paper_information_database"
    data_cursor.execute(create_query)

    use_information_database()


def use_information_database():
    """Sets the working database to paper_information_database."""
    use_query = "USE paper_information_database"
    data_cursor.execute(use_query)


def create_attendance_database():
    """Creates database to store all the attendance records."""
    create_query = "CREATE DATABASE paper_attendance_database"
    data_cursor.execute(create_query)

    use_attendance_database()


def use_attendance_database():
    """Sets the working database to paper_attendance_database."""
    use_query = "USE paper_attendance_database"
    data_cursor.execute(use_query)


def create_reports_database():
    """Creates database to store all the attendance reports."""
    create_query = "CREATE DATABASE paper_reports_database"
    data_cursor.execute(create_query)

    use_reports_database()


def use_reports_database():
    """Sets the working database to paper_reports_database."""
    use_query = "USE paper_reports_database"
    data_cursor.execute(use_query)


def create_data_table():
    """Creates table to store the PIN and Class Name provided by the user."""
    use_information_database()

    create_query = "CREATE TABLE paper_data_table (" \
                   "pin varchar(4), " \
                   "class_name varchar(20)" \
                   ")"
    data_cursor.execute(create_query)


def create_student_list_table():
    """Creates table to store the name of all the students of a class."""
    use_information_database()

    create_table_query = "CREATE TABLE paper_student_list_table (" \
                         "name varchar(40) PRIMARY KEY" \
                         ")"
    data_cursor.execute(create_table_query)


def create_settings_table():
    """Creates table to store all the setting values."""
    use_information_database()

    create_query = "CREATE TABLE paper_settings_table (" \
                   "check_present varchar(1), " \
                   "minimum_attendance int(3), " \
                   "backup_frequency int(1), " \
                   "backup_date date" \
                   ")"
    data_cursor.execute(create_query)

    set_default_settings_query = "INSERT INTO paper_settings_table " \
                                 "VALUES ('N', 75, 2, date_add(curdate(), interval 30 day))"
    data_cursor.execute(set_default_settings_query)


def create_attendance_table(date: str):
    """
    Creates table to store the daily attendance record.

    :param date: Date for creating attendance table.
    """
    use_attendance_database()

    create_query = f"CREATE TABLE {date} (" \
                   "name varchar(40) PRIMARY KEY, " \
                   "state varchar(1)" \
                   ")"
    data_cursor.execute(create_query)


def create_student_report_table():
    """Creates table to store individual student attendance report."""
    use_reports_database()

    create_query = "CREATE TABLE paper_student_report_table (" \
                   "name varchar(40) PRIMARY KEY, " \
                   "total_days int(3), " \
                   "days_present int(3)" \
                   ")"
    data_cursor.execute(create_query)


def create_daily_report_table():
    """Creates table to store daily attendance report."""
    use_reports_database()

    create_query = "CREATE TABLE paper_daily_report_table (" \
                   "id int AUTO_INCREMENT PRIMARY KEY, " \
                   "date varchar(10) UNIQUE, " \
                   "present int(3), " \
                   "absent int(3), " \
                   "attendance_percentage decimal(4, 1)" \
                   ")"
    data_cursor.execute(create_query)


def set_class_name(class_name: str):
    """Updates the Class Name when it is renamed."""
    use_information_database()

    set_class_name_query = f"UPDATE paper_data_table SET class_name = '{class_name}'"
    data_cursor.execute(set_class_name_query)


def get_class_name() -> str or None:
    """
    Gets the name of the Class.

    :return: Class name.
    """
    use_information_database()

    try:
        get_class_name_query = "SELECT class_name FROM paper_data_table"
        data_cursor.execute(get_class_name_query)

        class_name = data_cursor.fetchone()[0]

        return class_name
    except TypeError:
        return None


def get_date() -> tuple[str, list[int]]:
    """
    Makes the current date available in 'DD_MM_YYYY' and [DD, MM, YYYY] format.

    :return: A tuple containing today's date in string and list format.
    """
    raw_date = strftime("%d-%m-%Y")
    raw_date = raw_date.split("-")
    # raw_date is used to set date on date_edit UI elements
    raw_date = [int(raw_date[i]) for i in range(len(raw_date))]

    date = "_".join(str(i) for i in raw_date)

    return date, raw_date


def get_pin() -> str or None:
    """
    Gets the current pin if it is available.

    :return: The current pin, if available, else None.
    """
    use_information_database()

    try:
        get_pin_query = "SELECT pin FROM paper_data_table"
        data_cursor.execute(get_pin_query)

        pin = data_cursor.fetchone()[0]
        return pin
    except TypeError:
        return None


def get_settings() -> dict:
    """
    Prepares list of current values for the application settings.

    :return: Dictionary containing settings and their corresponding values.
    """
    use_information_database()

    # Try to get settings.
    try:
        get_settings_query = "SELECT * FROM paper_settings_table"
        data_cursor.execute(get_settings_query)

    # If an error occurs, it means that the table does not exist.
    # So create the settings table and get settings.
    except server.ProgrammingError:
        create_settings_table()

        get_settings_query = "SELECT * FROM paper_settings_table"
        data_cursor.execute(get_settings_query)

    settings = data_cursor.fetchall()
    current_settings = {
        "check present": settings[0][0],
        "minimum attendance": settings[0][1],
        "backup frequency": settings[0][2],
        "backup date": settings[0][3]
    }
    return current_settings


def get_student_list(date: str = None) -> list:
    """
    Prepares list of students studying in the Class on the provided date.

    :param date: Date for preparing student list.
    :return: List of students.
    """
    student_list = list()

    # date = None means: get student list for today's date.
    if date is None:
        # Try to get the list of students.
        try:
            use_information_database()

            get_student_list_query = "SELECT * FROM paper_student_list_table"
            data_cursor.execute(get_student_list_query)

            data = data_cursor.fetchall()

        # If an error occurs, it means that the table is not created till now.
        # So return the empty student list.
        except server.ProgrammingError:
            return student_list
    else:
        # Try to get student list from past attendance records.
        try:
            use_attendance_database()

            get_student_list_from_records_query = f"SELECT name FROM {date}"
            data_cursor.execute(get_student_list_from_records_query)

            data = data_cursor.fetchall()

        # If an error occurs, it means that the attendance record for the
        # provided date does not exist.
        # So return the empty student list.
        except server.ProgrammingError:
            return student_list

    # If no error occurred, prepare student list from the data received from the database.
    for student in data:
        student_list.append(student[0])

    return student_list


def get_past_attendance_records() -> list:
    """
    Prepares list of all the tables present inside "paper_attendance_database".
    Each table is a day's attendance record.

    :return: List of all past attendance record tables.
    """
    attendance_records = list()

    # Get the list of all tables present inside the "paper_attendance_database" database.
    get_table_list_query = 'SELECT table_name FROM information_schema.tables ' \
                           'WHERE table_schema = "paper_attendance_database"'
    data_cursor.execute(get_table_list_query)

    data = data_cursor.fetchall()

    for record in data:
        attendance_records.append(record[0])

    return attendance_records


def rename_student_in_past_records(old_name: str, new_name: str):
    """
    Renames student in past attendance records after a naming change.

    :param old_name: Old name of the student.
    :param new_name: New name of the student.
    """
    # Try renaming student in today's attendance record.
    try:
        use_attendance_database()

        today = get_date()[0]
        update_query = f"UPDATE {today} SET name = '{new_name}' WHERE name = '{old_name}'"
        data_cursor.execute(update_query)

    # If an error occurs, it means that the attendance has not been recorded for the day.
    # Do nothing.
    except server.ProgrammingError:
        pass

    # Rename the student in past attendance records.
    attendance_records = get_past_attendance_records()
    for record in attendance_records:
        # Try renaming the student in all the past attendance records.
        try:
            update_name_in_past_record_table_query = f"UPDATE {record} " \
                                                     f"SET name = '{new_name}' " \
                                                     f"WHERE name = '{old_name}'"
            data_cursor.execute(update_name_in_past_record_table_query)

        # If an error occurs, it means that the student was not a part of the class till the
        # corresponding date.
        # Do nothing.
        except server.ProgrammingError:
            pass


def export_data():
    """Exports attendance data to external file on hard-disk."""
    export_data_dialog = ExportDataDialog()
    export_data_dialog.exec()


def write_daily_report(date: str):
    """
    Prepares/ updates attendance report for the provided date.

    :param date: The date for which report should be prepared.
    """
    use_attendance_database()

    # Get the number of students present on the provided date.
    get_present_count_query = f"SELECT count(*) FROM {date} WHERE state = 'P'"
    data_cursor.execute(get_present_count_query)
    present_count = data_cursor.fetchone()[0]

    # Get the number of students absent on the provided date.
    get_absent_count_query = f"SELECT count(*) FROM {date} WHERE state = 'A'"
    data_cursor.execute(get_absent_count_query)
    absent_count = data_cursor.fetchone()[0]

    # The total number of students is calculated as (present_count + absent_count) to get
    # the total number of students on the provided date.
    # Current total number of students may not always match with total number of students
    # on a given date back in time.
    # This is done to facilitate displaying report of a past date.
    attendance_percentage = round((present_count / (present_count + absent_count)) * 100, 2)

    # Try creating the daily report table.
    try:
        create_daily_report_table()

    # If an error occurs, it means that the table already exists.
    # Do nothing.
    except server.ProgrammingError:
        pass

    use_reports_database()
    # Try writing report with the given parameters for the provided date.
    try:
        write_report_query = "INSERT INTO paper_daily_report_table(date, present, absent, attendance_percentage) " \
                             f"VALUES ('{date}', {present_count}, {absent_count}, {attendance_percentage})"
        data_cursor.execute(write_report_query)

    # If an error occurs, it means that report data already exists for the provided date.
    # So update the data for the provided date.
    except server.IntegrityError:
        update_report_query = f"UPDATE paper_daily_report_table " \
                              f"SET present = {present_count}, absent = {absent_count}, " \
                              f"attendance_percentage = {attendance_percentage} " \
                              f"WHERE date = '{date}'"
        data_cursor.execute(update_report_query)


def write_student_report(attendance_record: dict):
    """
    Prepares/ updates individual student attendance report.

    :param attendance_record: The attendance record for the day.
    """
    for student in attendance_record:
        if attendance_record[student] == "P":
            # Try adding report data for a "present" student. This will be done only when the student
            # is a new admit.
            try:
                add_record_query = f"INSERT INTO paper_student_report_table VALUES ('{student}', 1, 1)"
                data_cursor.execute(add_record_query)

            # If an error occurs, it means that the student is an old student.
            # So update her/ his report data.
            except server.IntegrityError:
                update_present_student_record_query = "UPDATE paper_student_report_table " \
                                                      "SET total_days = total_days + 1, " \
                                                      "days_present = days_present + 1 " \
                                                      f"WHERE name = '{student}'"
                data_cursor.execute(update_present_student_record_query)

        else:
            # Try adding report data for an "absent" student. This will be done only when the student
            # is a new admit.
            try:
                add_record_query = f"INSERT INTO paper_student_report_table VALUES ('{student}', 1, 0)"
                data_cursor.execute(add_record_query)

            # If an error occurs, it means that the student is an old student.
            # So update her/ his report data.
            except server.IntegrityError:
                update_absent_student_record_query = "UPDATE paper_student_report_table " \
                                                     "SET total_days = total_days + 1 " \
                                                     f"WHERE name = '{student}'"
                data_cursor.execute(update_absent_student_record_query)


class CreatePINDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/CreatePINDialog_ui.ui", self)

        self._created = False

        self.cancel_button.clicked.connect(self.close)
        self.save_button.clicked.connect(self.set_pin)

    def is_pin_created(self) -> bool:
        """
        Tells whether the PIN is created or not.

        :return: True if PIN is created, else False.
        """
        return self._created

    def set_pin(self):
        """Stores the provided PIN in database."""
        provided_pin = self.create_pin_line_edit.text().strip()

        if len(provided_pin) == 4:
            use_information_database()

            set_pin_query = f"INSERT INTO paper_data_table(PIN) VALUES ('{provided_pin}')"
            data_cursor.execute(set_pin_query)

            self._created = True
            self.close()

            pin_saved_message_dialog = PINSavedMessageDialog()
            pin_saved_message_dialog.exec()


class UnlockAppDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/UnlockAppDialog_ui.ui", self)

        self._valid = False

        self.cancel_button.clicked.connect(self.close)
        self.unlock_button.clicked.connect(self.check_pin)

    def is_pin_valid(self) -> bool:
        """
        Tells whether the entered PIN is authorized or not.

        :return: True is PIN is authorized, else False.
        """
        return self._valid

    def check_pin(self):
        """Checks if the PIN provided by the user is correct."""
        pin = get_pin()
        provided_pin = self.enter_pin_line_edit.text().strip()

        if provided_pin == pin:
            self._valid = True
            self.close()
        else:
            incorrect_pin_illustration = QtGui.QPixmap("src/drawables/icons8-wrong-pincode-96.png")
            self.pin_check_illustration.setPixmap(incorrect_pin_illustration)
            self.pinCheck_label.setText("Incorrect PIN")


class PINSavedMessageDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/PINSavedMessageDialog_ui.ui", self)

        self.close_button.clicked.connect(self.close)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/MainWindow_ui.ui", self)
        self.show()

        self.today = get_date()[0]

        # Try creating the "paper_information_database" database.
        # Try creating the "paper_data_table" table within the database.
        # This will be done only on the first run of the application.
        try:
            create_information_database()
            create_data_table()

        # If an error occurs, it means that the application was run before and
        # the corresponding database and table exists.
        # Do nothing.
        except server.DatabaseError:
            pass

        # As the PIN is not created/ verified till now, disable:
        #   1. Create Class button
        #   2. Attendance tab
        #   3. Reports tab
        #   4. Settings tab
        self.create_class_button.setEnabled(False)

        self.options_tabWidget.setTabEnabled(1, False)
        self.options_tabWidget.setTabEnabled(2, False)
        self.options_tabWidget.setTabEnabled(3, False)

        self.setup_about_screen()

        # Authorize the user with the correct PIN.
        self.authorize()
        # If class name is not none, it means that a class is created.
        # So set up the application to work.
        if get_class_name() is not None:
            self.setup()

    def authorize(self):
        """Authorize user with correct PIN."""
        pin = get_pin()
        if pin is None:
            create_pin_dialog = CreatePINDialog()
            create_pin_dialog.exec()
            pin_created = create_pin_dialog.is_pin_created()

            if pin_created:
                self.create_class_button.setEnabled(True)
                self.create_class_button.clicked.connect(self.create_class)
        else:
            unlock_app_dialog = UnlockAppDialog()
            unlock_app_dialog.exec()
            is_valid_pin = unlock_app_dialog.is_pin_valid()

            if is_valid_pin:
                self.create_class_button.setEnabled(True)
                self.create_class_button.clicked.connect(self.create_class)

    def setup(self):
        """Performs all the necessary tasks after the PIN is verified and application starts."""
        self.classTab_stackedWidget.setCurrentIndex(1)

        self.options_tabWidget.setTabEnabled(1, True)
        self.options_tabWidget.setTabEnabled(2, True)
        self.options_tabWidget.setTabEnabled(3, True)

        # Check whether the student list is empty or not.
        if get_student_list():
            # If student list is not empty, set the start up tab as the
            # "Attendance" tab to mark attendance.
            self.options_tabWidget.setCurrentIndex(1)
        else:
            # If it is empty, it means that no student is added in the class.
            # In this case, set the start up tab as the "Class" tab to add
            # students in the class.
            self.options_tabWidget.setCurrentIndex(0)

        self.setup_class_screen()
        self.setup_attendance_screen()
        self.setup_reports_screen()
        self.setup_settings_screen()

        # Try to set "paper_attendance_database" as the current working database.
        # If no error occurs, it means that the database exists along with attendance
        # records. So leave "Edit Data" and "Export Data" buttons in enabled state.
        try:
            use_attendance_database()

        # If an error occurs, it means that the database does not exist.
        # Hence, there are no attendance records.
        # So disable "Edit Data" and "Export Data" buttons.
        except server.ProgrammingError:
            self.edit_data_button.setEnabled(False)
            self.export_data_button.setEnabled(False)

    def setup_class_screen(self):
        """Setup all the visual elements on "Class" screen."""
        self.students_tree_widget.setHeaderLabels(["Roll", "Name"])
        self.students_tree_widget.setColumnWidth(0, 40)
        self.students_tree_widget.setColumnWidth(1, 80)
        self.class_name_label.setText(get_class_name())
        self.populate_student_list_on_class_screen()
        self.set_student_count()
        self.search_student_class_line_edit.textChanged.connect(self.search_student_in_student_list)
        self.rename_class_button.clicked.connect(self.rename_class)
        self.delete_class_button.clicked.connect(self.confirm_delete)
        self.edit_class_button.clicked.connect(self.edit_class)
        self.export_data_button.clicked.connect(export_data)
        self.backup_data()

    def setup_attendance_screen(self):
        """Setup all the visual elements on Attendance screen."""
        self.search_student_attendance_line_edit.textChanged.connect(self.search_student_in_attendance_list)
        self.edit_data_button.clicked.connect(self.show_edit_attendance_data_dialog)
        self.edit_attendance_button.clicked.connect(self.show_edit_attendance_data_dialog)
        self.date_label.setText(strftime("%d %B, %Y"))

        # Try to get all data from today's attendance record.
        # If no error occurs, set the "Attendance" tab to show
        # that the attendance has been recorded for the day.
        try:
            use_attendance_database()

            test_for_table_query = f"SELECT * FROM {self.today}"
            data_cursor.execute(test_for_table_query)

            self.attendance_stackedWidget.setCurrentIndex(1)

        # If an error occurs, it means that the attendance has not been recorded for the day.
        # So set the "Attendance" tab to take attendance.
        except server.ProgrammingError:
            self.attendance_stackedWidget.setCurrentIndex(0)
            self.populate_student_list_on_attendance_screen()

            self.mark_attendance_tree_widget.setHeaderLabels(["Present", "Roll", "Name"])
            self.mark_attendance_tree_widget.setColumnWidth(0, 50)
            self.mark_attendance_tree_widget.setColumnWidth(1, 40)
            self.mark_attendance_tree_widget.setColumnWidth(2, 80)

            self.save_button.clicked.connect(self.save_attendance)
            self.clear_button.clicked.connect(self.clear_student_list_attendance_screen)

    def setup_reports_screen(self):
        """Setup all the visual elements on Reports screen."""
        self.graph_widget.setBackground("w")
        self.graph_widget.setLabel("left", "Attendance Percentage")
        self.graph_widget.setLabel("bottom", "Days")
        self.graph_widget.showGrid(x=True, y=True)
        self.graph_widget.setMenuEnabled(False)
        self.graph_widget.setLimits(xMin=0, xMax=365, yMin=0, yMax=105, minXRange=10,
                                    maxXRange=31, minYRange=10, maxYRange=105)
        self.graph_widget.setRange(xRange=(1, 10), yRange=(1, 105))
        self.graph_widget.setTitle("Class Attendance Percentage Over The Past Days", size="12pt")

        raw_date = get_date()[1]
        self.report_date_date_edit.setDate(QtCore.QDate(raw_date[2], raw_date[1], raw_date[0]))
        self.get_report_button.clicked.connect(self.display_report)
        self.display_report()
        self.display_graph()
        self.populate_individual_student_report_list()

    def setup_settings_screen(self):
        """Setup all the visual elements on Settings screen."""
        settings = get_settings()
        if settings["check present"] == "Y":
            self.check_present_check_box.setCheckState(QtCore.Qt.CheckState.Checked)
        self.minimum_attendance_spin_box.setValue(settings["minimum attendance"])
        self.save_new_pin_button.clicked.connect(self.save_new_pin)
        self.backup_frequency_combo_box.addItems(["Daily", "Weekly", "Monthly"])
        self.backup_frequency_combo_box.setCurrentIndex(settings["backup frequency"])
        self.save_settings_button.clicked.connect(self.save_settings)
        self.reset_to_default_button.clicked.connect(self.reset_settings)

    def setup_about_screen(self):
        """Setup all the visual elements on About screen."""
        self.credits_button.clicked.connect(self.display_credits)
        self.license_button.clicked.connect(self.display_license)

    def populate_student_list_on_class_screen(self):
        """Populates the list of students on Class screen."""
        self.students_tree_widget.clear()

        student_list = get_student_list()
        for i in range(len(student_list)):
            student_name = student_list[i]
            self.students_tree_widget.addTopLevelItem(
                QtWidgets.QTreeWidgetItem([str(i + 1), student_name])
            )

        self.set_student_count()

    def get_children_of_students_tree_widget(self) -> list:
        """
        Prepares the list of children present inside the parent element
        of the students_tree_widget.
        Here, children refers to the sub-elements of the primary element
        (parent - the invisible root item) inside the students_tree_widget.

        :return: List containing children of the parent element.
        """
        parent = self.students_tree_widget.invisibleRootItem()
        child_count = parent.childCount()

        children = list()
        for i in range(child_count):
            children.append(parent.child(i))

        return children

    def search_student_in_student_list(self):
        """Searches and displays the required student in student list on Class screen."""
        children = self.get_children_of_students_tree_widget()

        for child in children:
            if self.search_student_class_line_edit.text().lower().strip() == child.text(0).lower() \
                    or self.search_student_class_line_edit.text().lower().strip() in child.text(1).lower():
                child.setHidden(False)

            else:
                child.setHidden(True)

    def set_student_count(self):
        """Sets the number of students on Class screen."""
        student_count = self._get_student_count()
        if student_count == 1:
            self.student_count_label.setText(str(student_count) + " student")
        else:
            self.student_count_label.setText(str(student_count) + " students")

    def _get_student_count(self) -> int:
        """
        Helper function for set_student_count().

        :return: Total number of students in Class.
        """
        return self.students_tree_widget.topLevelItemCount()

    def create_class(self):
        """Displays the dialog to create a new empty class."""
        create_class_dialog = CreateClassDialog()
        create_class_dialog.exec()

        self.setup()

    def rename_class(self):
        """Displays the dialog to rename class."""
        rename_class_dialog = RenameClassDialog()
        rename_class_dialog.exec()

        self.class_name_label.setText(get_class_name())

    @staticmethod
    def confirm_delete():
        """Asks for confirmation before deleting the class."""
        delete_class_confirmation_dialog = DeleteClassConfirmationDialog()
        delete_class_confirmation_dialog.exec()

    def edit_class(self):
        """Displays the dialog to add, remove and rename students in the class."""
        edit_class_dialog = EditClassDialog()
        edit_class_dialog.exec()

        if edit_class_dialog.get_action() == "add":
            self.populate_student_list_on_class_screen()
            self.populate_student_list_on_attendance_screen()

        elif edit_class_dialog.get_action() == "remove":
            self.populate_student_list_on_class_screen()
            self.populate_student_list_on_attendance_screen()

            self.populate_individual_student_report_list()

        elif edit_class_dialog.get_action() == "rename":
            self.populate_student_list_on_class_screen()
            self.populate_student_list_on_attendance_screen()

            self.display_report()
            self.populate_individual_student_report_list()

    @staticmethod
    def backup_data():
        """Exports attendance data to the required files and updates the backup date."""
        settings = get_settings()
        if strftime("%Y-%m-%d") == str(settings["backup date"]):
            export_data()
            use_information_database()

            update_backup_date_query = "UPDATE paper_settings_table " \
                                       "SET backup_date = date_add(" \
                                       f"curdate(), interval {settings['backup frequency']} day" \
                                       ")"
            data_cursor.execute(update_backup_date_query)

    def populate_student_list_on_attendance_screen(self):
        """Populates and displays the list of students on the Attendance screen."""
        student_list = get_student_list()
        settings = get_settings()

        self.mark_attendance_tree_widget.clear()

        # If the student list is not empty, enable the "Save" and "Clear" buttons.
        if student_list:
            self.save_button.setEnabled(True)
            self.clear_button.setEnabled(True)
        # If the student list is empty, then there is no use of the "Save" and "Clear"
        # buttons. So disable them.
        else:
            self.save_button.setEnabled(False)
            self.clear_button.setEnabled(False)

        # If the user has enabled the setting to "show all students marked as present", then
        # populate the student list on attendance screen with all checkboxes checked.
        if settings["check present"] == "Y":
            for i in range(len(student_list)):
                student_name = student_list[i]
                item = QtWidgets.QTreeWidgetItem(
                    self.mark_attendance_tree_widget,
                    ["", str(i + 1), student_name]
                )
                # Check all the checkboxes.
                item.setCheckState(0, QtCore.Qt.CheckState.Checked)
                self.mark_attendance_tree_widget.addTopLevelItem(item)

        # If the setting is disabled, then populate the student list with all checkboxes unchecked.
        else:
            for i in range(len(student_list)):
                student_name = student_list[i]
                item = QtWidgets.QTreeWidgetItem(self.mark_attendance_tree_widget, ["", str(i + 1), student_name])
                # Uncheck all the checkboxes.
                item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
                self.mark_attendance_tree_widget.addTopLevelItem(item)

    def get_children_of_attendance_tree_widget(self) -> list:
        """
        Prepares the list of children present inside the parent element
        of the mark_attendance_tree_widget.
        Here, children refers to the sub-elements of the primary element
        (parent - the invisible root item) inside the mark_attendance_tree_widget.

        :return: List containing children of the parent element.
        """
        parent = self.mark_attendance_tree_widget.invisibleRootItem()
        child_count = parent.childCount()

        children = list()

        for i in range(child_count):
            children.append(parent.child(i))

        return children

    def search_student_in_attendance_list(self):
        """Searches and displays the required student in attendance list on Attendance screen."""
        children = self.get_children_of_attendance_tree_widget()

        for child in children:
            if self.search_student_attendance_line_edit.text().lower().strip() == child.text(1).lower() \
                    or self.search_student_attendance_line_edit.text().lower().strip() in child.text(2).lower():
                child.setHidden(False)

            else:
                child.setHidden(True)

    def clear_student_list_attendance_screen(self):
        """Clears the recorded attendance to start over."""
        student_list = get_student_list()
        self.mark_attendance_tree_widget.clear()

        for i in range(len(student_list)):
            student_name = student_list[i]
            item = QtWidgets.QTreeWidgetItem(self.mark_attendance_tree_widget, ["", str(i + 1), student_name])
            item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
            self.mark_attendance_tree_widget.addTopLevelItem(item)

    def save_attendance(self):
        """Saves the recorded attendance data for the day."""
        save_attendance_confirmation_dialog = SaveAttendanceConfirmationDialog()
        save_attendance_confirmation_dialog.exec()
        action = save_attendance_confirmation_dialog.get_action()

        if action == "save":
            date = get_date()[0]
            # Try creating the database "paper_attendance_database". This will be done
            # only when the attendance is recorded for the first time.
            try:
                create_attendance_database()

            # If an error occurs, it means that the database already exists and this is
            # not the first attendance record.
            # Do nothing.
            except server.DatabaseError:
                pass

            # Try creating a table inside "paper_attendance_database" with
            # today's date in DD_MM_YYYY format as name.
            try:
                create_attendance_table(date)

            # If an error occurs, it means that the table already exists and the user
            # is editing today's attendance data.
            except server.ProgrammingError:
                pass

            parent = self.mark_attendance_tree_widget.invisibleRootItem()
            children = parent.childCount()

            attendance_record = dict()

            for i in range(children):
                current_child = parent.child(i)

                if current_child.checkState(0) == QtCore.Qt.CheckState.Checked:
                    attendance_record[current_child.text(2)] = "P"

                else:
                    attendance_record[current_child.text(2)] = "A"

            for student in attendance_record:
                use_attendance_database()

                record_attendance_query = f"INSERT INTO {self.today} " \
                                          f"VALUES ('{student}', '{attendance_record[student]}')"
                data_cursor.execute(record_attendance_query)

            self.write_attendance_report(attendance_record)
            self.attendance_stackedWidget.setCurrentIndex(1)

    def show_edit_attendance_data_dialog(self):
        """Displays the dialog for editing attendance data."""
        edit_attendance_data_dialog = EditAttendanceDataDialog()
        edit_attendance_data_dialog.exec()
        action = edit_attendance_data_dialog.get_action()

        if action == "edit attendance":
            self.display_report()
            self.display_graph()
            self.populate_individual_student_report_list()

    def write_attendance_report(self, attendance_record):
        """Writes all attendance reports to the database."""
        # Try to set "paper_reports_database" as the current working database.
        try:
            use_reports_database()

        # If an error occurs, it means that the database does not exist.
        # So create the database. Inside the database, create the
        # "paper_student_report_table" table.
        # This will be done only when the attendance is recorded for
        # the first time.
        except server.ProgrammingError:
            create_reports_database()
            use_reports_database()

            create_student_report_table()

        write_student_report(attendance_record)
        write_daily_report(self.today)

        self.display_report()
        self.display_graph()

    def display_report(self):
        """
        Gets the statistical report data for the selected date and displays it
        in the Reports section.
        """
        date = self.report_date_date_edit.text().split("-")
        date = "_".join(str(int(i)) for i in date)

        # Try to get report data for a particular date.
        # If no error occurs, it means that the data exists.
        # So populate the list of present and absent students and show statistical data.
        try:
            use_reports_database()
            get_report_query = "SELECT date, present, absent, attendance_percentage FROM paper_daily_report_table " \
                               f"WHERE date = '{date}'"
            data_cursor.execute(get_report_query)

            statistical_report_data = data_cursor.fetchall()
            self.student_count_reports_label.setText(
                str(statistical_report_data[0][1] + statistical_report_data[0][2])
            )
            self.present_count_label.setText(str(statistical_report_data[0][1]))
            self.absent_count_label.setText(str(statistical_report_data[0][2]))
            self.attendance_percentage_label.setText(str(statistical_report_data[0][3]) + "%")

            self.populate_present_report_list(date)
            self.populate_absent_report_list(date)

        # If an error occurs, it means that the data for the corresponding date does not exist.
        # So set up the "Reports" screen to show that no data was found.
        except server.ProgrammingError or IndexError:
            self.student_count_reports_label.setText("-")
            self.present_count_label.setText("-")
            self.absent_count_label.setText("-")
            self.attendance_percentage_label.setText("-")

            self.present_tree_widget.clear()
            self.absent_tree_widget.clear()

            self.present_tree_widget.setColumnCount(1)
            self.absent_tree_widget.setColumnCount(1)

            self.present_tree_widget.setHeaderLabel("")
            self.absent_tree_widget.setHeaderLabel("")

            self.present_tree_widget.addTopLevelItem(QtWidgets.QTreeWidgetItem(["No data found!"]))
            self.absent_tree_widget.addTopLevelItem(QtWidgets.QTreeWidgetItem(["No data found!"]))

        # Populate the individual student report list as this data is displayed
        # irrespective of any date.
        self.populate_individual_student_report_list()

    def populate_present_report_list(self, date: str):
        """
        Populates and displays the list of students present on the provided date.

        :param date: Date for querying the list of present students.
        """
        self.present_tree_widget.clear()

        self.present_tree_widget.setHeaderLabels(["No.", "Name", "Roll"])
        self.present_tree_widget.setColumnWidth(0, 40)
        self.present_tree_widget.setColumnWidth(1, 150)
        self.present_tree_widget.setColumnWidth(2, 60)

        student_list = get_student_list(date)

        use_attendance_database()

        get_present_students_query = f"SELECT name FROM {date} WHERE state = 'P'"
        data_cursor.execute(get_present_students_query)

        data = data_cursor.fetchall()
        present = [student[0] for student in data]

        for i in range(len(present)):
            student_name = present[i]
            roll_number = str(student_list.index(student_name) + 1)

            self.present_tree_widget.addTopLevelItem(QtWidgets.QTreeWidgetItem([str(i + 1),
                                                                                student_name, roll_number]))

    def populate_absent_report_list(self, date: str):
        """
        Populates and displays the list of students absent on the provided date.

        :param date: Date for querying the list of absent students.
        """
        self.absent_tree_widget.clear()

        self.absent_tree_widget.setHeaderLabels(["No.", "Name", "Roll"])
        self.absent_tree_widget.setColumnWidth(0, 40)
        self.absent_tree_widget.setColumnWidth(1, 150)
        self.absent_tree_widget.setColumnWidth(2, 60)

        student_list = get_student_list(date)

        use_attendance_database()

        get_absent_students_query = f"SELECT name FROM {date} WHERE state = 'A'"
        data_cursor.execute(get_absent_students_query)

        data = data_cursor.fetchall()
        absent = [student[0] for student in data]

        for i in range(len(absent)):
            student_name = absent[i]
            roll_number = str(student_list.index(student_name) + 1)

            self.absent_tree_widget.addTopLevelItem(QtWidgets.QTreeWidgetItem([str(i + 1),
                                                                               student_name, roll_number]))

    def plot_class_attendance_graph(self, days: list, attendance_percentage: list):
        """Plots the attendance graph."""
        self.graph_widget.plot(days, attendance_percentage, pen="k", symbol="o", symbolPen="b", symbolBrush=0.1)

    def display_graph(self):
        """Gets the required data and displays the "Attendance Chart"."""
        # Try to get attendance percentage data.
        try:
            use_reports_database()

            get_attendance_percentage_data_query = "SELECT attendance_percentage FROM paper_daily_report_table"
            data_cursor.execute(get_attendance_percentage_data_query)

            data = data_cursor.fetchall()

        # If an error occurs, it means that no attendance has been recorded till now.
        # So return empty list.
        except server.ProgrammingError:
            data = list()

        days_data = list()
        attendance_percentage_data = list()

        for i in range(len(data)):
            days_data.append(i + 1)
            attendance_percentage_data.append(float(data[i][0]))

        self.graph_widget.clear()
        self.plot_class_attendance_graph(days_data, attendance_percentage_data)

    def populate_individual_student_report_list(self):
        """Populates and displays the list of students with attendance report of each student."""
        self.student_report_tree_widget.clear()

        self.student_report_tree_widget.setHeaderLabels(["Roll", "Name", "Days Present",
                                                         "Total Days", "Percentage", "Remark"])

        self.student_report_tree_widget.setColumnWidth(0, 40)
        self.student_report_tree_widget.setColumnWidth(1, 150)
        self.student_report_tree_widget.setColumnWidth(2, 100)
        self.student_report_tree_widget.setColumnWidth(3, 100)
        self.student_report_tree_widget.setColumnWidth(4, 100)
        self.student_report_tree_widget.setColumnWidth(5, 40)

        # Try to populate the individual student report list.
        try:
            use_reports_database()

            get_student_report_query = "SELECT * FROM paper_student_report_table"
            data_cursor.execute(get_student_report_query)

            student_report = data_cursor.fetchall()
            settings = get_settings()

            for i in range(len(student_report)):
                student_name = student_report[i][0]
                total_days = student_report[i][1]
                days_present = student_report[i][2]

                percentage = round((days_present / total_days) * 100, 2)

                item = QtWidgets.QTreeWidgetItem(self.student_report_tree_widget, [str(i + 1), student_name,
                                                                                   str(days_present),
                                                                                   str(total_days),
                                                                                   str(percentage) + "%"])

                if 50 < percentage <= settings["minimum attendance"]:
                    remark_icon = QtGui.QIcon("src/icons/icons8-error-96.png")
                    item.setIcon(5, remark_icon)

                elif percentage > 90:
                    remark_icon = QtGui.QIcon("src/icons/icons8-prize-96.png")
                    item.setIcon(5, remark_icon)

                elif percentage <= 50:
                    remark_icon = QtGui.QIcon("src/icons/icons8-high-priority-96.png")
                    item.setIcon(5, remark_icon)

                else:
                    pass

                self.student_report_tree_widget.addTopLevelItem(item)

        # If an error occurs, it means that no attendance has been recorded till now.
        # Do nothing.
        except server.ProgrammingError:
            pass

    def save_new_pin(self):
        """Updates PIN to the new PIN provided by the user."""
        old_pin = self.old_pin_line_edit.text().strip()
        new_pin = self.new_pin_line_edit.text().strip()

        if old_pin == get_pin():
            correct_old_pin_illustration = QtGui.QPixmap("src/drawables/icons8-verified-account-100.png")
            self.old_pin_check_illustration.setPixmap(correct_old_pin_illustration)

            if len(new_pin) < 4 or new_pin == old_pin:
                bad_new_pin_illustration = QtGui.QPixmap("src/icons/icons8-error-96.png")
                self.new_pin_check_illustration.setPixmap(bad_new_pin_illustration)

            elif len(new_pin) == 4:
                good_new_pin_illustration = QtGui.QPixmap("src/drawables/icons8-verified-account-100.png")
                self.new_pin_check_illustration.setPixmap(good_new_pin_illustration)

                use_information_database()

                save_new_pin_query = f"UPDATE paper_data_table SET pin = '{new_pin}'"
                data_cursor.execute(save_new_pin_query)

                get_pin()

                pin_saved_message_dialog = PINSavedMessageDialog()
                pin_saved_message_dialog.exec()

        else:
            incorrect_old_pin_illustration = QtGui.QPixmap("src/drawables/icons8-wrong-pincode-96.png")
            self.old_pin_check_illustration.setPixmap(incorrect_old_pin_illustration)

            self.new_pin_check_illustration.clear()

    def save_setting_check_present(self):
        """Manages the "Show all students marked as present" setting."""
        use_information_database()
        if self.check_present_check_box.checkState() == QtCore.Qt.CheckState.Checked:
            update_settings_check_present_query = "UPDATE paper_settings_table SET check_present = 'Y'"
            data_cursor.execute(update_settings_check_present_query)

        elif self.check_present_check_box.checkState() == QtCore.Qt.CheckState.Unchecked:
            update_settings_check_present_query = "UPDATE paper_settings_table SET check_present = 'N'"
            data_cursor.execute(update_settings_check_present_query)

    def save_setting_minimum_attendance(self):
        """Manages the "Minimum attendance percentage" setting."""
        minimum_attendance_percentage = self.minimum_attendance_spin_box.text()
        minimum_attendance_numerical = minimum_attendance_percentage[0:len(minimum_attendance_percentage) - 1]

        use_information_database()
        set_minimum_attendance_percentage_query = "UPDATE paper_settings_table " \
                                                  f"SET minimum_attendance = {minimum_attendance_numerical}"
        data_cursor.execute(set_minimum_attendance_percentage_query)

    def save_setting_backup_frequency(self):
        """Manages the "Automatic backup" setting."""
        selected_backup_frequency = self.backup_frequency_combo_box.currentText()

        if selected_backup_frequency == "Daily":
            backup_frequency = 0
            backup_date_difference = 1

        elif selected_backup_frequency == "Weekly":
            backup_frequency = 1
            backup_date_difference = 7

        else:
            backup_frequency = 2
            backup_date_difference = 30

        use_information_database()

        set_backup_frequency_query = f"UPDATE paper_settings_table SET backup_frequency = {backup_frequency}"
        data_cursor.execute(set_backup_frequency_query)

        update_backup_frequency_query = "UPDATE paper_settings_table " \
                                        "SET backup_date = date_add(" \
                                        f"curdate(), interval {backup_date_difference} day" \
                                        ")"
        data_cursor.execute(update_backup_frequency_query)

    def save_settings(self):
        """Saves all the chosen settings."""
        self.save_setting_check_present()
        self.save_setting_minimum_attendance()
        self.save_setting_backup_frequency()

        self.perform_settings()

        settings_saved_message_dialog = SettingsSavedMessageDialog()
        settings_saved_message_dialog.exec()

    def reset_settings(self):
        """Sets all the settings to their default values."""
        reset_settings_confirmation_dialog = ResetSettingsConfirmationDialog()
        reset_settings_confirmation_dialog.exec()
        action = reset_settings_confirmation_dialog.get_action()

        if action == "reset settings":
            self.check_present_check_box.setCheckState(QtCore.Qt.CheckState.Unchecked)

            use_information_database()

            drop_settings_table_query = "DROP TABLE paper_settings_table"
            data_cursor.execute(drop_settings_table_query)

            create_settings_table()

            self.perform_settings()

    def perform_settings(self):
        """Makes required changes after a setting's value changes."""
        settings = get_settings()
        self.minimum_attendance_spin_box.setValue(settings["minimum attendance"])
        self.backup_frequency_combo_box.setCurrentIndex(settings["backup frequency"])

        self.populate_student_list_on_attendance_screen()
        self.populate_individual_student_report_list()

    @staticmethod
    def display_credits():
        """Shows the "Credits" dialog."""
        credits_dialog = CreditsDialog()
        credits_dialog.exec()

    @staticmethod
    def display_license():
        """Shows the software license terms dialog."""
        license_terms_dialog = LicenseTermsDialog()
        license_terms_dialog.exec()


class CreateClassDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/CreateClassDialog_ui.ui", self)

        self.create_button.clicked.connect(self.create)
        self.cancel_button.clicked.connect(self.close)

    def create(self):
        """Creates a new empty Class."""
        class_name = self.class_name_line_edit.text().strip()

        if class_name != "":
            set_class_name(class_name)
            create_student_list_table()

            self.close()


class RenameClassDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/RenameClassDialog_ui.ui", self)

        self.rename_button.clicked.connect(self.rename)
        self.cancel_button.clicked.connect(self.close)

    def rename(self):
        """Sets the new class name in database."""
        provided_class_name = self.new_class_name_line_edit.text().strip()

        if provided_class_name != "":
            set_class_name(provided_class_name)

            self.close()


class DeleteClassConfirmationDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/DeleteClassConfirmationDialog_ui.ui", self)

        self.yes_button.clicked.connect(self.delete)
        self.no_button.clicked.connect(self.close)

    def delete(self):
        """Deletes all the databases, hence deleting the Class."""
        self.close()

        verify_identity_dialog = VerifyIdentityDialog()
        verify_identity_dialog.exec()
        pin_valid = verify_identity_dialog.is_verified()

        if pin_valid:
            try:
                use_attendance_database()
                export_data()
            except server.ProgrammingError:
                pass

            delete_information_database_query = "DROP DATABASE paper_information_database"
            data_cursor.execute(delete_information_database_query)

            try:
                delete_attendance_database_query = "DROP DATABASE paper_attendance_database"
                data_cursor.execute(delete_attendance_database_query)

                delete_reports_database_query = "DROP DATABASE paper_reports_database"
                data_cursor.execute(delete_reports_database_query)

            except server.DatabaseError:
                pass

        global main_window
        main_window.destroy()

        create_information_database()
        create_data_table()

        main_window = MainWindow()


class VerifyIdentityDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/VerifyIdentityDialog_ui.ui", self)

        self._verified = False

        self.verify_button.clicked.connect(self.verify)
        self.cancel_button.clicked.connect(self.close)

    def is_verified(self) -> bool:
        """
        Tells whether the entered PIN is verified or not.

        :return: True if PIN is verified, else False.
        """
        return self._verified

    def verify(self):
        """Checks whether the PIN provided by the user is correct or not."""
        pin = get_pin()
        provided_pin = self.enter_pin_line_edit.text().strip()

        if provided_pin == pin:
            self.close()
            self._verified = True
        else:
            incorrect_pin_illustration = QtGui.QPixmap("src/drawables/icons8-wrong-pincode-96.png")
            self.pin_check_illustration.setPixmap(incorrect_pin_illustration)
            self.pinCheck_label.setText("Incorrect PIN")


class ExportDataDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/ExportDataDialog_ui.ui", self)

        self.show()
        self.close_button.clicked.connect(self.close)
        self.go_to_file_button.clicked.connect(self.go_to_file)

        self.FOLDER_PATH = os.path.expanduser("~") + "\\Documents\\Paper\\Attendance Records"
        attendance_records = get_past_attendance_records()

        if not os.path.exists(os.path.expanduser("~") + "\\Documents\\Paper\\Attendance Records"):
            os.makedirs(os.path.expanduser("~") + "\\Documents\\Paper\\Attendance Records")

        use_attendance_database()
        for record in attendance_records:
            # Each attendance record is named as "DD_MM_YYYY". To make things presentable, replace
            # all underscores with hyphens to make it look like a general date (DD-MM-YYYY).
            file_name = record.replace("_", "-")
            data_file = open(self.FOLDER_PATH + f"\\Attendance Record {file_name} .csv", "w", newline="")
            data_writer = writer(data_file)

            self.file_name_label.setText(f"Attendance Record {file_name}")

            get_record_query = f"SELECT * FROM {record}"
            data_cursor.execute(get_record_query)

            attendance_data = data_cursor.fetchall()

            data_writer.writerow(["Name", "State"])
            data_writer.writerows(attendance_data)

            data_file.flush()

            self.progress_bar.setValue(
                ((attendance_records.index(record) + 1) // len(attendance_records)) * 100
            )
            application.processEvents()

        self.stackedWidget.setCurrentIndex(1)

    def go_to_file(self):
        """Opens the file where all attendance data is exported, in File Explorer."""
        subprocess.Popen(f'explorer "{self.FOLDER_PATH}"')


class EditClassDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/EditClassDialog_ui.ui", self)

        self._action = None

        self.edit_class_combo_box.addItems(["Add student", "Remove student", "Rename student"])
        self.edit_class_combo_box.activated.connect(self.switch_page)

        self.add_button.clicked.connect(self.add_student)
        self.cancel_add_page_button.clicked.connect(self.close)

        self.remove_button.clicked.connect(self.remove_student)
        self.cancel_remove_page_button.clicked.connect(self.close)

        self.rename_student_button.clicked.connect(self.rename_student)
        self.cancel_rename_page_button.clicked.connect(self.close)

    def get_action(self) -> str:
        """
        Tells the current edit action. The various edit actions are
        "add", "rename" and "remove".

        :return: The current edit action.
        """
        return self._action

    def switch_page(self):
        """Displays the page for the selected action."""
        self.editOptions_stackedWidget.setCurrentIndex(self.edit_class_combo_box.currentIndex())

    def add_student(self):
        """Adds a student to the Class if the student does not exist."""
        use_information_database()

        name = self.name_add_page_line_edit.text().strip().title()

        if name != "":
            try:
                add_query = f"INSERT INTO paper_student_list_table VALUES ('{name}')"
                data_cursor.execute(add_query)

                self._action = "add"
                self.close()
            except server.IntegrityError:
                self.close()

                duplicate_student_error_dialog = DuplicateStudentErrorDialog()
                duplicate_student_error_dialog.exec()

    def remove_student(self):
        """Removes the desired student from the Class if the entered roll number is correct."""
        use_information_database()

        student_list = get_student_list()
        roll_number = self.roll_number_remove_page_line_edit.text().strip()

        if roll_number.isdigit() and 0 < int(roll_number) <= len(student_list):
            student_name = student_list[int(roll_number) - 1]

            remove_query = "DELETE FROM paper_student_list_table " \
                           f"WHERE name = '{student_name}'"
            data_cursor.execute(remove_query)

            # Try to remove student from individual student report.
            try:
                use_reports_database()
                remove_from_individual_student_report_query = "DELETE FROM paper_student_report_table " \
                                                              f"WHERE name = '{student_name}'"
                data_cursor.execute(remove_from_individual_student_report_query)

            # If an error occurs, it means that the individual student report list is empty
            # because no attendance has been recorded till now.
            # Do nothing.
            except server.ProgrammingError:
                pass

            self._action = "remove"
            self.close()
        else:
            self.close()

            roll_number_not_found_error_dialog = RollNumberNotFoundErrorDialog()
            roll_number_not_found_error_dialog.exec()

    def rename_student(self):
        """Renames the student if the entered roll number is correct."""
        student_list = get_student_list()

        roll_number = self.roll_number_rename_page_line_edit.text().strip()
        new_name = self.new_name_rename_page_line_edit.text().strip().title()

        if roll_number.isdigit() and 0 < int(roll_number) <= len(student_list) and new_name != "":
            old_name = student_list[int(roll_number) - 1]

            try:
                use_information_database()
                rename_query = "UPDATE paper_student_list_table " \
                               f"SET name = '{new_name}' " \
                               f"WHERE name = '{old_name}'"
                data_cursor.execute(rename_query)

                # Try to rename student in individual student report.
                try:
                    use_reports_database()
                    rename_query = "UPDATE paper_student_report_table " \
                                   f"SET name = '{new_name}' " \
                                   f"WHERE name = '{old_name}'"
                    data_cursor.execute(rename_query)

                # If an error occurs, it means that the individual student report list is empty
                # because no attendance has been recorded till now.
                # Do nothing.
                except server.ProgrammingError:
                    pass

                rename_student_in_past_records(old_name, new_name)

                self._action = "rename"
                self.close()
            except server.IntegrityError:
                self.close()

                duplicate_student_error_dialog = DuplicateStudentErrorDialog()
                duplicate_student_error_dialog.exec()

        else:
            self.close()

            roll_number_not_found_error_dialog = RollNumberNotFoundErrorDialog()
            roll_number_not_found_error_dialog.exec()


class DuplicateStudentErrorDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/DuplicateStudentErrorDialog_ui.ui", self)

        self.close_button.clicked.connect(self.close)


class SaveAttendanceConfirmationDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/SaveAttendanceConfirmationDialog_ui.ui", self)

        self._action = None

        self.no_button.clicked.connect(self.close)
        self.yes_button.clicked.connect(self.confirm_save)

    def get_action(self) -> str:
        """
        Tells whether the user chose to save attendance or not.

        :return: String "save" if the user chose to save attendance.
        """
        return self._action

    def confirm_save(self):
        """Confirms saving the attendance record."""
        self._action = "save"
        self.close()


class EditAttendanceDataDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/EditAttendanceDataDialog_ui.ui", self)

        self._action = None

        raw_date = get_date()[1]
        self.attendance_data_date_edit.setDate(QtCore.QDate(raw_date[2], raw_date[1], raw_date[0]))
        self.state_combo_box.addItems(["Present", "Absent"])

        self.cancel_button.clicked.connect(self.close)
        self.edit_button.clicked.connect(self.edit_data)

    def get_action(self) -> str:
        """
        Tells whether the user edited attendance data or not.

        :return: String "edit attendance" if user edited, else None.
        """
        return self._action

    def edit_data(self) -> str or None:
        """Edits attendance data."""
        selected_date = self.attendance_data_date_edit.text().split("-")
        selected_date = "_".join(str(int(i)) for i in selected_date)

        student_list = get_student_list(selected_date)

        provided_roll_number = self.roll_number_line_edit.text().strip()
        state_position = self.state_combo_box.currentIndex()

        if state_position == 0:
            state = "P"
        else:
            state = "A"

        try:
            use_attendance_database()

            test_for_attendance_record_query = f"SELECT * FROM {selected_date}"
            data_cursor.execute(test_for_attendance_record_query)

            if provided_roll_number.isdigit() and 0 < int(provided_roll_number) <= len(student_list):
                student_name = student_list[int(provided_roll_number) - 1]
                get_current_state_query = f"SELECT state FROM {selected_date} " \
                                          f"WHERE name = '{student_name}'"

                data_cursor.execute(get_current_state_query)
                current_state = data_cursor.fetchone()[0]

                if state == "P":
                    update_data_query = f"UPDATE {selected_date} " \
                                        "SET state = 'P' " \
                                        f"WHERE name = '{student_name}'"
                else:
                    update_data_query = f"UPDATE {selected_date} " \
                                        "SET state = 'A' " \
                                        f"WHERE name = '{student_name}'"

                data_cursor.execute(update_data_query)

                use_reports_database()

                if state == "P":
                    # If the student was previously marked absent, only then update the individual
                    # student report by adding 1 to the number of days present.
                    if current_state == "A":
                        update_student_report_query = "UPDATE paper_student_report_table " \
                                                      "SET days_present = days_present + 1 " \
                                                      f"WHERE name = '{student_name}'"
                        data_cursor.execute(update_student_report_query)

                else:
                    # If the student was previously marked present, only then update the individual
                    # student report by subtracting 1 from the number of days present.
                    if current_state == "P":
                        update_student_report_query = "UPDATE paper_student_report_table " \
                                                      "SET days_present = days_present - 1 " \
                                                      f"WHERE name = '{student_name}'"
                        data_cursor.execute(update_student_report_query)

                write_daily_report(selected_date)

                self._action = "edit attendance"
                self.close()

            else:
                self.close()

                roll_number_not_found_error_dialog = RollNumberNotFoundErrorDialog()
                roll_number_not_found_error_dialog.exec()

        except server.ProgrammingError:
            self.close()

            no_data_found_error_dialog = NoDataFoundErrorDialog()
            no_data_found_error_dialog.exec()


class NoDataFoundErrorDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/NoDataFoundErrorDialog_ui.ui", self)

        self.close_button.clicked.connect(self.close)


class RollNumberNotFoundErrorDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/RollNumberNotFoundErrorDialog_ui.ui", self)

        self.close_button.clicked.connect(self.close)


class SettingsSavedMessageDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/SettingsSavedMessageDialog_ui.ui", self)

        self.close_button.clicked.connect(self.close)


class ResetSettingsConfirmationDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/ResetSettingsConfirmationDialog_ui.ui", self)

        self._action = None

        self.yes_button.clicked.connect(self.reset)
        self.no_button.clicked.connect(self.close)

    def get_action(self) -> str:
        """
        Tells whether the user chose to reset settings or not.

        :return: String "reset settings" if user chose to reset settings.
        """
        return self._action

    def reset(self):
        """Confirms resetting settings."""
        self._action = "reset settings"
        self.close()


class CreditsDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/CreditsDialog_ui.ui", self)


class LicenseTermsDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/layout/LicenseTermsDialog_ui.ui", self)


if __name__ == "__main__":
    application = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    application.exec()
