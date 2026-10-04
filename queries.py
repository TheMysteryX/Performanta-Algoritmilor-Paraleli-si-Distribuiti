def filter(data, field, value):
    return [row for row in data if row[field] == value]


def count(data):
    return len(data)


def sum_field(data, field):
    return sum(int(row[field]) for row in data if row[field].isdigit())


def inner_join(data1, data2, key1, key2):

    rez = []

    index = {}

    for row in data2:
        index[row[key2]] = row

    for row in data1:
        if row[key1] in index:
            merged = {**row, **index[row[key1]]}
            rez.append(merged)

    return rez
