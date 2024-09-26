import csv
import sqlite3
from os import system
from xmlrpc.client import DateTime
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QDateEdit, QTimeEdit, QDialog, QFileDialog
)
from PyQt5.QtCore import QItemSelection, QItemSelectionModel, pyqtSignal, QDate, QTime, QDateTime, QFile, QTextStream
import sys

from pythonProject.auth import AuthDialog


class EventManagementSystem(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Event Management System")
        self.setGeometry(500, 100, 1050, 800)
        self.apply_stylesheet()


        # Database connection
        self.conn = sqlite3.connect("events.db")
        self.cursor = self.conn.cursor()
        self.create_table()
        self.create_venue_table()
        self.create_user_table()

        # Auth Dialog
        self.auth_dialog = AuthDialog()
        if not self.auth_dialog.exec_():
            sys.exit()

            # Layouts
        self.main_layout = QVBoxLayout()
        self.form_layout = QVBoxLayout()

        # Form inputs for event creation
        self.create_form()

        # Buttons
        self.create_buttons()
        self.clear_field_button = QPushButton("Clear Fields")
        self.clear_field_button.clicked.connect(self.clear_inputs)
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.clear_field_button)

        self.clear_filter_button = QPushButton("Clear Filter")
        self.clear_filter_button.clicked.connect(self.clear_filter)
        self.button_layout.addWidget(self.clear_filter_button)


        self.main_layout.addLayout(self.button_layout)
        # Event Table
        self.event_table = QTableWidget()
        self.event_table.setColumnCount(8)
        self.event_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Time", "Place", "Category", "SubCategory", "Hosted By", "People Coming"]
        )
        self.main_layout.addWidget(self.event_table)
        self.event_table.selectionModel().selectionChanged.connect(self.table_selection_changed)
        # Load events into table
        self.load_events()
        self.load_available_venues()

        self.setLayout(self.main_layout)
        self.check_today_events()

    def create_user_table(self):
        """Create the users table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)
        self.conn.commit()
    def apply_stylesheet(self):
        """Load and apply the external QSS stylesheet."""
        file = QFile("style.qss")
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())
        file.close()
    def table_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        """Update form fields when a table row is selected."""
        selected_row = self.event_table.currentRow()
        if selected_row != -1:
            event_id = self.event_table.item(selected_row, 0).text()
            name = self.event_table.item(selected_row, 1).text()
            time = self.event_table.item(selected_row, 2).text()
            place = self.event_table.item(selected_row, 3).text()
            category = self.event_table.item(selected_row, 4).text()
            subcategory = self.event_table.item(selected_row, 5).text()
            hosted_by = self.event_table.item(selected_row, 6).text()
            people_coming = self.event_table.item(selected_row, 7).text()

            # Update form fields
            self.name_input.setText(name)

            # Split date and time for date/time fields
            date_str, time_str= time.split(" ")
            self.date_input.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))
            self.time_input.setTime(QTime.fromString(time_str, "HH:mm:ss"))
            #self.venue_dropdown.addItem(place)
            if(self.venue_dropdown.findText(place) == -1):
                self.venue_dropdown.insertItem(0,place)
                self.venue_dropdown.setCurrentIndex(0)
            else:
                self.venue_dropdown.setCurrentText(place)
            self.category_input.setCurrentText(category)
            self.subcategory_input.setText(subcategory)
            self.hosted_input.setText(hosted_by)
            self.people_input.setText(people_coming)

    def create_table(self):
        """Create the events table if it doesn't exist."""
        #self.cursor.execute("""DROP TABLE events""")

        #self.conn.commit()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                time TEXT,
                place TEXT,
                category TEXT,
                subcategory TEXT,
                hosted_by TEXT,
                people_coming INTEGER,
                status TEXT
            )
        """)
        self.conn.commit()

    def create_venue_table(self):
        """Create the venue table to store available venues."""
        self.cursor.execute("""DROP TABLE venue""")
        self.conn.commit()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS venue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )            
        """)
        self.conn.commit()
        self.cursor.execute("""
                    INSERT INTO venue (name) values ('MUMBAI'),('PUNE'),('INDORE'),('DELHI'),('SURAT')            
                """)
        self.conn.commit()

    def load_available_venues(self):
        """Load available venues into the dropdown (venues not currently in use)."""
        self.cursor.execute("""
            SELECT name FROM venue 
            WHERE name NOT IN (
                SELECT place FROM events WHERE status IS NULL OR status = 'ongoing'
            )
        """)
        venues = self.cursor.fetchall()
        self.venue_dropdown.clear()  # Clear existing dropdown items
        for venue in venues:
            self.venue_dropdown.addItem(venue[0])
    def clear_filter(self) :
        self.load_events()
    def create_form(self):
        """Create input form for event creation."""
        # Event Name
        self.name_label = QLabel("Event Name:")
        self.name_input = QLineEdit()
        self.form_layout.addWidget(self.name_label)
        self.form_layout.addWidget(self.name_input)

        # Event Time
        self.time_label = QLabel("Event Time:")
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setDate(QDate.currentDate())
        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm:ss")
        print(QTime.currentTime())
        self.time_input.setTime(QTime.currentTime())
        self.form_layout.addWidget(self.time_label)
        self.form_layout.addWidget(self.date_input)
        self.form_layout.addWidget(self.time_input)



        # Event Category
        self.category_label = QLabel("Category:")
        self.category_input = QComboBox()
        self.category_input.addItems(["Conference", "Workshop", "Seminar", "Party"])
        self.form_layout.addWidget(self.category_label)
        self.form_layout.addWidget(self.category_input)

        # Event Subcategory
        self.subcategory_label = QLabel("SubCategory:")
        self.subcategory_input = QLineEdit()
        self.form_layout.addWidget(self.subcategory_label)
        self.form_layout.addWidget(self.subcategory_input)

        # Hosted By
        self.hosted_label = QLabel("Hosted By:")
        self.hosted_input = QLineEdit()
        self.form_layout.addWidget(self.hosted_label)
        self.form_layout.addWidget(self.hosted_input)

        # Number of People Coming
        self.people_label = QLabel("Number of People Coming:")
        self.people_input = QLineEdit()


        self.form_layout.addWidget(self.people_label)
        self.form_layout.addWidget(self.people_input)


        self.form_layout.addWidget(QLabel("Venue"))
        self.venue_dropdown = QComboBox()
        self.form_layout.addWidget(self.venue_dropdown)

        self.main_layout.addLayout(self.form_layout)

    def create_buttons(self):
        """Create buttons for form actions."""
        self.button_layout = QHBoxLayout()
        self.button_layout2 = QHBoxLayout()

        # Add Event Button
        self.add_event_button = QPushButton("Add Event")
        self.add_event_button.clicked.connect(self.add_event)
        self.button_layout.addWidget(self.add_event_button)

        # Update Event Button
        self.update_event_button = QPushButton("Update Event")
        self.update_event_button.clicked.connect(self.update_event)
        self.button_layout.addWidget(self.update_event_button)

        # Cancel Event Button
        self.cancel_event_button = QPushButton("Cancel Event")
        self.cancel_event_button.clicked.connect(self.cancel_event)
        self.button_layout.addWidget(self.cancel_event_button)

        # Filter Event Button
        self.filter_event_button = QPushButton("Filter by Category")
        self.filter_event_button.clicked.connect(self.filter_event)
        self.button_layout2.addWidget(self.filter_event_button)

        self.export_button = QPushButton("Export Events")
        self.export_button.clicked.connect(self.export_events)
        self.button_layout2.addWidget(self.export_button)

        # Import Events Button
        self.import_button = QPushButton("Import Events")
        self.import_button.clicked.connect(self.import_events)
        self.button_layout2.addWidget(self.import_button)

        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(self.button_layout2)

    def export_events(self):
        """Export events to a CSV file."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Events", "", "CSV Files (*.csv);;All Files (*)",
                                                   options=options)

        if file_name:
            try:
                with open(file_name, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        ["ID", "Name", "Time", "Place", "Category", "SubCategory", "Hosted By", "People Coming",
                         "Status"])  # Header

                    self.cursor.execute("SELECT * FROM events")
                    events = self.cursor.fetchall()
                    writer.writerows(events)  # Write data
                QMessageBox.information(self, "Export Successful", f"Events exported successfully to {file_name}!")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export events: {e}")

    def import_events(self):
        """Import events from a CSV file."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Events", "", "CSV Files (*.csv);;All Files (*)",
                                                   options=options)

        if file_name:
            try:
                with open(file_name, mode='r') as file:
                    reader = csv.reader(file)
                    next(reader)  # Skip header
                    for row in reader:
                        # Ensure the row has the correct number of fields before inserting
                        if len(row) == 9:  # Adjust based on your table structure
                            self.cursor.execute("""
                                INSERT INTO events (id, name, time, place, category, subcategory, hosted_by, people_coming, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, row)
                    self.conn.commit()
                self.load_events()  # Refresh the events table
                QMessageBox.information(self, "Import Successful", f"Events imported successfully from {file_name}!")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import events: {e}")

    def add_event(self):
        """Add an event to the database and update the table."""
        name = self.name_input.text()
        time = f"{self.date_input.text()} {self.time_input.text()}"
        place = self.venue_dropdown.currentText()
        category = self.category_input.currentText()
        subcategory = self.subcategory_input.text()
        hosted_by = self.hosted_input.text()
        people_coming = self.people_input.text()

        if not name or not time or not place:
            QMessageBox.warning(self, "Input Error", "Please fill out the required fields.")
            return

        try:
            # Insert the event into the database
            self.cursor.execute("""
                        INSERT INTO events (name, time, place, category, subcategory, hosted_by, people_coming, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (name, time, place, category, subcategory, hosted_by, people_coming, 'ongoing'))
            self.conn.commit()

            # Clear inputs
            self.clear_inputs()
            self.load_available_venues()
            # Reload events in table
            self.load_events()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add event: {e}")

    def load_events(self):
        """Load events from the database into the table."""

        today = QDate.currentDate().toString("yyyy-MM-dd")
        todaywithtime = QTime.currentTime().toString("HH:mm:ss")

        self.cursor.execute("SELECT id FROM events WHERE status='ongoing' and date(time) <= ? and TIME(time) < ?", (today, todaywithtime))
        eventsID = self.cursor.fetchall()
        for i in eventsID:
            self.complete_event(i[0])
        self.event_table.setRowCount(0)  # Clear the table first
        self.cursor.execute("SELECT * FROM events where status='ongoing'")
        events = self.cursor.fetchall()

        for row_num, event in enumerate(events):
            self.event_table.insertRow(row_num)
            for col_num, data in enumerate(event):
                self.event_table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def update_event(self):
        """Update the selected event."""
        selected_row = self.event_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select an event to update.")
            return

        event_id = self.event_table.item(selected_row, 0).text()

        # Update data based on form inputs
        name = self.name_input.text()
        time = f"{self.date_input.text()} {self.time_input.text()}"
        place = self.venue_dropdown.currentText()
        category = self.category_input.currentText()
        subcategory = self.subcategory_input.text()
        hosted_by = self.hosted_input.text()
        people_coming = self.people_input.text()

        try:
            self.cursor.execute(
                "UPDATE events SET name=?, time=?, place=?, category=?, subcategory=?, hosted_by=?, people_coming=? WHERE id=?",
                (name, time, place, category, subcategory, hosted_by, people_coming, event_id)
            )
            self.conn.commit()
            self.load_events()
            self.load_available_venues()
            QMessageBox.information(self, "Update", "Event updated successfully!")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update event: {e}")

    def cancel_event(self):
        """Cancel the selected event."""
        selected_row = self.event_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select an event to cancel.")
            return

        event_id = self.event_table.item(selected_row, 0).text()

        reply = QMessageBox.question(self, "Cancel Event", "Are you sure you want to cancel this event?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("""
                            UPDATE events SET status = 'canceled' WHERE id = ?
                        """, (event_id,))
                self.conn.commit()
                self.load_available_venues()
                self.load_events()
                QMessageBox.information(self, "Canceled", "Event canceled successfully!")

            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"Failed to cancel event: {e}")

    def complete_event(self, event_id):
        """Mark an event as completed."""
        self.cursor.execute("""
            UPDATE events SET status = 'completed' WHERE id = ?
        """, (event_id,))
        self.conn.commit()

        # Reload the available venues (since a venue is now free)
        self.load_available_venues()
        self.load_events()
    def filter_event(self):
        """Filter events based on category."""
        category = self.category_input.currentText()
        self.event_table.setRowCount(0)

        self.cursor.execute("SELECT * FROM events WHERE category=?", (category,))
        events = self.cursor.fetchall()

        for row_num, event in enumerate(events):
            self.event_table.insertRow(row_num)
            for col_num, data in enumerate(event):
                self.event_table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def check_today_events(self):
        """Check if there are any events happening today."""
        today = QDate.currentDate().toString("yyyy-MM-dd")
        todaywithtime = QTime.currentTime().toString("HH:mm:ss")

        self.cursor.execute("SELECT * FROM events WHERE date(time) = ? and TIME(time) >= ?", (today,todaywithtime))
        events = self.cursor.fetchall()
        # self.cursor.execute("SELECT * FROM events")
        # events1 = self.cursor.fetchall()
        # events =set()
        # for row_num, event in enumerate(events1):
        #     for col_num, data in enumerate(event):
        #         if(col_num==2 and today==data.split(" ")[0]):
        #             events.add(events1[row_num])
        if events:
            msg = "\n".join([f"{event[1]} at {event[2]} in {event[3]}" for event in events])
            QMessageBox.information(self, "Today's Events", f"The following events are happening today:\n\n{msg}")
        else:
            QMessageBox.information(self, "Today's Events", "No events happening today.")

    def clear_inputs(self):
        """Clear form inputs."""
        self.name_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.time_input.setTime(QTime.currentTime())
        self.subcategory_input.clear()
        self.hosted_input.clear()
        self.people_input.clear()


def main():
    app = QApplication(sys.argv)
    window = EventManagementSystem()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
