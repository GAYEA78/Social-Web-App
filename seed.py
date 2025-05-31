import os
import sqlite3
import logging
from flask_bcrypt import Bcrypt
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "activity.sqlite")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "app", "utils", "schema.sql")
bcrypt = Bcrypt()

def init_db():
    """Initialize the database schema"""
    # Ensure instance directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()
    
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema)
    conn.commit()
    log.info("Database schema initialized")

def create_or_update_user(username, email, password, role):
    """Create a new user or update an existing one"""
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    log.debug(f"Using hashed password for {username}: {password_hash}")
    
    # Check if user exists
    c.execute("SELECT resident_id FROM resident WHERE email = ?", (email,))
    existing_user = c.fetchone()
    
    if existing_user:
        # Update existing user
        c.execute(
            """
            UPDATE resident 
            SET username = ?, password_hash = ?, role = ?
            WHERE email = ?
            """,
            (username, password_hash, role, email)
        )
    else:
        # Create new user
        c.execute(
            """
            INSERT INTO resident (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (username, email, password_hash, role)
        )

def create_test_activity_groups():
    """Create test activity groups"""
    test_groups = [
        {
            'name': 'Kpop Dance',
            'category': 'Dance',
            'description': 'A group for Kpop dance lovers',
            'founding_date': '2020-01-01',
            'website': 'http://kpopdance.com',
            'email': 'kpop@example.com',
            'phone_number': '555-5678',
            'social_media_links': '{"instagram": "@kpopdance"}',
            'is_active': True,
            'total_members': 10,
            'event_frequency': 'weekly',
            'membership_fee': 0,
            'open_to_public': True,
            'min_age': 18
        },
        {
            'name': 'Boston Book Club',
            'category': 'Literature',
            'description': 'A club for book lovers in Boston',
            'founding_date': '2018-03-15',
            'website': 'http://bostonbookclub.com',
            'email': 'books@example.com',
            'phone_number': '555-2345',
            'social_media_links': '{"facebook": "@bostonbookclub"}',
            'is_active': True,
            'total_members': 25,
            'event_frequency': 'monthly',
            'membership_fee': 10,
            'open_to_public': True,
            'min_age': 16
        },
        {
            'name': 'Boston Runners',
            'category': 'Sports',
            'description': 'Running group for all levels',
            'founding_date': '2015-06-10',
            'website': 'http://bostonrunners.com',
            'email': 'run@example.com',
            'phone_number': '555-3456',
            'social_media_links': '{"instagram": "@bostonrunners"}',
            'is_active': True,
            'total_members': 40,
            'event_frequency': 'weekly',
            'membership_fee': 0,
            'open_to_public': True,
            'min_age': 18
        },
        {
            'name': 'Boston Chess Masters',
            'category': 'Games',
            'description': 'For chess enthusiasts and learners',
            'founding_date': '2019-09-01',
            'website': 'http://bostonchess.com',
            'email': 'chess@example.com',
            'phone_number': '555-4567',
            'social_media_links': '{"twitter": "@bostonchess"}',
            'is_active': True,
            'total_members': 15,
            'event_frequency': 'biweekly',
            'membership_fee': 5,
            'open_to_public': True,
            'min_age': 12
        },
        {
            'name': 'Boston Foodies',
            'category': 'Food',
            'description': 'Exploring Boston one restaurant at a time',
            'founding_date': '2021-02-20',
            'website': 'http://bostonfoodies.com',
            'email': 'food@example.com',
            'phone_number': '555-5679',
            'social_media_links': '{"instagram": "@bostonfoodies"}',
            'is_active': True,
            'total_members': 30,
            'event_frequency': 'monthly',
            'membership_fee': 20,
            'open_to_public': True,
            'min_age': 21
        },
        {
            'name': 'Boston Coders',
            'category': 'Technology',
            'description': 'A group for coding enthusiasts',
            'founding_date': '2017-11-05',
            'website': 'http://bostoncoders.com',
            'email': 'code@example.com',
            'phone_number': '555-6789',
            'social_media_links': '{"github": "bostoncoders"}',
            'is_active': True,
            'total_members': 50,
            'event_frequency': 'weekly',
            'membership_fee': 0,
            'open_to_public': True,
            'min_age': 16
        }
    ]
    
    for group in test_groups:
        c.execute(
            """
            INSERT OR REPLACE INTO activity_group 
            (name, category, description, founding_date, website, email, phone_number, 
             social_media_links, is_active, total_members, event_frequency, 
             membership_fee, open_to_public, min_age)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                group['name'], group['category'], group['description'],
                group['founding_date'], group['website'], group['email'],
                group['phone_number'], group['social_media_links'],
                group['is_active'], group['total_members'],
                group['event_frequency'], group['membership_fee'],
                group['open_to_public'], group['min_age']
            )
        )

