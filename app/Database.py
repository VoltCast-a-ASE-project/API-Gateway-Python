import _sqlite3
import os

from sqlite3 import DatabaseError
from dotenv import load_dotenv


class Database:
    """
    Class holds method that perform queries on the SQLite database.
    """

    @staticmethod
    def establish_con():
        """
        Method establishes connection to database and returns connection object.
        """
        load_dotenv()
        db_name = os.getenv("DB_NAME")
        return _sqlite3.connect(db_name)

    def setup_db(self):
        """
        Called during Backend setup. Creates all necessary tables.
        :return: None
        """
        con = self.establish_con()
        cur = con.cursor()
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS user(
                        username TEXT PRIMARY KEY NOT NULL,
                        password TEXT);
                    ''')
        con.commit()
        con.close()

    def write_user_data(self, user) -> bool:
        """
        Writes user data to database.
        :param user: JSON with user data.
        :return: boolean
        """
        con = self.establish_con()
        cur = con.cursor()

        try:
            cur.execute('''INSERT INTO user (username, password)
                           VALUES (?, ?)''',
                        (user.username, user.hashed_password))
            con.commit()
        except DatabaseError:
            return False
        finally:
            con.close()

        return True


    def get_user_password(self, username: str):
        """
        Method returns user password hash.
        :param username: String username
        :return: Database tuple with user password hash.
        """
        con = self.establish_con()
        cur = con.cursor()
        print(username)

        cur.execute(
            "SELECT password FROM user WHERE username = ?",
            (username,)
        )
        response = cur.fetchall()

        con.commit()
        con.close()

        return response