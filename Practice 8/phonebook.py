import psycopg2
from config import load_config


def get_connection():
    params = load_config()
    return psycopg2.connect(**params)


def show_all_contacts():
    sql = "SELECT * FROM phonebook ORDER BY id"
    try:
        conn = get_connection()
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


def search_by_pattern():
    pattern = input("Enter pattern: ")
    sql = "SELECT * FROM search_phonebook(%s)"

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(sql, (pattern,))
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


def get_paginated_contacts():
    try:
        lim = int(input("Enter LIMIT: "))
        off = int(input("Enter OFFSET: "))

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM get_phonebook_page(%s, %s)", (lim, off))
        rows = cur.fetchall()

        if rows:
            for row in rows:
                print(row)
        else:
            print("No contacts found")

        cur.close()
        conn.close()

    except ValueError:
        print("Limit and offset must be integers")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def insert_or_update_one_user():
    name = input("Enter name: ")
    phone = input("Enter phone: ")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("CALL insert_or_update_user(%s, %s)", (name, phone))
        conn.commit()

        print("User inserted or updated successfully")

        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def insert_many_users():
    try:
        n = int(input("How many users do you want to enter? "))
        names = []
        phones = []

        for i in range(n):
            print(f"\nUser {i + 1}")
            name = input("Enter name: ")
            phone = input("Enter phone: ")
            names.append(name)
            phones.append(phone)

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("CALL insert_many_users(%s, %s)", (names, phones))
        conn.commit()

        print("Bulk insert procedure executed")

        cur.close()
        conn.close()

    except ValueError:
        print("Please enter a valid number")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def delete_user():
    value = input("Enter name or phone to delete: ")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("CALL delete_user(%s)", (value,))
        conn.commit()

        print("Delete procedure executed")

        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def menu():
    while True:
        print("\n--- PHONEBOOK MENU ---")
        print("1. Show all contacts")
        print("2. Search contacts by pattern")
        print("3. Insert or update one user")
        print("4. Insert many users")
        print("5. Show contacts with pagination")
        print("6. Delete user")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            show_all_contacts()

        elif choice == "2":
            search_by_pattern()

        elif choice == "3":
            insert_or_update_one_user()

        elif choice == "4":
            insert_many_users()

        elif choice == "5":
            get_paginated_contacts()

        elif choice == "6":
            delete_user()

        elif choice == "7":
            print("Goodbye")
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    menu()