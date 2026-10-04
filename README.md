# Performanta-Algoritmilor-Paraleli-si-Distribuiti
Acest proiect implementeaza un sistem de procesare a interogarilor pe un set de date medicale de dimensiuni mari (1.000.000 de inregistrari). Scopul principal este compararea performantei dintre trei paradigme de programare: secventiala, paralela si distribuita.

Proiectul simuleaza o baza de date medicala reala, cu tabele pentru pacienti, medici, programari, diagnostice si retete. Utilizatorul poate rula interogari de tip COUNT, FILTER, SUM si JOIN, iar sistemul masoara si compara timpii de executie pentru fiecare abordare.
Obiectivele proiectului sunt:
    • Generarea unui volum mare de date medicale sintetice
    • Implementarea interogarii datelor in mod secvential (referinta de performanta)
    • Paralelizarea procesarii folosind multiprocessing si citire directa din fisier prin offset-uri de bytes
    • Implementarea unui sistem distribuit cu workeri independenti care comunica prin socket-uri TCP
    • Compararea si analiza performantei celor trei variante


# Prezentare Proiect
Proiectul este organizat în mai multe fișiere:

- generare_validare_date.py
- queries.py
- secvential.py
- paralel.py
- worker.py
- coordonator.py
- impartire_date.py
- date/*.csv


Fisierul de generare date are doua roluri principale: de a genera date aleatorii cu volum mare pentru programari, pacienti, medici, diagnostice, si retete, si de a realiza interfata pentru utilizator. Aceasta interfata permite utilizatorului să aleagă tipul interogarii, tabelul, campul si valoarea.


<img width="1249" height="468" alt="image" src="https://github.com/user-attachments/assets/7f954189-e011-498a-9d53-41348df7c06e" />


Functia citire() din generare_validare_date.py ghideaza utilizatorul prin urmatorii pasi:
    • Pasul 1 — Tipul interogarii:  COUNT, FILTER, SUM, JOIN
    • Pasul 2 — Tabelul: utilizatorul alege unul din cele 5 tabele disponibile
    • Pasul 3 — Campul: campurile disponibile difera per tabel (ex: programari are doar 'specializare')
    • Pasul 4 — Valoarea: valorile din lista de valori permise (ex: doar specializari existente)

Toate valorile introduse de utilizator sunt validate inainte de procesare. De exemplu, pentru specializare se accepta doar una din cele 19 valori din lista predefinita. Daca utilizatorul introduce o valoare invalida, i se afiseaza lista de optiuni valide si i se cere sa incerce din nou.


Fisierul queries.py contine implementarile pure ale operatiilor de interogare. Aceste functii opereaza pe liste de dictionare (formatul returnat de csv.DictReader) si sunt folosite direct in varianta secventiala.
    • filter(data, field, value) returneaza o lista cu toate randurile unde valoarea campului field este egala cu value. Foloseste list comprehension pentru eficienta.
    • count(data) returneaza numarul de elemente din lista primita ca argument. Se foloseste dupa filter() pentru a numara rezultatele.
    • sum_field(data, field) sumeaza valorile numerice ale unui camp. Foloseste isdigit() pentru a sari peste valori non-numerice, evitand exceptii la conversie.
    • inner(join(data1,data2,key1,key2) uneste doua tabele pe baza cheilor key1 si key2. Construieste mai intai un index (dictionar) din tabelul 2,apoi cauta fiecare rand din tabelul 1 in index.


Fisierul secvential.py abordeaza implementarea clasica. Aceasta citeste tot fisierul CSV in memorie ca o lista de dictionare si executa interogarea liniar pe toata lista. Se citeste input-ul, se incarca datele, se aplica interogarea si la final se afiseaza rezultatul cu timpul de executie.

Fluxul de executie:
    • Pasul 1: in functia citire() utilizatorul alege tipul interogarii, tabelul, campul si valoarea
    • Pasul 2: functia load_data(path) deschide fisierul, foloseste csv.DictReader, intoarce lista de dictionare
    • Pasul 3: aplicarea interogarii folosind functiile din queries.py
    • Pasul 4: afisarea rezultatului si a timpului de executie

Astfel, avem un singur proces, cu un singur fir de executie cu zero overhead de comunicare, si toate datele sunt in acelasi spatiu de memorie.

Fisierul paralel.py foloseste multiprocessing.Pool pentru a crea mai multe procese care citesc si proceseaza simultan bucati diferite din fisierul CSV. Cheia optimizarii este ca fiecare proces deschide fisierul independent si face seek() direct la offsetul sau, astfel datele brute nu trec prin IPC.

O abordare clasica incarca tot fisierul in memorie si apoi trimite bucatile proceselor prin IPC (pickle). Aceasta este mai lenta decat varianta secventiala deoarece:
    • Serializarea a 1.000.000 de dictionare prin pickle costa mai mult decat procesarea lor
    • Datele trec prin pipe-uri IPC, rezultand overhead semnificativ pentru volume mari
    • Pornirea proceselor din Pool adauga un overhead fix de cateva sute de milisecunde

Astfel, in loc sa incarcam datele si sa le trimitem proceselor, calculam doar pozitiile (offset-uri) in bytes ale fiecarei bucati din fisier. Fiecare proces deschide fisierul independent si citeste direct bucata sa:
```py
# Prin IPC trec doar argumentele (cateva bytes):
args = [(path, start_byte, end_byte, tip, camp, valoare) for start, end in offsets]

# Fiecare proces executa:
with open(path, 'rb') as f:
    f.seek(start)                    # salt direct la pozitia noastra
    bucata_bytes = f.read(end-start)  # citim doar bucata noastra

# Prin IPC inapoi trec doar rezultatele (un numar intreg pentru COUNT/SUM)
```
Functia gaseste_offseturi() rezolva problema taierii randurilor la mijloc. Fisierul poate arata in acest fel in bytes:
```py
[byte 0]  id_programare,id_pacient,specializare,data,cost\n   -> header
[byte 52] 1,12453,Cardiologie,2024-03-15,450\n
[byte 89] 2,8821,Pediatrie,2024-07-02,300\n
...
[byte 83.886.080]  -> sfârșitul fișierului
```
Offset-ul ideal poate cadea exact in mijlocul unui rand CSV, ceea ce ar corupe datele:
```py
f.seek(offset_ideal)    # mergem la pozitia calculata matematic
f.readline()            # consumam randul partial (pana la \n)
start = f.tell()        # acum suntem la inceputul unui rand complet
Rezultatul este o lista de tupluri (start_byte, end_byte) unde fiecare pereche garanteaza alinierea la randuri CSV complete.
In functia citeste_bucata(), fiecare din cele N procese executa aceasta functie simultan pe bucata sa:
def citeste_bucata(args):
    path, start, end, tip, camp, valoare = args
    with open(path, 'rb') as f:
        header = f.readline().decode('utf-8').strip().split(',')
        f.seek(start)                          # salt la bucata noastra
        bucata_bytes = f.read(end - start)
    reader = csv.DictReader(io.StringIO(text), fieldnames=header)
    if tip == 'COUNT':
        return sum(1 for rand in reader if rand[camp] == valoare)
```
Pentru JOIN, tabelul 2 (mai mic de obicei) este citit secvential o singura data pentru a construi index-ul. Tabelul 1 este impartit si procesat in paralel, fiecare proces primeste o referinta la index (serializat prin pickle o singura data per proces).

Varianta distribuita simuleaza un sistem distribuit real: coordonatorul si workerii sunt procese complet separate care comunica prin socket-uri TCP. Arhitectura e conceputa sa functioneze si pe masini fizice diferite in retea.
Astfel, pentru implementarea variantei distributive, am creat 3 fisiere: worker, coordonator si cel de impartirea datelor.

Fisierul impartire_date.py, dupa cum sugereaza numele, imparte fiecare CSV in bucati. Astfel, fiecare tabel a fost impartit in trei bucati, ca mai apoi fiecare worker sa lucreze pe cate o bucata din cele trei.
Fiecare fisier partial pastreaza header-ul original, astfel incat csv.DictReader functioneaza corect pe fiecare bucata independent.

Fisierul worker.py reprezinta un nod de calcul distribuit. Mai exact, avem 3 servere, care asculta pe trei porturi diferite si ruleaza in acelasi timp, primesc interogarile, si fiecare proceseaza doar bucata sa de date in mod paralel si trimit rezultatul. Acestia  se pornesc in terminale separate inainte de a rula coordonatorul.

Fisierul coordonator.py reprezinta clientul principal care coordoneaza workerii. El citeste interogarea, trimite query la toti workerii si colecteaza rezultatele.

Comunicarea se face prin TCP cu serializare pickle. Fluxul complet pentru un query:
    1. Handshake TCP
    2. Trimitere query: coordonatorul serialzeaza query-ul cu pickle.dumps() si il trimite cu sendall()
    3. Semnal end-of-message: coordonatorul apeleaza shutdown pentru a semnala ca a terminat de trimis
    4. Receptie worker: workerul citeste in bucle recv(65536) pana primeste semnalul de shutdown
    5. Procesare:  workerul deserializeaza query-ul, proceseaza fisierul sau si returneaza rezultatul
    6. Raspuns:  rezultatul este serializat cu pickle.dumps() si trimis inapoi cu sendall()
    7. Agregare: coordonatorul colecteaza rezultatele de la toti workerii si le combina


Diferenta de performanta este destul de vizibila. Daca avem o interogare COUNT cu 1.000.000 de randuri, varianta secventiala are un timp de aproximativ 1,38s, cea paralela un timp de 0.34s, iar cea distributiva un timp de 0.55s . Varianta paralela este mai rapida deoarece aceasta rulueaza pe mai multe nuclee si nu implica retea, pe cand cea distribuita este, totusi, putin mai lenta, din cauza faptului ca are un overhead de retea, foloseste serializare, plus latenta. Aceasta poate fi insa, avantajoasa, cand avem date extrem de mari, cu mai multe masini si un cluster real.


In concluzie, varianta secventiala ramane optiunea optima pentru volume moderate de date pe o singura masina, datorita simplitatii si absentei totale a overhead-ului.

Varianta paralela este cea mai rapida pe o singura masina datorita citirii directe din fisier cu seek() pe bytes solutia cheie care elimina bottleneck-ul IPC din varianta paralela clasica.

Varianta distribuita este mai lenta pe aceeasi masina din cauza overhead-ului TCP si serializarii pickle, dar reprezinta singura solutie scalabila pentru date care depasesc capacitatea unei singure masini. Ea modeleza arhitectura sistemelor reale de procesare distribuita.


Instructiuni de rulare:
```
python generare_validare_date.py
python secvential.py
python paralel.py
python impartire_date.py
python worker.py 5001 _1
python worker.py 5002 _2
python worker.py 5003 _3
python coordonator.py
```
