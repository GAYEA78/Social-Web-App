DROP TABLE IF EXISTS hosts;
DROP TABLE IF EXISTS member;
DROP TABLE IF EXISTS prerequisite;
DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS session;
DROP TABLE IF EXISTS event;
DROP TABLE IF EXISTS location;
DROP TABLE IF EXISTS activity_group;
DROP TABLE IF EXISTS resident;
DROP TABLE IF EXISTS waitlist;
DROP TABLE IF EXISTS registrations;

-- Table: resident
CREATE TABLE resident (
    resident_id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'admin')),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: activity_group
CREATE TABLE activity_group (
    name TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    founding_date DATE,
    website TEXT,
    email TEXT NOT NULL,
    phone_number TEXT,
    social_media_links TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    total_members INTEGER DEFAULT 0,
    event_frequency TEXT CHECK (event_frequency IN ('weekly', 'biweekly', 'monthly')),
    membership_fee INTEGER DEFAULT 0,
    open_to_public BOOLEAN DEFAULT TRUE,
    min_age INTEGER DEFAULT 18,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: review
CREATE TABLE review (
    review_id SERIAL PRIMARY KEY,
    resident_id INTEGER NOT NULL,
    activity_group_name TEXT NOT NULL,
    content TEXT NOT NULL,
    star_rating INTEGER NOT NULL CHECK (star_rating BETWEEN 1 AND 5),
    review_date DATE NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resident_id) REFERENCES resident(resident_id),
    FOREIGN KEY (activity_group_name) REFERENCES activity_group(name)
);

-- Table: location
CREATE TABLE location (
    id SERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: event
CREATE TABLE event (
    id SERIAL PRIMARY KEY,
    activity_group_name TEXT NOT NULL,
    date DATE NOT NULL,
    location_id INTEGER,
    max_participants INTEGER,
    cost NUMERIC(10,2) NOT NULL DEFAULT 0,
    registration_required BOOLEAN NOT NULL DEFAULT FALSE,
    registration_deadline DATE,
    created_by INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activity_group_name) REFERENCES activity_group(name),
    FOREIGN KEY (location_id) REFERENCES location(id),
    FOREIGN KEY (created_by) REFERENCES resident(resident_id)
);

-- Table: session
CREATE TABLE session (
    id SERIAL PRIMARY KEY,
    activity_group_name TEXT NOT NULL,
    event_id INTEGER NOT NULL,
    date DATE NOT NULL,
    attendance INTEGER,
    agenda TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activity_group_name) REFERENCES activity_group(name),
    FOREIGN KEY (event_id) REFERENCES event(id)
);

-- Table: member (associative)
CREATE TABLE member (
    resident_id INTEGER,
    activity_group_name TEXT,
    join_date DATE,
    role TEXT,
    PRIMARY KEY (resident_id, activity_group_name),
    FOREIGN KEY (resident_id) REFERENCES resident(resident_id),
    FOREIGN KEY (activity_group_name) REFERENCES activity_group(name)
);

-- Table: hosts (associative)
CREATE TABLE hosts (
    activity_group_name TEXT,
    session_id INTEGER,
    PRIMARY KEY (activity_group_name, session_id),
    FOREIGN KEY (activity_group_name) REFERENCES activity_group(name),
    FOREIGN KEY (session_id) REFERENCES session(id)
);

-- Table: prerequisite (associative, self-referencing)
CREATE TABLE prerequisite (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL,
    prerequisite_event_id INTEGER NOT NULL,
    minimum_performance INTEGER NOT NULL,
    qualification_period INTEGER NOT NULL,
    is_waiver_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES event(id),
    FOREIGN KEY (prerequisite_event_id) REFERENCES event(id),
    CHECK (event_id != prerequisite_event_id)
);

-- Table: registrations
CREATE TABLE registrations (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'registered' CHECK (status IN ('registered', 'cancelled', 'completed')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES event(id),
    FOREIGN KEY (user_id) REFERENCES resident(resident_id),
    UNIQUE (event_id, user_id)
);

-- Table: waitlist
CREATE TABLE waitlist (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES event(id),
    FOREIGN KEY (user_id) REFERENCES resident(resident_id),
    UNIQUE (event_id, user_id)
);
