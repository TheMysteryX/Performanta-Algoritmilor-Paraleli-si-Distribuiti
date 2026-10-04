import csv
import random
from datetime import datetime, timedelta
import queries

nume = [
    "Popescu",
    "Ionescu",
    "Georgescu",
    "Dumitrescu",
    "Stanescu",
    "Marinescu",
    "Vasilescu",
    "Radu",
    "Constantinescu",
    "Munteanu",
    "Tudor",
    "Enescu",
    "Neagu",
    "Grigorescu",
    "Iliescu",
    "Dobre",
    "Florea",
    "Nistor",
    "Mihai",
    "Dinu",
    "Petrescu",
    "Rusu",
    "Voicu",
    "Balan",
    "Sava",
    "Dinca",
    "Moldovan",
    "Dumitru",
    "Stan",
    "Popa",
    "Iancu",
    "Dobreanu",
]

prenume = [
    "Andrei",
    "Maria",
    "Ion",
    "Elena",
    "Vasile",
    "Ioana",
    "Mihai",
    "Ana",
    "Florin",
    "Cristina",
    "Adrian",
    "Gabriela",
    "Dan",
    "Raluca",
    "Bogdan",
    "Alina",
    "Stefan",
    "Simona",
    "Lucian",
    "Diana",
    "Catalin",
    "Oana",
    "Marian",
    "Cosmin",
    "Marius",
    "Alina",
    "Valentin",
    "Andreea",
    "Claudiu",
    "Denisa",
    "Vlad",
    "Anca",
]

specializari = [
    "Cardiologie",
    "Dermatologie",
    "Pediatrie",
    "Neurologie",
    "Ortopedie",
    "Ginecologie",
    "Oftalmologie",
    "Urologie",
    "Endocrinologie",
    "Gastroenterologie",
    "Oncologie",
    "Psihiatrie",
    "Reumatologie",
    "Hematologie",
    "Nefrologie",
    "Pulmonologie",
    "Infectioase",
    "Radiologie",
    "Chirurgie",
]

diagnostice = [
    "Gripa",
    "Anemie",
    "Bronsita",
    "Artrita",
    "Obezitate",
    "Sinuzita",
    "Hepatita",
    "Gastrita",
    "Diabet",
    "Hipertensiune",
    "Eczema",
    "Astm",
    "Migrena",
    "Fractura",
    "Spondiloza",
    "Depresie",
    "Anxietate",
    "Insomnie",
]

