import csv

def split_csv(input_file, nr_bucati):
    with open(input_file) as f:
        reader = list(csv.reader(f))

    header = reader[0]
    rows = reader[1:]

    chunk_size = len(rows) // nr_bucati

    for i in range(nr_bucati):
        start = i * chunk_size
        end = len(rows) if i == nr_bucati - 1 else (i + 1) * chunk_size

        with open(f"{input_file[:-4]}_{i+1}.csv", "w", newline="") as out:
            writer = csv.writer(out)
            writer.writerow(header)
            writer.writerows(rows[start:end])
            
split_csv("date/programari.csv", 3)
split_csv("date/pacienti.csv", 3)
split_csv("date/medici.csv", 3)
split_csv("date/diagnostice.csv", 3)
split_csv("date/retete.csv", 3)