import json
import csv
import psycopg2
from config import load_config


def get_connection():
    params = load_config()
    return psycopg2.connect(**params)


def show_all_contacts():
    sql = """
        SELECT c.id, c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        ORDER BY c.id;
    """

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


def add_contact():
    name = input("Enter name: ")
    email = input("Enter email: ")
    birthday = input("Enter birthday YYYY-MM-DD: ")
    group_name = input("Enter group Family/Work/Friend/Other: ")
    phone = input("Enter phone: ")
    phone_type = input("Enter phone type home/work/mobile: ")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO groups(name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING;
        """, (group_name,))

        cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
        group_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE
            SET email = EXCLUDED.email,
                birthday = EXCLUDED.birthday,
                group_id = EXCLUDED.group_id
            RETURNING id;
        """, (name, email, birthday, group_id))

        contact_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO phones(contact_id, phone, type)
            VALUES (%s, %s, %s);
        """, (contact_id, phone, phone_type))

        conn.commit()
        print("Contact added or updated successfully")

        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def add_phone_to_contact():
    name = input("Enter contact name: ")
    phone = input("Enter new phone: ")
    phone_type = input("Enter phone type home/work/mobile: ")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
        conn.commit()

        print("Phone added")

        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def move_contact_to_group():
    name = input("Enter contact name: ")
    group_name = input("Enter new group: ")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
        conn.commit()

        print("Contact moved to group")

        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def search_contacts():
    query = input("Enter search query: ")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
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


def filter_by_group():
    group_name = input("Enter group name: ")

    sql = """
        SELECT c.id, c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE g.name = %s
        ORDER BY c.name;
    """

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(sql, (group_name,))
        rows = cur.fetchall()

        if rows:
            for row in rows:
                print(row)
        else:
            print("No contacts in this group")

        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def sort_contacts():
    print("Sort by: name / birthday / created_at")
    sort_by = input("Enter field: ")

    allowed = ["name", "birthday", "created_at"]

    if sort_by not in allowed:
        print("Invalid sort field")
        return

    sql = f"""
        SELECT c.id, c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.{sort_by};
    """

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(sql)
        rows = cur.fetchall()

        for row in rows:
            print(row)

        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def paginated_navigation():
    limit = 3
    offset = 0

    while True:
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT c.id, c.name, c.email, c.birthday, g.name
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                ORDER BY c.id
                LIMIT %s OFFSET %s;
            """, (limit, offset))

            rows = cur.fetchall()

            print("\n--- PAGE ---")
            if rows:
                for row in rows:
                    print(row)
            else:
                print("No contacts")

            cur.close()
            conn.close()

            command = input("next / prev / quit: ")

            if command == "next":
                offset += limit
            elif command == "prev":
                offset = max(0, offset - limit)
            elif command == "quit":
                break
            else:
                print("Invalid command")

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            break


def export_to_json():
    filename = input("Enter JSON filename: ")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT c.name, c.email, c.birthday, g.name, p.phone, p.type
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON c.id = p.contact_id
            ORDER BY c.name;
        """)

        rows = cur.fetchall()

        data = []
        for row in rows:
            data.append({
                "name": row[0],
                "email": row[1],
                "birthday": str(row[2]) if row[2] else None,
                "group": row[3],
                "phone": row[4],
                "phone_type": row[5]
            })

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print("Export completed")

        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def import_from_json():
    filename = input("Enter JSON filename: ")

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        conn = get_connection()
        cur = conn.cursor()

        for item in data:
            cur.execute("""
                INSERT INTO groups(name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING;
            """, (item["group"],))

            cur.execute("SELECT id FROM groups WHERE name = %s", (item["group"],))
            group_id = cur.fetchone()[0]

            cur.execute("SELECT id FROM contacts WHERE name = %s", (item["name"],))
            existing = cur.fetchone()

            if existing:
                answer = input(f"{item['name']} exists. overwrite/skip: ")
                if answer == "skip":
                    continue

                cur.execute("""
                    UPDATE contacts
                    SET email = %s, birthday = %s, group_id = %s
                    WHERE name = %s
                    RETURNING id;
                """, (item["email"], item["birthday"], group_id, item["name"]))
                contact_id = cur.fetchone()[0]

                cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
            else:
                cur.execute("""
                    INSERT INTO contacts(name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                """, (item["name"], item["email"], item["birthday"], group_id))
                contact_id = cur.fetchone()[0]


            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s);
            """, (contact_id, item["phone"], item["phone_type"]))

        conn.commit()
        print("Import completed")

        cur.close()
        conn.close()

    except Exception as error:
        print(error)


def delete_contact():
    name = input("Enter contact name to delete: ")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
        conn.commit()

        print("Contact deleted")

        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def menu():
    while True:
        print("\n--- EXTENDED PHONEBOOK MENU ---")
        print("1. Show all contacts")
        print("2. Add or update contact")
        print("3. Add phone to contact")
        print("4. Move contact to group")
        print("5. Search contacts")
        print("6. Filter by group")
        print("7. Sort contacts")
        print("8. Paginated navigation")
        print("9. Export to JSON")
        print("10. Import from JSON")
        print("11. Delete contact")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            show_all_contacts()
        elif choice == "2":
            add_contact()
        elif choice == "3":
            add_phone_to_contact()
        elif choice == "4":
            move_contact_to_group()
        elif choice == "5":
            search_contacts()
        elif choice == "6":
            filter_by_group()
        elif choice == "7":
            sort_contacts()
        elif choice == "8":
            paginated_navigation()
        elif choice == "9":
            export_to_json()
        elif choice == "10":
            import_from_json()
        elif choice == "11":
            delete_contact()
        elif choice == "0":
            print("Goodbye")
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    menu()