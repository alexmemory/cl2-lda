"""
Usage: python database.py <create|query> (query)
"""
import csv
import re
import sqlite3
import sys


DATABASE = "debate_reactions.db"
REACTIONS_FNAME = "/Users/peter/resources/data/reactions_oct3_4project.csv"


def fetch(query):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(query)
    ret = cur.fetchall()
    conn.close()
    return ret


def create():
    conn = sqlite3.connect(DATABASE)
    with open(REACTIONS_FNAME) as reactions_file:
        reader = csv.reader(reactions_file, delimiter=',', quotechar='"')
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS reactions")
        cursor.execute("CREATE TABLE users (userid int NOT NULL UNIQUE, "
                       "gender text, age text, long_id text, "
                       "income text, race text, religion text, "
                       "state text, "
                       "candidate text, party text"
                       ")")
        cursor.execute("CREATE TABLE reactions (userid int, time text, "
                       "reaction text"
                       ")")
        simple_id_map = {}
        next_id = 0
        for row_num, row in enumerate(reader):
            if row_num == 0:
                continue
            user = row[0]
            if re.search(r'democrat', row[32]):
                party = 'democrat'
            elif re.search(r'republican', row[32]):
                party = 'republican'
            else:
                party = 'independent'
            if not row[18]:
                religion = "no answer"
            else:
                religion = re.findall(r'([\w ]+)( \(.*\))?',
                                      row[18])[0][0].strip()
            if user not in simple_id_map:
                simple_id_map[user] = next_id
                next_id += 1
                cursor.execute('INSERT INTO users VALUES ("%s", "%s", "%s", '
                               '"%s", "%s", "%s", "%s", "%s", "%s", "%s")'
                               % (simple_id_map[user], row[14], row[15], user,
                                  row[16], row[17], religion, row[20],
                                  row[25], party))
            time = re.findall(r'\d+:\d+:\d+', row[2])[0]
            #time = datetime.datetime.strptime(tmp, '%H:%M:%S')
            cursor.execute('INSERT INTO reactions VALUES ("%s", "%s", "%s")'
                           % (simple_id_map[user], time, row[1]))
        conn.commit()
        #reactions.sort(key=lambda x: x[2])
    conn.close()


def main(argv):
    if argv[0] == "create":
        create()
    elif argv[0] == "query":
        for row in fetch(argv[1]):
            print row


if __name__ == "__main__":
    main(sys.argv[1:])
