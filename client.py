import socket
from pyope.ope import OPE

# Initialisation du client et connexion au serveur
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 1200)
client_socket.connect(server_address)

# Réception du message de bienvenue du serveur
message_arrivé = client_socket.recv(1024).decode()
print(message_arrivé)

# Boucle pour envoyer des requêtes SQL au serveur
while True:
    # Lecture de la requête SQL entrée par l'utilisateur
    sql = input("SQL>")

    # Lecture des paramètres de la requête chiffrés avec OPE
    ohe_params = []
    if '{{OHE}}' in sql:
        for i in range(sql.count('{{OHE}}')):
            while True:
                try:
                    x = int(input(f"ohe arg {i} :"))
                    ohe_params.append(str(x))
                    break
                except:
                    print("[x] OHE Args must be integers !")
                    pass

    ohe_params_str = ';'.join(ohe_params)
    trame = f'{sql}|||{ohe_params_str}'

    client_socket.send(trame.encode())
    db_response = client_socket.recv(1024).decode()
    print(db_response)

client_socket.close()