import socket
import sqlite3 as sl
from pyope.ope import OPE


class SqliteConnector:
    def __init__(self, name):
        self.ohe_key = OPE.generate_key()
        self.ohe = OPE(self.ohe_key)
        self.con = sl.connect(name)
        self.drop_table()
        self.create_table()

    def query_encrypt(self, query: str, ohe_params: list):
        new_query = query
        for i, ohe_param in enumerate(ohe_params):
            if i == 0 and ohe_param == '':
                pass
            else:
                print("Replace {{OHE}} with", ohe_param)
                new_query = self.nth_replace(new_query, '{{OHE}}', f"{self.ohe.encrypt(int(ohe_param))}", i + 1)
        print("[ DEBUG ] Query :", new_query)
        return new_query

    def query_decrypt(self, query_result):
        decrypted_result = []
        if len(query_result) > 0:
            for id, nom, montant in query_result:
                print("Found :", id, nom, montant)
                decrypted_result.append((id, nom, self.ohe.decrypt(int(montant))))
            return decrypted_result
        else:
            return query_result

    def nth_replace(self, string, old, new, n=1, option='only nth'):
        """
        Cette fonction remplace les occurrences de la chaîne "ancienne" par la chaîne "nouvelle".
        Il existe trois types de remplacement de la chaîne 'old' :
        1) "only nth" remplace uniquement la nième occurrence (par défaut).
        2) "all left" remplace la nième occurrence et toutes les occurrences à gauche.
        3) 'all right' remplace la nième occurrence et toutes les occurrences à droite.
        """
        if option == 'only nth':
            left_join = old
            right_join = old
        elif option == 'all left':
            left_join = new
            right_join = old
        elif option == 'all right':
            left_join = old
            right_join = new
        else:
            print("Invalid option. Please choose from: 'only nth' (default), 'all left' or 'all right'")
            return None
        groups = string.split(old)
        nth_split = [left_join.join(groups[:n]), right_join.join(groups[n:])]
        return new.join(nth_split)

    def drop_table(self):
        try:
            with self.con:
                self.con.execute("""
                    drop table salaire;
                """)
                print("  -> Existing table salaire droped from database")
        except Exception as err:
            print(err)
            pass

    def create_table(self):
        try:
            with self.con:
                self.con.execute("""
                    create table salaire
                    (
                        id      INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        nom     text not null,
                        montant text not null
                    );
                """)
                print("  -> New Table salaire create in database")
        except Exception as err:
            print(err)
            pass

    def query(self, sql_query: str, ohe_parameters: list):
        with self.con:
            r = self.con.execute(self.query_encrypt(sql_query, ohe_parameters), [])
            return self.query_decrypt(r.fetchall())


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 1200)
server_socket.bind(server_address)
server_socket.listen(1)

print('[-] Database initialization:')

con = SqliteConnector('secure.db')

client_socket, client_address = server_socket.accept()

print('[-] Server waiting for connection...')
print(f'[!] Connection established')