import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
import calendar

from nltk.chat.util import Chat, reflections

from cryptography.fernet import Fernet


class PasswordKeeper:

    def __init__(self):
        self.passwords = {}
        self.key = None

    def generate_key(self):
        self.key = Fernet.generate_key()

    def encrypt_password(self, password):
        if not self.key:
            raise ValueError("Encryption key not generated.")
        cipher_suite = Fernet(self.key)
        encrypted_password = cipher_suite.encrypt(password.encode())
        return encrypted_password

    def decrypt_password(self, encrypted_password):
        if not self.key:
            raise ValueError("Encryption key not generated.")
        cipher_suite = Fernet(self.key)
        decrypted_password = cipher_suite.decrypt(encrypted_password).decode()
        return decrypted_password

    def add_password(self, website, username, password):
        encrypted_password = self.encrypt_password(password)
        self.passwords[website] = (username, encrypted_password)

    def get_password(self, website):
        if website in self.passwords:
            username, encrypted_password = self.passwords[website]
            decrypted_password = self.decrypt_password(encrypted_password)
            return f"Website: {website}, Username: {username}, Password: {decrypted_password}"
        else:
            return "Website not found in password keeper."

    def view_passwords(self):
        if not self.passwords:
            return "No passwords saved in the password keeper."
        password_list = []
        for website in self.passwords:
            password_list.append(self.get_password(website))
        return "\n".join(password_list)

class DesktopAssistant:

    def __init__(self):
        self.reminders = []
        self.todo_list = []

        self.engine = pyttsx3.init()
        self.chatbot = Chat(self.get_responses(), reflections)
        self.password_keeper = PasswordKeeper()
        self.password_keeper.generate_key()





    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def set_a_reminder(self, reminder, time):
        self.reminders.append((reminder, time))
        print(f"Reminder added: '{reminder}' at {time}")

    def add_todo(self, task):
        self.todo_list.append(task)
        print("Task added to the to-do list:", task)

    def view_reminders(self):
        while True:
            if not self.reminders:
                print("You have no reminders.")
                break
            else:
                print("Your Reminders:")
                for idx, reminder in enumerate(self.reminders, start=1):
                    print(f"{idx}. {reminder[0]} at {reminder[1]}")
                break

    def view_todo_list(self):
        while True:
            if not self.todo_list:
                print("Your to-do list is empty.")
                break
            else:
                print("Your To-Do List:")
                for idx, task in enumerate(self.todo_list, start=1):
                    print(f"{idx}. {task}")
                break

    def takeCommand(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("Listening...")
            try:
                audio = r.listen(source)
                print("Recognizing...")
                query = r.recognize_google(audio, language="en-in")
                print(f"User said: {query}")
                return query
            except sr.UnknownValueError:
                print("Sorry, I didn't understand that.")
                return ""
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return ""

    def takeTypingInput(self, prompt="Type your command: "):
        while True:
            print(prompt, end="")
            query = input()
            return query.lower()


    def show_calendar(self):
        while True:
            now = datetime.datetime.now()
            year = now.year
            month = now.month

            cal = calendar.month(year, month)
            calendar_text = f"Showing calendar for {calendar.month_name[month]} {year}:"
            print(calendar_text)
            self.speak(calendar_text)
            print(cal)
            break


    def calculator(self, expression=None):
        while True:
            if expression is None:
                self.speak(" please enter the mathematical expression.")
                expression = self.takeCommand()
            try:
                result = eval(expression)
                result_text = f"Result: {result}"
                print(result_text)
                self.speak(result_text)
            except Exception as e:
                error_text = f"Error calculating: {e}"
                print(error_text)
                self.speak("Sorry, I couldn't calculate that.")
            break

    def run(self):
        print("Welcome to your personal assistant")
        self.speak("Welcome to your personal assistant")

        while True:
            print("Choose input method:")
            print("1. Speech Recognition")
            print("2. Typing")
            print("3. Exit")
            choice = input()

            if choice == "3":
                break
            elif choice == "1":
                query = self.takeCommand()
            elif choice == "2":
                query = self.takeTypingInput("Please enter your command: ")
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
                continue

            response = self.chatbot.respond(query)
            if response:
                print("Assistant:", response)
                self.speak(response)

            sites = [["YouTube", "https://www.youtube.com"], ["Wikipedia", "https://www.wikipedia.com"],
                     ["Google", "https://www.google.com"]]
            for site in sites:
                if f"open {site[0]}".lower() in query.lower():
                    self.speak(f"Opening {site[0]} ")
                    webbrowser.open(site[1])
                    break
            if "the time" in query.lower():
                strfTime = datetime.datetime.now().strftime("%H:%M:%S")
                print (f"The time is {strfTime}")
                self.speak(f"The time is {strfTime}")

            if "set a reminder" in query.lower():
                print("Add your reminder:")
                reminder = self.takeTypingInput("Please enter your reminder: ")
                print("Enter time in HH:MM AM/PM format:")
                time = self.takeTypingInput("Please enter the time: ")
                self.set_a_reminder(reminder, time)

            if "add task" in query.lower():
                task = self.takeTypingInput("Add your task to the to-do list:")
                self.add_todo(task)

            if "view reminders" in query.lower():
                self.view_reminders()

            if "view to do list" in query.lower():
                self.view_todo_list()

            if 'calculator' in query.lower():
                calc_expression = self.takeTypingInput("Please enter the mathematical expression: ")
                self.calculator(calc_expression)

            if "show calendar" in query.lower():
                self.show_calendar()

            if "add password" in query.lower():
                print("Enter website:")
                website = self.takeTypingInput()
                print("Enter username:")
                username = self.takeTypingInput()
                print("Enter password:")
                password = self.takeTypingInput()
                self.password_keeper.add_password(website, username, password)
                print("Password saved.")

            if "get password" in query.lower():
                print("Enter website for which you want the password:")
                website = self.takeTypingInput()
                password_info = self.password_keeper.get_password(website)
                print(password_info)

            if "view passwords" in query.lower():
                password_list = self.password_keeper.view_passwords()
                print(password_list)

    def get_responses(self):
        responses = [
            (r"hello|hi", ["Hello!", "Hi there!"]),
            (r"how are you", ["I'm good, thanks.", "I'm doing well, how about you?"]),
            (r"what's your name|who are you", ["I'm your assistant.", "I'm an AI assistant."]),

        ]
        return responses


if __name__ == '__main__':
    assistant = DesktopAssistant()
    assistant.run()

