import socket
import time
import pickle
from concurrent.futures import ThreadPoolExecutor
from generare_validare_date import citire

workers = [
    ("localhost", 5001),
    ("localhost", 5002),
    ("localhost", 5003)
]

def recv_all(s):  # un singur recv poate sa nu aduca toate datele, asa ca citim pana cand conexiunea se inchide
    bucati = []
    while True:
        chunk = s.recv(65536)  #citim pana la 64kb odata 
        if not chunk:
            break
        bucati.append(chunk)
    return b"".join(bucati)

def trimite_query(worker, query):  # trimite query la worker si asteapta rezultatul
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(worker)
    s.sendall(pickle.dumps(query))  # serializam query-ul cu pickle pentru a-l putea trimite ca bytes
    s.shutdown(socket.SHUT_WR) 
    rez = pickle.loads(recv_all(s))  # deserializam rezultatul primit de la worker
    s.close()
    return rez

if __name__ == "__main__":
    query = citire()
    start = time.time()

    rezultate = []
    with ThreadPoolExecutor(max_workers=len(workers)) as ex:  # trimitem query-ul catre toti workerii simultan folosind thread-uri
        futures = [ex.submit(trimite_query, w, query) for w in workers]
        for f in futures:
            try:
                rezultate.append(f.result())
            except Exception as e:
                print("Worker indisponibil:", e)

    tip = query[0]
    if tip in ["COUNT", "SUM"]:
        total = sum(rezultate)
    else:
        total = []
        for r in rezultate:
            total.extend(r)

    end = time.time()
    print("Rezultat:", len(total) if isinstance(total, list) else total)
    print("Timp:", round(end - start, 3), "s")