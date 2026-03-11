import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


def get_db_connection():
    """Create a database connection"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


def create_table():
    """Create the assessment table if it doesn't exist"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            create_table_query = """
                                 CREATE TABLE IF NOT EXISTS personality_assessments \
                                 ( \
                                     id \
                                     SERIAL \
                                     PRIMARY \
                                     KEY, \
                                     job_role \
                                     VARCHAR \
                                 ( \
                                     255 \
                                 ) NOT NULL,
                                     company VARCHAR \
                                 ( \
                                     255 \
                                 ) NOT NULL,
                                     experience INTEGER NOT NULL,
                                     age INTEGER NOT NULL,
                                     ext1 INTEGER, ext2 INTEGER, ext3 INTEGER, ext4 INTEGER, ext5 INTEGER,
                                     ext6 INTEGER, ext7 INTEGER, ext8 INTEGER, ext9 INTEGER, ext10 INTEGER,
                                     est1 INTEGER, est2 INTEGER, est3 INTEGER, est4 INTEGER, est5 INTEGER,
                                     est6 INTEGER, est7 INTEGER, est8 INTEGER, est9 INTEGER, est10 INTEGER,
                                     agr1 INTEGER, agr2 INTEGER, agr3 INTEGER, agr4 INTEGER, agr5 INTEGER,
                                     agr6 INTEGER, agr7 INTEGER, agr8 INTEGER, agr9 INTEGER, agr10 INTEGER,
                                     csn1 INTEGER, csn2 INTEGER, csn3 INTEGER, csn4 INTEGER, csn5 INTEGER,
                                     csn6 INTEGER, csn7 INTEGER, csn8 INTEGER, csn9 INTEGER, csn10 INTEGER,
                                     opn1 INTEGER, opn2 INTEGER, opn3 INTEGER, opn4 INTEGER, opn5 INTEGER,
                                     opn6 INTEGER, opn7 INTEGER, opn8 INTEGER, opn9 INTEGER, opn10 INTEGER,
                                     submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                     ) \
                                 """
            cursor.execute(create_table_query)
            conn.commit()
            print("Table created successfully!")
        except Exception as e:
            print(f"Error creating table: {e}")
        finally:
            cursor.close()
            conn.close()


def save_assessment(data):
    """Save assessment data to database"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Extract answers from all_scores
            answers = data['Answers']

            insert_query = """
                           INSERT INTO personality_assessments
                           (job_role, company, experience, age,
                            ext1, ext2, ext3, ext4, ext5, ext6, ext7, ext8, ext9, ext10,
                            est1, est2, est3, est4, est5, est6, est7, est8, est9, est10,
                            agr1, agr2, agr3, agr4, agr5, agr6, agr7, agr8, agr9, agr10,
                            csn1, csn2, csn3, csn4, csn5, csn6, csn7, csn8, csn9, csn10,
                            opn1, opn2, opn3, opn4, opn5, opn6, opn7, opn8, opn9, opn10)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                   %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                   %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                   %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                   %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                           """

            values = (
                data['Demographics']['Job Role'],
                data['Demographics']['Company'],
                data['Demographics']['Experience'],
                data['Demographics']['Age'],
                # EXT
                answers.get('question_0'), answers.get('question_1'), answers.get('question_2'),
                answers.get('question_3'), answers.get('question_4'), answers.get('question_5'),
                answers.get('question_6'), answers.get('question_7'), answers.get('question_8'),
                answers.get('question_9'),
                # EST
                answers.get('question_10'), answers.get('question_11'), answers.get('question_12'),
                answers.get('question_13'), answers.get('question_14'), answers.get('question_15'),
                answers.get('question_16'), answers.get('question_17'), answers.get('question_18'),
                answers.get('question_19'),
                # AGR
                answers.get('question_20'), answers.get('question_21'), answers.get('question_22'),
                answers.get('question_23'), answers.get('question_24'), answers.get('question_25'),
                answers.get('question_26'), answers.get('question_27'), answers.get('question_28'),
                answers.get('question_29'),
                # CSN
                answers.get('question_30'), answers.get('question_31'), answers.get('question_32'),
                answers.get('question_33'), answers.get('question_34'), answers.get('question_35'),
                answers.get('question_36'), answers.get('question_37'), answers.get('question_38'),
                answers.get('question_39'),
                # OPN
                answers.get('question_40'), answers.get('question_41'), answers.get('question_42'),
                answers.get('question_43'), answers.get('question_44'), answers.get('question_45'),
                answers.get('question_46'), answers.get('question_47'), answers.get('question_48'),
                answers.get('question_49')
            )

            cursor.execute(insert_query, values)
            conn.commit()
            print("Assessment saved successfully!")
            return True
        except Exception as e:
            print(f"Error saving assessment: {e}")
            return False
        finally:
            cursor.close()
            conn.close()


def get_all_assessments():
    """Get all assessments from database"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM personality_assessments ORDER BY submitted_at DESC")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return results
        except Exception as e:
            print(f"Error fetching assessments: {e}")
            return []
        finally:
            cursor.close()
            conn.close()