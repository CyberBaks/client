import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        DROP TABLE IF EXISTS phone;
        DROP TABLE IF EXISTS "user";
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS "user"(
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(255) NOT NULL,
        last_name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE
        );
        """)
        conn.commit()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS phone(
        id SERIAL PRIMARY KEY,
        id_number INTEGER REFERENCES "user"(id),
        phone VARCHAR(255) NOT NULL
        );
        """)
        conn.commit()


def add_client(conn, first_name, last_name, email):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO "user" (first_name, last_name, email)
        VALUES (%s, %s, %s)
        RETURNING id, first_name, last_name, email;
        """, (first_name, last_name, email))
        conn.commit()
        return cur.fetchone()

def add_phone(conn, id_number, phone):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO phone (id_number, phone)
        VALUES (%s, %s)
        RETURNING id, phone;
        """, (id_number, phone))
        conn.commit()
        return cur.fetchone()

def change_client(conn, id, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
        UPDATE "user" SET first_name=%s, last_name=%s, email=%s
        WHERE id=%s
        RETURNING id, first_name, last_name, email;
        """, (first_name, last_name, email, id))
        conn.commit()
        return cur.fetchone()

def change_phone(conn, id_number, name=None, lastname=None, email=None, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
        UPDATE "phone" SET phone=%s
        WHERE id_number=%s
        RETURNING id_number, phone;
        """, (phone, id_number))
        conn.commit()
        return cur.fetchone()

def delete_phone(conn, id_number, phone):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM phone
        WHERE id_number=%s AND phone=%s;""", (id_number, phone))
        conn.commit()
        return 'Номер успешно удалён'

def delete_client(conn, id):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM "user"
        WHERE id=%s
        """, (id))
        conn.commit()
        return 'Пользователь успешно удалён'

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
        SELECT u.id, u.first_name, u.last_name, u.email, phone.phone FROM "user" as u
        LEFT JOIN phone ON phone.id_number = u.id
        WHERE u.first_name=%s or u.last_name=%s or u.email=%s or phone.phone=%s;
        """,(first_name, last_name, email, phone))
        conn.commit()
        return cur.fetchone()


with psycopg2.connect(database="netology_db", user="postgres", password="root") as conn:
    create_db(conn)

    usr = add_client(conn, 'Anastasia', 'Dybianskaya', 'anastasia@example.com')
    usr_phone = add_phone(conn, '1', '123-456-789')
    usr_update = change_client(conn, '1', 'Janna', 'Nemovna', 'newemail@gmail.com')
    usr_changePhone = change_phone(conn, '1', phone='88811144499')

    print(f'Создан новый пользователь: ID: {usr[0]}, Имя: {usr[1]}, Фамилия: {usr[2]}, email: {usr[3]}')
    print(f'Пользователю добавлен номер телефона: ID: {usr_phone[0]}, Номер телефона: {usr_phone[1]}')
    print(f'Пользователь изменил данные: ID: {usr_update[0]}, Имя: {usr_update[1]}, Фамилия: {usr_update[2]}, email: {usr_update[3]}')
    print(f'Пользователь изменил номер: ID: {usr_changePhone[0]}, Номер: {usr_changePhone[1]}')
    print(delete_phone(conn, '1', '88811144499'))
    print(delete_client(conn, '1'))
    print(find_client(conn, 'Janna'))
conn.close()