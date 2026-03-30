import csv
import psycopg2
from config import load_config


def create_table():
    command = """
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        phone VARCHAR(20) NOT NULL
    )
    """
    try:
        params = load_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        cur.execute(command)
        conn.commit()

        cur.close()
        conn.close()
        print("Table created successfully")

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def insert_contact(name, phone):
    sql = """
    INSERT INTO phonebook (name, phone)
    VALUES (%s, %s)
    """
    try:
        params = load_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        cur.execute(sql, (name, phone))
        conn.commit()

        cur.close()
        conn.close()
        print("Contact inserted successfully")

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def insert_from_csv(filename):
    sql = """
    INSERT INTO phonebook (name, phone)
    VALUES (%s, %s)
    """
    try:
        params = load_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        with open(filename, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                cur.execute(sql, (row[0], row[1]))

        conn.commit()

        cur.close()
        conn.close()
        print("Contacts inserted from CSV successfully")

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def show_contacts():
    sql = "SELECT * FROM phonebook"
    try:
        params = load_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        cur.execute(sql)
        rows = cur.fetchall()

        if rows:
            for row in rows:
                print(row)
        else:
            print("Phonebook is empty")

        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def search_contact(pattern):
    sql = """
    SELECT * FROM phonebook
    WHERE name ILIKE %s OR phone ILIKE %s
    """
    try:
        params = load_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        cur.execute(sql, (pattern + "%", pattern + "%"))
        rows = cur.fetchall()

        if rows:
            for row in rows:
                print(row)
        else:
            print("No contacts found")

        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def update_contact(contact_id, new_name, new_phone):
    sql = """
    UPDATE phonebook
    SET name = %s, phone = %s
    WHERE id = %s
    """
    try:
        params = load_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        cur.execute(sql, (new_name, new_phone, contact_id))
        conn.commit()

        if cur.rowcount > 0:
            print("Contact updated successfully")
        else:
            print("Contact not found")

        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def delete_contact(value):
    sql = """
    DELETE FROM phonebook
    WHERE name = %s OR phone = %s
    """
    try:
        params = load_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        cur.execute(sql, (value, value))
        conn.commit()

        if cur.rowcount > 0:
            print("Contact deleted successfully")
        else:
            print("Contact not found")

        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def menu():
    while True:
        print("\n--- PHONEBOOK MENU ---")
        print("1. Create table")
        print("2. Insert contact from console")
        print("3. Insert contacts from CSV")
        print("4. Show all contacts")
        print("5. Search contacts")
        print("6. Update contact")
        print("7. Delete contact")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            create_table()

        elif choice == "2":
            name = input("Enter name: ")
            phone = input("Enter phone: ")
            insert_contact(name, phone)

        elif choice == "3":
            filename = input("Enter CSV filename: ")
            insert_from_csv(filename)

        elif choice == "4":
            show_contacts()

        elif choice == "5":
            pattern = input("Enter name or phone prefix: ")
            search_contact(pattern)

        elif choice == "6":
            contact_id = int(input("Enter contact id: "))
            new_name = input("Enter new name: ")
            new_phone = input("Enter new phone: ")
            update_contact(contact_id, new_name, new_phone)

        elif choice == "7":
            value = input("Enter name or phone to delete: ")
            delete_contact(value)

        elif choice == "8":
            print("Goodbye")
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    menu()