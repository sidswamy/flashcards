import sqlite3
from pathlib import Path
import csv

DBFILE = str(Path(__file__).parent) + '/flashcards.db'

con:sqlite3.Connection = None
cur:sqlite3.Cursor = None

# -------------------------

def get_deck(deckname:str):
    deck = {}
    with con:
        cur.execute('select * from flashcards where deck = (?)',(deckname,))
        for r in cur:
            deck[r[0]] = {
                'term' : r[2],
                'img_term' : r[3],
                'definition' : r[4],
                'img_definition' : r[5],
                'comfort' : r[6]
            }
    return deck


def deck_to_db(deckname:str,deck:list):
    if deckname == '':
        raise Exception('Deckname is empty.')
    deckname = deckname.replace(' ','_')
    
    for r in deck:
        r.insert(0,deckname)
        if Path(r[2]).is_file():
            with open(r[2],'rb') as f:
                r[2] = f.read()
        else:
            r[2]=None
        if Path(r[4]).is_file():
            with open(r[4],'rb') as f:
                r[4] = f.read()
        else:
            r[4] = None
    
    with con:
        cur.executemany('''
            insert into flashcards 
            (deck,term,img_term,definition,img_definition,comfort)
            values (?,?,?,?,?,2)
        ''',deck)
        print('Deck imported into the database.')


def import_csv(filename:str):
    deck = []
    if not Path(filename).is_file():
        raise FileNotFoundError(f'<{filename}> does not seem to be a valid file.')
    
    with open(filename,'rt',newline='') as f:
        reader = csv.reader(f)
        next(reader)
        try:
            for row in reader:
                deck.append(row)
        except csv.Error:
            print(f'ERROR: While importing deck from csv. Line # {reader.line_num}')
        except Exception as e:
            raise e
    return deck
    

def db_is_new():
    with con:
        cur.execute('''
            create table if not exists flashcards(
                card_id integer primary key not null,
                deck string not null,
                term string not null,
                img_term blob,
                definition string,
                img_definition blob,
                comfort string
            );
        ''')
    cur.execute('select name from sqlite_master where type="table" and name="flashcards";')
    if not cur.fetchone()[0] == 'flashcards':
        raise sqlite3.DatabaseError('Table was not created. Please debug.')
    else:
        print('INFO: New database file and empty table created.')


def connect_db():
    global con
    global cur
    newdb = False

    if not Path(DBFILE).is_file():
        newdb = True
    
    con = sqlite3.connect(DBFILE)
    cur = con.cursor()
    con.row_factory = sqlite3.Row
    
    if newdb:
        db_is_new()


def main():
    connect_db()
    # im_deck = import_csv('test.csv')
    # deck_to_db('python',im_deck)
    # deck_to_db('javascript',im_deck)
    # deck_to_db('abc',im_deck)
    # print(get_deck('abc'))

    con.close()


if __name__ == '__main__':
    main()
