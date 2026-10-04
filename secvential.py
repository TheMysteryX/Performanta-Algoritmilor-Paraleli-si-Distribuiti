import csv
import time
from generare_validare_date import citire
from queries import filter, count, sum_field, inner_join


def load_data(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        return list(reader)


if __name__ == "__main__":

    rezultat = citire()
    start = time.time()

    tip = rezultat[0]

    if tip == "JOIN":

        _, tabel1, path1, tabel2, path2, key1, key2 = rezultat

        data1 = load_data(path1)
        data2 = load_data(path2)

        rezultat_final = inner_join(data1, data2, key1, key2)

        print("Rezultat JOIN:", len(rezultat_final))

    else:
        tip, tabel, path, camp, valoare = rezultat

        data = load_data(path)

        if tip == "COUNT":
            rezultat_final = count(filter(data, camp, valoare))

        elif tip == "FILTER":
            rezultat_final = filter(data, camp, valoare)

        elif tip == "SUM":
            rezultat_final = sum_field(data, camp)

        if isinstance(rezultat_final, list):
            print("Rezultat (numar):", len(rezultat_final))
        else:
            print("Rezultat:", rezultat_final)

    end = time.time()

    print("Timp executie:", end - start)