def create_test_locations():
    """Create test locations"""
    boston_college_locations = [
        ("123 Main St", "Boston", "MA", "02118"),
        ("Gasson Hall", "Chestnut Hill", "MA", "02467"),
        ("Devlin Hall", "Chestnut Hill", "MA", "02467"),
        ("Bapst Library", "Chestnut Hill", "MA", "02467"),
        ("St. Mary's Hall", "Chestnut Hill", "MA", "02467"),
        ("Roberts Center", "Chestnut Hill", "MA", "02467"),
        ("McElroy Commons", "Chestnut Hill", "MA", "02467"),
        ("Carney Hall", "Chestnut Hill", "MA", "02467"),
        ("McGuinn Hall", "Chestnut Hill", "MA", "02467"),
        ("Higgins Hall", "Chestnut Hill", "MA", "02467"),
        ("Fulton Hall", "Chestnut Hill", "MA", "02467"),
        ("Thomas More Apartments", "Chestnut Hill", "MA", "02467"),
        ("Gabelli Hall", "Chestnut Hill", "MA", "02467"),
        ("Vanderslice Hall", "Chestnut Hill", "MA", "02467"),
        ("Stayer Hall", "Chestnut Hill", "MA", "02467"),
        ("Walsh Hall", "Chestnut Hill", "MA", "02467"),
        ("Fenwick Hall", "Chestnut Hill", "MA", "02467"),
        ("Claver Hall", "Chestnut Hill", "MA", "02467"),
        ("Cheverus Hall", "Chestnut Hill", "MA", "02467"),
        ("Gonzaga Hall", "Chestnut Hill", "MA", "02467")
    ]
    
    for address, city, state, zip_code in boston_college_locations:
        c.execute(
            """
            INSERT OR IGNORE INTO location (address, city, state, zip_code)
            VALUES (?, ?, ?, ?)
            """,
            (address, city, state, zip_code)
        )

def create_test_events():
    """Create test events"""
    events = [
        ('Kpop Dance', '2025-06-01', 1, 50, 0, 1, '2025-05-25'),
        ('Boston Book Club', '2025-07-15', 2, 30, 10, 1, '2025-07-10'),
        ('Boston Runners', '2025-08-20', 3, 100, 0, 1, '2025-08-15')
    ]
    
    for activity_group, date, location_id, max_participants, cost, reg_required, reg_deadline in events:
        c.execute(
            """
            INSERT OR IGNORE INTO event 
            (activity_group_name, date, location_id, max_participants, cost, 
             registration_required, registration_deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (activity_group, date, location_id, max_participants, cost, reg_required, reg_deadline)
        )

def create_test_prerequisites():
    """Create test prerequisites"""
    prerequisites = [
        (2, 1, 80, 30, 1),
        (3, 2, 90, 60, 0)
    ]
    
    for event_id, prereq_id, min_perf, qual_period, waiver in prerequisites:
        c.execute(
            """
            INSERT OR IGNORE INTO prerequisite 
            (event_id, prerequisite_event_id, minimum_performance, 
             qualification_period, is_waiver_allowed)
            VALUES (?, ?, ?, ?, ?)
            """,
            (event_id, prereq_id, min_perf, qual_period, waiver)
        )

def create_test_reviews():
    """Create test reviews"""
    reviews = [
        (1, 'Kpop Dance', 'Great dance class! The instructor was amazing.', 5, '2024-03-15', 1),
        (1, 'Boston Book Club', 'Interesting discussion about the latest book.', 4, '2024-03-14', 1),
        (2, 'Boston Runners', 'Perfect running route and great company!', 5, '2024-03-13', 1),
        (2, 'Boston Chess Masters', 'Challenging games and friendly atmosphere.', 4, '2024-03-12', 1),
        (3, 'Boston Foodies', 'Delicious food and great recommendations.', 5, '2024-03-11', 1),
        (3, 'Boston Coders', 'Very informative coding workshop.', 4, '2024-03-10', 1)
    ]
    
    for resident_id, activity_group_name, content, star_rating, review_date, is_verified in reviews:
        c.execute(
            """
            INSERT OR IGNORE INTO review 
            (resident_id, activity_group_name, content, star_rating, review_date, is_verified)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (resident_id, activity_group_name, content, star_rating, review_date, is_verified)
        )

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Create test users
        create_or_update_user('admin', 'admin@example.com', 'admin123', 'admin')
        create_or_update_user('testuser', 'user@example.com', 'user123', 'user')
        create_or_update_user('testuser2', 'user2@example.com', 'user123', 'user')
        create_or_update_user('testuser3', 'user3@example.com', 'user123', 'user')
        
        # Create test data
        create_test_activity_groups()
        create_test_locations()
        create_test_events()
        create_test_prerequisites()
        create_test_reviews()
        
        # Commit changes
        conn.commit()
        print("Test data created successfully!")
        print("\nTest accounts created:")
        print("Admin - Username: admin, Password: admin123")
        print("User - Username: testuser, Password: user123")
        print("User - Username: testuser2, Password: user123")
        print("User - Username: testuser3, Password: user123")
        
    except Exception as e:
        print(f"Error creating test data: {e}")
        conn.rollback()
    finally:
        conn.close()
