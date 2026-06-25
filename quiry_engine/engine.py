# sql string

import json
import os
import readline

# tables = {
#     "users": [
#         {"id": 1, "name": "Souma", "city": "Kolkata"},
#         {"id": 2, "name": "Ritam", "city": "Mumbai"},
#         {"id": 3, "name": "user3", "city": "Kolkata"},
#         {"id": 4, "name": "user4", "city": "Delhi"},
#     ]
# }
WAL_FILE = "wal.json"
def load_wal(entry:dict):
    with open(WAL_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
        print(f"[WAL] Written to {os.path.abspath(WAL_FILE)}")


DATA_FILE = "file.json"


def load_table():
    if not os.path.exists(DATA_FILE):
        return {}
    else:
        with open(DATA_FILE, "r") as f:
            return json.load(f)


def clear_wal():
    with open(WAL_FILE, "w") as f:
        f.write("")


def replay_wal():
    if not os.path.exists(WAL_FILE):
        return

    with open(WAL_FILE, "r") as f:
        lines = f.readlines()

    if not lines:
        return

    print(f"Replaying WAL with {len(lines)} entries...")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        entry = json.loads(line)

        if entry["type"] == "INSERT":
            table = entry["table"]
            row = entry["row"]
            if table not in tables:
                tables[table] = []
            tables[table].append(row)
    save_table(tables)
    clear_wal()  # clear the WAL after replaying
    print("WAL replay completed.")


def save_table(tables):
    with open(DATA_FILE, "w") as f:
        json.dump(tables, f, indent=2)


def build_index():
    for table_name, rows in tables.items():
        indexes[table_name] = {}
        for i, row in enumerate(rows):
            for col, val in row.items():
                if col not in indexes[table_name]:
                    indexes[table_name][col] = {}
                val_key = str(val)
                if val_key not in indexes[table_name][col]:
                    indexes[table_name][col][val_key] = []
                indexes[table_name][col][val_key].append(i)


def update_index(table_name, row_idx, row):
    if table_name not in indexes:
        indexes[table_name] = {}
    for col,val in row.items():
        if col not in indexes[table_name]:
            indexes[table_name][col] = {}
        val_key = str(val)
        if val_key not in indexes[table_name][col]:
            indexes[table_name][col][val_key] = []
        indexes[table_name][col][val_key].append(row_idx)

tables = load_table()
indexes = {}
build_index()  # build indexes on startup to speed up queries
replay_wal()



def execute(query):
    # parse query manually for now
    # "SELECT * FROM table WHERE city = 'Kolkata'"
    token = query.strip().split()
    # ['SELECT', '*', 'FROM', 'table', 'WHERE', 'city', '=', "'Kolkata'"]


    keywords = ["SELECT", "FROM", "WHERE"]
    token = [t.upper() if t.upper() in keywords else t for t in token]
    # finding columns
    select_idx = token.index("SELECT")
    from_idx = token.index("FROM")
    columns = token[select_idx + 1 : from_idx]  # ['*']
    columns = [col.strip(",") for col in columns]  # ['*']

    # find table
    table_name = token[from_idx + 1]  # 'table'

    if table_name not in tables:
        raise Exception(f"Table '{table_name}' does not exist.")
    # data = tables.get(table_name, [])

    # find where clause
    where_col = None
    where_val = None
    if "WHERE" in token:
        where_idx = token.index("WHERE")
        where_col = token[where_idx + 1]
        where_val = token[where_idx + 3].strip("'")  # 'Kolkata'


    if where_col:
        if (table_name in indexes and
            where_col in indexes[table_name] and
            where_val in indexes[table_name][where_col]):
            row_indices = indexes[table_name][where_col][str(where_val)]
            data = [tables[table_name][i] for i in row_indices]
        else:
            data = tables[table_name]  # fallback to full table scan if index not found
    else:
        data = tables[table_name]  # no where clause, use full table



    # execute query
    results = []
    for row in data:
        # if where_col:
        #     if str(row.get(where_col)) != where_val:
        #         continue

        if columns == ["*"]:
            results.append(row)
        else:
            results.append({col: row.get(col) for col in columns})

    return results


def insert(query):
    tokens = query.strip().split()
    keywords = ["INSERT", "INTO", "VALUES"]
    tokens = [t.upper() if t.upper() in keywords else t for t in tokens]

    into_idx = tokens.index("INTO")
    values_idx = tokens.index("VALUES")

    table_name = tokens[into_idx + 1] # table name after INTO
    if table_name not in tables:
        tables[table_name] = []  # create table if not exists

    # extract columns and values
    columns_str = " ".join(tokens[into_idx + 2 : values_idx]) # " (id, name, city) "
    columns_str = columns_str.strip("() ")
    columns = [c.strip() for c in columns_str.split(",")] # ['id', 'name', 'city']

    # extract values
    values_str = " ".join(tokens[values_idx + 1 :]) # " (1, 'Souma', 'Kolkata') "
    values_str = values_str.strip("() ")
    # raw_values = [v.strip().strip("'") for v in values_str.split(",")] # ['1', 'Souma', 'Kolkata']

    # convert types
    raw_values = [v.strip() for v in values_str.split(",")]
    values = []
    for v in raw_values:
        if v.startswith("'") and v.endswith("'"):
            values.append(v.strip("'"))
        elif v.isdigit():
            values.append(int(v))
        else:
            values.append(v)

    if len(columns) != len(values):
        raise Exception("Number of columns and values do not match.")

    row = dict(zip(columns, values)) # {'id': 1, 'name': 'Souma', 'city': 'Kolkata'}

    load_wal({"type": "INSERT", "table": table_name, "row": row}) # log the insert operation to the WAL
    if table_name not in tables:
        tables[table_name] = []
    tables[table_name].append(row)
    row_idx = len(tables[table_name]) - 1
    update_index(table_name, row_idx, row) # update the index for the new row
    save_table(tables)

    # import time

    # time.sleep(5)
    clear_wal() # clear the WAL after successful commit

    return {"status": "success", "message": f"1 row inserted into '{table_name}'."}


# print(execute("SELECT * FROM users WHERE city = 'Kolkata'"))
# print(execute("SELECT name FROM users WHERE city = 'Mumbai'"))
# print(execute("SELECT id, city FROM users"))
# # print(execute("SELECT * FROM nonexistent"))


if __name__ == "__main__":
    print("Query Engine is running... - Type 'exit' to quit")

    while True:
        query = input("SQL> ")
        if query.lower() == "exit":
            break
        try:
            if query.strip().upper().startswith("SELECT"):
                results = execute(query)
                print(json.dumps(results, indent=2))
            elif query.strip().upper().startswith("INSERT"):
                result = insert(query)
                print(json.dumps(result, indent=2))
            else:
                print("Only SELECT and INSERT queries are supported.")
        except Exception as e:
            print(f"Error: {e}")


# #indexes = {
#     "users": {
#         "city": {
#             "Kolkata": [0, 2],  # row positions in tables["users"]
#             "Mumbai":  [1],
#             "Delhi":   [3]
#         }
#     }
# }