medicamente = [
    "Paracetamol",
    "Ibuprofen",
    "Amoxicilina",
    "Metformin",
    "Lisinopril",
    "Atorvastatina",
    "Omeprazol",
    "Simvastatina",
    "Aspirina",
    "Ciprofloxacina",
    "Levotiroxina",
    "Alprazolam",
    "Furosemid",
    "Losartan",
    "Gabapentin",
    "Sertralina",
    "Prednison",
    "Clopidogrel",
    "Tamsulosina",
    "Montelukast",
]
def generare(n=1000000):

    with open("date/programari.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id_programare","id_pacient","specializare","data","cost"])
        start_data = datetime(2024, 1, 1)

        for i in range(1, n+1):
            specializare = random.choice(specializari)
            date = start_data + timedelta(random.randint(0, 365))
            cost = random.randint(100, 1000)

            writer.writerow([
                i,
                random.randint(1, 50000),
                specializare,
                date.strftime("%Y-%m-%d"),
                cost
            ])
            
    with open("date/pacienti.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["id_pacient","nume","prenume","varsta","sex"])
        for i in range(1, 100001):
            numele = random.choice(nume)
            prenumele = random.choice(prenume)
            varsta = random.randint(1, 100)
            sex = random.choice(["M", "F"])
            writer.writerow([i, numele, prenumele, varsta, sex])

    with open("date/medici.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["id_medic","nume","prenume","specializare"])
        for i in range(1, 10001):
            numele = random.choice(nume)
            prenumele = random.choice(prenume)
            specializare = random.choice(specializari)
            writer.writerow([i, numele, prenumele, specializare])

    with open("date/diagnostice.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["id_diagnostic","id_pacient","id_medic","diagnostic"])
        for i in range(1, n+1):
            id_pacient = random.randint(1, 50000)
            id_medic = random.randint(1, 1000)
            diagnostic = random.choice(diagnostice)
            writer.writerow([i, id_pacient, id_medic, diagnostic])
            
    with open("date/retete.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["id_reteta","id_pacient","id_medic","medicamente"])
        for i in range(1, n+1):
            id_pacient = random.randint(1, 50000)
            id_medic = random.randint(1, 1000)
            medicament = random.choice(medicamente)
            writer.writerow([i, id_pacient, id_medic, medicament])

def citire_nume():
    while True:
        nume = input("Introduceti numele: ").strip()
        prenume = input("Introduceti prenumele: ").strip()
        if nume in nume and prenume in prenume:
            return nume, prenume
        print("Nume sau prenume invalid!")
        
def citire_spec():
    while True:
        spec = input("Introduceti specializarea: ").strip()
        if spec in specializari:
            return spec
        print("Specializare invalida!")
        print("Optiuni valide:", ", ".join(specializari))

def citire_diagnostic():
    while True:
        diag = input("Introduceti diagnosticul: ").strip()
        if diag in diagnostice:
            return diag
        print("Diagnostic invalid!")
        print("Optiuni valide:", ", ".join(diagnostice))
        
def citire_medicament():
    while True:
        med = input("Introduceti medicamentul: ").strip()
        if med in medicamente:
            return med
        print("Medicament invalid!")
        print("Optiuni valide:", ", ".join(medicamente))

def alege_tabel():

    tabele = {
        "1": ("programari", "date/programari.csv"),
        "2": ("pacienti", "date/pacienti.csv"),
        "3": ("medici", "date/medici.csv"),
        "4": ("diagnostice", "date/diagnostice.csv"),
        "5": ("retete", "date/retete.csv"),
    }

    while True:
        opt = input(
            "Alege tabel:\n"
            "1. Programari\n"
            "2. Pacienti\n"
            "3. Medici\n"
            "4. Diagnostice\n"
            "5. Retete\n"
        )

        if opt in tabele:
            return tabele[opt]

        print("Optiune invalida!")

def alege_camp(tabel):

    campuri = {
        "programari": ["specializare"],
        "pacienti": ["nume", "prenume", "sex"],
        "medici": ["specializare"],
        "diagnostice": ["diagnostic"],
        "retete": ["medicamente"],
    }
    lista = campuri[tabel]
    print("Campuri:", lista)
    while True:
        camp = input("Camp: ").strip()
        if camp in lista:
            return camp
        print("Camp invalid!")
        
def alege_valoare(camp):
    if camp == "specializare":
        return citire_spec()

    elif camp == "diagnostic":
        return citire_diagnostic()

    elif camp == "medicamente":
        return citire_medicament()

    else:
        return input("Valoare: ")

def alege_interogare():

    optiuni = {
        "1": "COUNT",
        "2": "FILTER",
        "3": "SUM",
        "4": "JOIN"
    }

    while True:
        print("\nTipuri interogari:")
        print("1. COUNT")
        print("2. FILTER")
        print("3. SUM")
        print("4. JOIN")

        opt = input("Alege interogarea: ").strip()

        if opt in optiuni:
            return optiuni[opt]

        print("Optiune invalida!")

def alege_cheie(tabel):

    campuri = {
        "programari": ["id_programare", "id_pacient", "specializare", "data", "cost"],
        "pacienti": ["id_pacient", "nume", "prenume", "varsta", "sex"],
        "medici": ["id_medic", "nume", "prenume", "specializare"],
        "diagnostice": ["id_diagnostic", "id_pacient", "id_medic", "diagnostic"],
        "retete": ["id_reteta", "id_pacient", "id_medic", "medicamente"],
    }

    lista = campuri[tabel]

    print(f"Campuri disponibile pentru {tabel}:")
    print(", ".join(lista))

    while True:
        key = input("Introdu cheia: ").strip()

        if key in lista:
            return key

        print("Cheie invalida!")
        
def citire():

    tip = alege_interogare()

    if tip == "JOIN":
        tabel1, path1 = alege_tabel()
        tabel2, path2 = alege_tabel()

        key1 = alege_cheie(tabel1)
        key2 = alege_cheie(tabel2)

        return tip, tabel1, path1, tabel2, path2, key1, key2

    else:
        tabel, path = alege_tabel()
        camp = alege_camp(tabel)
        valoare = alege_valoare(camp)

        return tip, tabel, path, camp, valoare
 
if __name__ == "__main__":
    generare()