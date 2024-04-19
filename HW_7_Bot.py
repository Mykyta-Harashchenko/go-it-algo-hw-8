from collections import defaultdict, UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():
            self.__value = value
        else:
            raise ValueError('Invalid phone number')


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            raise ValueError('Incorrect date format, please enter in the format: dd.mm.yyyy')


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        self.phones = [p for p in self.phones if str(p) != phone_number]

    def edit_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if str(phone) == old_phone:
                self.phones[i] = Phone(new_phone)
        if str(phone) != old_phone:
            raise ValueError("Old phone number not found in the contact's phones.")

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)



    def __str__(self):
        phones_str = '; '.join(str(phone) for phone in self.phones)
        birthday_str = f', birthday: {self.birthday.value}' if self.birthday else ''
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def find_next_birthday(self, weekday):
        self.today = datetime.today().date()
        upcoming_birthdays = []

        for user in self.data.values():
            birthday_date = datetime.strptime(user.birthday.value, "%d.%m.%Y").date()

            birthday_this_year = datetime(self.today.year, birthday_date.month, birthday_date.day).date()

            if birthday_this_year < self.today:
                birthday_this_year = datetime(self.today.year + 1, birthday_date.month, birthday_date.day).date()

            days_until_birthday = (birthday_this_year - self.today).days

            if 0 <= days_until_birthday <= 7:
                if birthday_this_year.weekday() >= 5:
                    next_monday = self.today + timedelta(days=(7 - self.today.weekday()))
                    congrats_date = next_monday
                else:
                    congrats_date = birthday_this_year

                upcoming_birthdays.append(
                    {"name": user.name.value, "congratulation_date": congrats_date.strftime("%Y.%m.%d")})

        return upcoming_birthdays


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Insufficient arguments. Required: name and phone number."
    name, phone = args[:2]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        return "Insufficient arguments. Required: name, old phone number, and new phone number."
    name, old_phone, new_phone = args[:3]
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone number updated successfully."
    else:
        raise KeyError("Contact not found.")


@input_error
def show_phones(args, book: AddressBook):
    if not args:
        return "Insufficient arguments. Required: name."
    name = args[0]
    record = book.find(name)
    if record:
        return ', '.join(str(phone) for phone in record.phones)
    else:
        raise KeyError("Contact not found.")


@input_error
def show_all(book: AddressBook):
    return '\n'.join(str(record) for record in book.values())


@input_error
def add_birthday(args, book: AddressBook):
    if len(args) < 2:
        return "Insufficient arguments. Required: name and birthday."
    name, birthday = args[:2]
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added/updated successfully."
    else:
        raise KeyError("Contact not found.")


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday.value}"
    else:
        raise KeyError("Contact not found or birthday not set.")


@input_error
def birthdays(args, book: AddressBook):
    upcoming_birthdays = book.find_next_birthday(weekday=None)
    return '\n'.join(f"{b['name']}'s birthday is on {b['congratulation_date']}" for b in upcoming_birthdays)


def parse_input(user_input):
    parts = user_input.split()
    cmd = parts[0].strip().lower() if parts else ""
    args = parts[1:] if len(parts) > 1 else []
    return cmd, args

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = AddressBook()
    book = load_data()
    print("Welcome to the address book bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phones(args, book))

        elif command == "all":
           print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

        save_data(book)

if __name__ == "__main__":
    main()