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

        cur.execute("""
        CREATE TABLE IF NOT EXISTS phone(
        id SERIAL PRIMARY KEY,
        id_number INTEGER REFERENCES "user"(id),
        phone VARCHAR(255) NOT NULL
        );
        """)


def add_client(conn, first_name, last_name, email):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO "user" (first_name, last_name, email)
        VALUES (%s, %s, %s)
        RETURNING id, first_name, last_name, email;
        """, (first_name, last_name, email))
        return cur.fetchone()

def add_phone(conn, id_number, phone):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO phone (id_number, phone)
        VALUES (%s, %s)
        RETURNING id, phone;
        """, (id_number, phone))
        return cur.fetchone()

def change_client(conn, id, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
        UPDATE "user" SET 
        first_name = COALESCE(%s, first_name),
        last_name = COALESCE(%s, last_name),
        email = COALESCE(%s, email)
        WHERE id = %s
        RETURNING id, first_name, last_name, email;
        """, (first_name, last_name, email, id))
        return cur.fetchone()

def change_phone(conn, id_number, name=None, lastname=None, email=None, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
        UPDATE "phone" SET phone=%s
        WHERE id_number=%s
        RETURNING id_number, phone;
        """, (phone, id_number))
        return cur.fetchone()

def delete_phone(conn, id_number, phone):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM phone
        WHERE id_number=%s AND phone=%s;""", (id_number, phone))
        return 'Номер успешно удалён'

def delete_client(conn, id):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM phone
        WHERE id_number=%s
        """, (id))

        cur.execute("""
        DELETE FROM "user"
        WHERE id=%s
        """, (id))
        return 'Пользователь успешно удалён'

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
        SELECT u.id, u.first_name, u.last_name, u.email, phone.phone FROM "user" as u
        LEFT JOIN phone ON phone.id_number = u.id
        WHERE (%(first_name)s IS NULL OR u.first_name = %(first_name)s)
        AND (%(last_name)s IS NULL OR u.last_name = %(last_name)s)
        AND (%(email)s IS NULL OR u.email = %(email)s)
        AND (%(phone)s IS NULL OR phone.phone = %(phone)s);
        """, {"first_name": first_name, "last_name": last_name, "email": email, "phone": phone})
        return cur.fetchone()

if __name__ == "__main__":
    with psycopg2.connect(database="netology_db", user="postgres", password="root") as conn:
        create_db(conn)

        usr = add_client(conn, 'Anastasia', 'Dybianskaya', 'anastasia@example.com')
        usr_phone = add_phone(conn, '1', '123-456-789')
        #usr_update = change_client(conn, '1', 'Janna', 'Nemovna', 'newemail@gmail.com')
        usr_changePhone = change_phone(conn, '1', phone='88811144499')

        print(f'Создан новый пользователь: ID: {usr[0]}, Имя: {usr[1]}, Фамилия: {usr[2]}, email: {usr[3]}')
        print(f'Пользователю добавлен номер телефона: ID: {usr_phone[0]}, Номер телефона: {usr_phone[1]}')
        print(change_client(conn, id='1', first_name='Inna', email='testemail@gmail.com'))
        #print(f'Пользователь изменил номер: ID: {usr_changePhone[0]}, Номер: {usr_changePhone[1]}')
        #print(delete_phone(conn, '1', '88811144499'))
        #print(delete_client(conn, '1'))
        print(find_client(conn, phone='88811144499', last_name='Dybianskaya'))
