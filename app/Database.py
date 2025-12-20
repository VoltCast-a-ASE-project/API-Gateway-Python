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

        cur.execute('''
                    CREATE TABLE IF NOT EXISTS microservices(
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        name TEXT NOT NULL,
                        ip_address TEXT,
                        port INTEGER,
                        username TEXT,
                        FOREIGN KEY(username) REFERENCES user(username));
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


        def write_microservice_data(self, microservice):
            con = self.establish_con("VoltCast_DB")
            cur = con.cursor()

            # timestamp = realtime_data["realtime_data"]["current_generation"]["timestamp"]
            # unit = realtime_data["realtime_data"]["current_generation"]["unit"]
            # value = realtime_data["realtime_data"]["current_generation"]["value"]
            #
            # cur.execute('''INSERT INTO current_energy (timestamp, unit, energy)
            #                VALUES (?, ?, ?)''',
            #             (timestamp, unit, value))
            # con.commit()
            #
            # timestamp = realtime_data["realtime_data"]["current_consumption"]["timestamp"]
            # unit = realtime_data["realtime_data"]["current_consumption"]["unit"]
            # value = realtime_data["realtime_data"]["current_consumption"]["value"]
            #
            # cur.execute('''INSERT INTO current_consumption (timestamp, unit, energy)
            #                VALUES (?, ?, ?)''',
            #             (timestamp, unit, value))
            # con.commit()
            #
            # timestamp = realtime_data["realtime_data"]["battery_capacity"]["timestamp"]
            # unit = realtime_data["realtime_data"]["battery_capacity"]["unit"]
            # value = realtime_data["realtime_data"]["battery_capacity"]["value"]
            #
            # cur.execute('''INSERT INTO battery_capacity (timestamp, unit, energy)
            #                VALUES (?, ?, ?)''',
            #             (timestamp, unit, value))
            con.commit()
            con.close()