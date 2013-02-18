#!/usr/bin/env python
import sqlite3

def gen_config():
    try:
        f = open('config.txt', 'r')
    except:
        f = open('config.txt', 'w')
        f.write('api_key=')
        f.close()


def create_db():
    connection = sqlite3.connect('reading_notes.db')
    cursor = connection.cursor()
    cursor.executescript("""
        create table if not exists work(
            work_id integer primary key not null,
            author text,
            isbn text,
            title text,
            publisher text,
            pub_year text,
            genre text,
            pages integer
        );

        create table if not exists note(
            note_id integer primary key not null,
            quotation text,
            comments text,
            page integer,
            work_id text,
            foreign key(work_id) references work(work_id)
        );
        """)
    connection.commit()
    connection.close()

def create_state():
    try:
        f = open('book_state.txt', 'r')
    except:
        f = open('book_state.txt', 'w+')
        f.write('None')
        print "Created file"

def main():
    print "Beginning config...\n"
    gen_config()
    print "Generated config file. Creating DB...\n"
    create_db()
    print "Created database.\n\nCreating state file...\n"
    create_state()
    print "Created state file\n\nDone."

if __name__=='__main__':
    main()
