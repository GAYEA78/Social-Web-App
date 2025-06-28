import psycopg2
from psycopg2.extras import execute_values
from flask_bcrypt import Bcrypt

# Initialize bcrypt for password hashing
bcrypt = Bcrypt()

DATABASE_URL = "postgresql://social_web_app_s6s9_user:1Plv8JdbQBwV4jRXHuqD0fHC0f8F9kyu@dpg-d1fesa2dbo4c739v6tvg-a.ohio-postgres.render.com/social_web_app_s6s9"

def create_or_update_user(c, username, email, password, role):
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    c.execute("SELECT resident_id FROM resident WHERE email=%s", (email,))
    existing_user = c.fetchone()
    if existing_user:
        c.execute("""
            UPDATE resident SET username=%s, password_hash=%s, role=%s WHERE email=%s
        """, (username, password_hash, role, email))
    else:
        c.execute("""
            INSERT INTO resident (username, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET username=EXCLUDED.username
        """, (username, email, password_hash, role))

def create_test_activity_groups(c):
    test_groups = [
        ('Kpop Dance', 'Dance', 'A group for Kpop dance lovers', '2020-01-01', 'http://kpopdance.com', 'kpop@example.com', '555-5678', '{"instagram": "@kpopdance"}', True, 10, 'weekly', 0, True, 18),
        ('Boston Book Club', 'Literature', 'A club for book lovers in Boston', '2018-03-15', 'http://bostonbookclub.com', 'books@example.com', '555-2345', '{"facebook": "@bostonbookclub"}', True, 25, 'monthly', 10, True, 16),
        ('Boston Runners', 'Sports', 'Running group for all levels', '2015-06-10', 'http://bostonrunners.com', 'run@example.com', '555-3456', '{"instagram": "@bostonrunners"}', True, 40, 'weekly', 0, True, 18),
        ('Boston Chess Masters', 'Games', 'For chess enthusiasts and learners', '2019-09-01', 'http://bostonchess.com', 'chess@example.com', '555-4567', '{"twitter": "@bostonchess"}', True, 15, 'biweekly', 5, True, 12),
        ('Boston Foodies', 'Food', 'Exploring Boston one restaurant at a time', '2021-02-20', 'http://bostonfoodies.com', 'food@example.com', '555-5679', '{"instagram": "@bostonfoodies"}', True, 30, 'monthly', 20, True, 21),
        ('Boston Coders', 'Technology', 'A group for coding enthusiasts', '2017-11-05', 'http://bostoncoders.com', 'code@example.com', '555-6789', '{"github": "bostoncoders"}', True, 50, 'weekly', 0, True, 16),
    ]

    execute_values(c, """
        INSERT INTO activity_group
        (name, category, description, founding_date, website, email, phone_number,
        social_media_links, is_active, total_members, event_frequency,
        membership_fee, open_to_public, min_age)
        VALUES %s
        ON CONFLICT (name) DO NOTHING
    """, test_groups)

def main():
    # Connect to Postgres database
    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()
    try:
        print("Connected to the database!")

        #  Create test users
        create_or_update_user(c, 'admin', 'admin@example.com', 'admin123', 'admin')
        create_or_update_user(c, 'testuser', 'user@example.com', 'user123', 'user')
        create_or_update_user(c, 'testuser2', 'user2@example.com', 'user123', 'user')
        create_or_update_user(c, 'testuser3', 'user3@example.com', 'user123', 'user')

        #  Create test activity groups
        create_test_activity_groups(c)


        conn.commit()
        print("\n Test data created successfully!")
        print("\nTest accounts created:")
        print("Admin - Username: admin, Password: admin123")
        print("User - Username: testuser, Password: user123")
        print("User - Username: testuser2, Password: user123")
        print("User - Username: testuser3, Password: user123")
    except Exception as e:
        print(f"\n Error creating test data: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == '__main__':
    main()
