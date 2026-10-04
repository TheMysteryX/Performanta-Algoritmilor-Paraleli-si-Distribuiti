import csv
import io
import os
import time
from multiprocessing import Pool
from generare_validare_date import citire


def gaseste_offseturi(path, nr_procese):  # impartim in segmente de bytes, fara sa taiem randuri la mijloc
    size = os.path.getsize(path)
    offsets = []
    with open(path, 'rb') as f:
        header_end = len(f.readline())  #sarim peste header
        for i in range(nr_procese):
            start = header_end + i * (size - header_end) // nr_procese  # offset-ul ideal pentru inceputul bucatii i, dar poate fi la mijlocul unui rand
            if i == 0:  
                start = header_end  # prima bucata
            else:
                f.seek(start)  # ne ducem la offset-ul ideal
                f.readline()  #avansam pana la sfarsitul randului curent in cazul in care offset-ul ideal se afla la mijlocul randului
                start = f.tell()  #ajungem la inceputul unui rand complet
            if i == nr_procese - 1:  
                end = size  # ultima bucata 
            else:
                end_ideal = header_end + (i + 1) * (size - header_end) // nr_procese  #pt sfarsitul bucatii i
                f.seek(end_ideal)
                f.readline()
                end = f.tell()
            offsets.append((start, end))

    return offsets


def citeste_bucata(args):  # fiecare proces deschide fisierul independent si citeste bucata lui simultan
    path, start, end, tip, camp, valoare = args

    with open(path, 'rb') as f:
        header = f.readline().decode('utf-8').strip().split(',')  #header = nume coloana
        f.seek(start)
        bucata_bytes = f.read(end - start)

    text = bucata_bytes.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text), fieldnames=header)

    if tip == "COUNT":
        return sum(1 for rand in reader if rand[camp] == valoare)

    elif tip == "FILTER":
        return [rand for rand in reader if rand[camp] == valoare]

    elif tip == "SUM":
        return sum(int(rand[camp]) for rand in reader if rand[camp].isdigit())


def citeste_bucata_join(args):
    path1, start, end, header, index, key1 = args

    with open(path1, 'rb') as f:
        f.readline()  # sarim peste header
        f.seek(start)
        bucata_bytes = f.read(end - start)

    text = bucata_bytes.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text), fieldnames=header)

    rezultat = []
    for row in reader:
        if row[key1] in index:
            for match in index[row[key1]]:
                rezultat.append({**row, **match})
    return rezultat


def load_header(path):
    with open(path, newline='') as f:
        return next(csv.reader(f))


def load_data_index(path):  #tabelul 2 intreg
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


if __name__ == "__main__":
    rezultat = citire()
    nr_procese = os.cpu_count()
    start_timp = time.time()

    tip = rezultat[0]

    if tip == "JOIN":
        _, tabel1, path1, tabel2, path2, key1, key2 = rezultat

        # tabelul 2 il citim secvential pentru indexare, iar tabelul 1 il procesam in paralel
        data2 = load_data_index(path2)
        index = {}
        for row in data2:
            index.setdefault(row[key2], []).append(row)

        header1 = load_header(path1)
        offsets = gaseste_offseturi(path1, nr_procese)

        args = [(path1, s, e, header1, index, key1) for s, e in offsets]

        with Pool(nr_procese) as pool:
            rez = pool.map(citeste_bucata_join, args)

        total = []
        for r in rez:
            total.extend(r)

        print("Rezultat JOIN:", len(total))

    else:
        tip, tabel, path, camp, valoare = rezultat

        offsets = gaseste_offseturi(path, nr_procese)
        args = [(path, s, e, tip, camp, valoare) for s, e in offsets]

        with Pool(nr_procese) as pool:
            rez = pool.map(citeste_bucata, args)

        if tip in ["COUNT", "SUM"]:
            total = sum(rez)
        else:
            total = []
            for r in rez:
                total.extend(r)

        print("Rezultat:", len(total) if isinstance(total, list) else total)

    end_timp = time.time()
    print("Timp execuție:", round(end_timp - start_timp, 3), "s")
    