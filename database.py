import sqlite3


def create_database():

    conn = sqlite3.connect("resume_history.db")

    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        role TEXT,

        score REAL,

        experience INTEGER,

        status TEXT

    )
    """)


    conn.commit()
    conn.close()



def save_candidate(name, role, score, experience, status):

    conn = sqlite3.connect("resume_history.db")

    cursor = conn.cursor()


    cursor.execute("""
    INSERT INTO candidates
    (name, role, score, experience, status)

    VALUES (?, ?, ?, ?, ?)
    """,
    (name, role, score, experience, status))


    conn.commit()
    conn.close()



def get_candidates():

    conn = sqlite3.connect("resume_history.db")

    cursor = conn.cursor()


    cursor.execute(
        "SELECT * FROM candidates"
    )


    data = cursor.fetchall()


    conn.close()


    return data



create_database()