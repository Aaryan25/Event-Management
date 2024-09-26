import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QDialog
)
import sys


class AuthDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("User Authentication")
        self.setGeometry(600, 300, 300, 200)

        self.layout = QVBoxLayout()

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.signup_button = QPushButton("Sign Up")
        self.signup_button.clicked.connect(self.signup)

        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.signup_button)

        self.setLayout(self.layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return

        conn = sqlite3.connect("events.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            QMessageBox.information(self, "Login Successful", "Welcome to the Event Management System!")
            self.accept()  # Close dialog
        else:
            QMessageBox.warning(self, "Login Error", "Invalid username or password.")

    def signup(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return

        conn = sqlite3.connect("events.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            QMessageBox.information(self, "Sign Up Successful", "You can now log in with your credentials.")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Sign Up Error", "Username already exists. Choose another username.")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to sign up: {e}")
        finally:
            conn.close()


class EventManagementSystem(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Management System")
        self.setGeometry(500, 100, 900, 800)

        # Database connection
        self.conn = sqlite3.connect("events.db")
        self.cursor = self.conn.cursor()
        self.create_user_table()

        # Auth Dialog
        self.auth_dialog = AuthDialog()
        if not self.auth_dialog.exec_():
            sys.exit()  # Exit if login fails or dialog is closed

        # Layouts and other components...
        # Here you would continue with the rest of your system setup

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


def main():
    app = QApplication(sys.argv)
    window = EventManagementSystem()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
