import _sqlite3
from sqlite3 import DatabaseError


class Database:

    @staticmethod
    def establish_con(db_name):
        return _sqlite3.connect("VoltCastDB")

    def setup_db(self):
        """
        Called during Backend setup
        :return:
        """
        con = self.establish_con("VoltCastDB")
        cur = con.cursor()
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS user(
                        username TEXT PRIMARY KEY NOT NULL,
                        password TEXT);
                    ''')
        con.commit()
        con.close()

    def write_user_data(self, user) -> bool:
        con = self.establish_con("VoltCastDB")
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
        con = self.establish_con("VoltCastDB")
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