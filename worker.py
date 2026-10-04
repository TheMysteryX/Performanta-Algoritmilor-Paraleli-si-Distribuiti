import socket
import csv
import pickle
import sys

#rulare:
# python worker.py 5001 _1
# python worker.py 5002 _2
# python worker.py 5003 _3

HOST = "localhost"
PORT = int(sys.argv[1])
SUFIX = sys.argv[2]

def load_data_full(path):
    with open(path) as f:
        return list(csv.DictReader(f))

def load_data(path):
    new_path = path.replace(".csv", f"{SUFIX}.csv")

    with open(new_path) as f:
        return list(csv.DictReader(f))
            
def proceseaza_query(query): #la fel ca in varianta secventiala
    tip = query[0]

    if tip == "JOIN":
        _, _, path1, _, path2, key1, key2 = query

        data1 = load_data(path1)
        data2 = load_data_full(path2)

        # index
        index = {}
        for row in data2:
            index.setdefault(row[key2], []).append(row)

        rezultat = []
        for row in data1:
            if row[key1] in index:
                for match in index[row[key1]]:
                    rezultat.append({**row, **match})

        return rezultat

    else:
        _, _, path, camp, valoare = query

        data = load_data(path)

        if tip == "COUNT":
            return sum(1 for r in data if r[camp] == valoare)

        elif tip == "FILTER":
            return [r for r in data if r[camp] == valoare]

        elif tip == "SUM":
            return sum(int(r[camp]) for r in data if r[camp].isdigit())

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #TCP
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # permitem refolosirea portului imediat după restart
    server.bind((HOST, PORT))
    server.listen()
    print(f"Worker pe port {PORT} cu sufix {SUFIX} ruleaza...")
    while True:
        conn, _ = server.accept()
        bucati = []
        while True:
            chunk = conn.recv(65536)
            if not chunk:
                break
            bucati.append(chunk)
        query = pickle.loads(b"".join(bucati))
        rez = proceseaza_query(query)
        conn.sendall(pickle.dumps(rez))
        conn.close()
        

if __name__ == "__main__":
    start_server()