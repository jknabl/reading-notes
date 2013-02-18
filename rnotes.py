#!/usr/bin/env python
import argparse
import sqlite3
import httplib
from lxml import etree
import string

def get_current_book():
    f = open('book_state.txt', 'r')
    current = f.readline()
    if current == "None":
        return None
    else:
        return int(current)

def insert_book_manual():
    print "Add a book. If you don't want to enter data in a particular field, leave it blank and press enter."
    print "Name of the book is:"
    name = raw_input()
    print "Author is:"
    author = raw_input()
    print "ISBN is:"
    isbn = raw_input()
    print "Publisher is:"
    publisher = raw_input()
    print "Publication date is:"
    pub_date = raw_input()
    print "Genre is:"
    genre = raw_input()
    print "Number of pages is:"
    try:
        pages = int(raw_input())
    except:
        print "Numeric values only. Try again."
    connection = sqlite3.connect('reading_notes.db')
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO work(author, isbn, title, publisher, pub_year, genre, pages) VALUES(?, ?, ?, ?, ?, ?, ?)''', (author, isbn, name, publisher, pub_date, genre, pages))
    connection.commit()
    connection.close()


def print_book_info():
    book_id = get_current_book()
    if book_id == None:
        print "There is no active book. Please add a book by searching."
    else:
        connection = sqlite3.connect('reading_notes.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM work WHERE work_id =?", (book_id, ))
        book = cursor.fetchone()
        print "Active book is %s by %s" % (book[3], book[1])

def change_active_book():
    valid_ids = []
    connection = sqlite3.connect('reading_notes.db')
    cursor = connection.cursor()
    for row in cursor.execute('''SELECT * FROM work'''):
        print "Book ID %d is %s by %s" % (row[0], row [3], row[1])
        valid_ids.append(row[0])
    print "Now select an active book by entering its ID:"
    try:
        selection = raw_input()
        file = open('book_state.txt', 'w')
        if selection == "None":
            file.write(selection)
            print "Active book cleared."
        elif int(selection) in valid_ids:
            file.write(selection)
            print "Active book changed to %s" % selection
        else:
            print "You entered an invalid ID. Try again."
        file.close()
    except:
        print "You entered an invalid ID. Try again."

def search_book():
    print "Search for a book."

def add_quotation(quotation):
    print "Add a quotation."
    print quotation[0]
    work_id = get_current_book()
    if work_id == None:
        print "You must select an active book [-a] before adding a quotation."
        return None
    try:
        page_num = int(quotation[1])
    except:
        print "Invalid page number. Integers only."
    connection = sqlite3.connect('reading_notes.db')
    cursor = connection.cursor()
    try:
        cursor.execute('''INSERT INTO note(quotation, page, work_id) values(?, ?, ?)''', (quotation[0], page_num, work_id))
        connection.commit()
        connection.close()
        print "Successfully added quotation."
    except:
        print "Error. Try again."


def add_note(note):
    print "Add a note."
    work_id = get_current_book()
    if work_id == None:
        print "You must select an active book [-a] before adding a reading note."
        return None
    try:
        page_num = int(note[1])
    except:
        print "Invalid page number. IDs are integers."
    connection = sqlite3.connect('reading_notes.db')
    cursor = connection.cursor()
    try:
        cursor.execute('''INSERT INTO note(comments, page, work_id) values (?, ?, ?)''', (note[0], page_num, work_id))
        connection.commit()
        connection.close()
        print "Successfully added reading note."
    except:
        print "Error. Try again."

def add_quotation_with_note(args):
    print "Add a quotation with a note."
    work_id = get_current_book()
    if work_id == None:
        print "You must select an active book [-a] before adding a quotation with a note."
        return None
    try:
        page_num = int(args[2])
    except:
        print "Invalid page number. IDs are integers."
    connection = sqlite3.connect('reading_notes.db')
    cursor = connection.cursor()
    try:
        cursor.execute('''INSERT INTO note(quotation, comments, page, work_id) values (?, ?, ?, ?)''', (args[0], args[1], page_num, work_id))
        connection.commit()
        connection.close()
        print "Successfully added quotation with reading note."
    except:
        print "Error. Try again."

def print_quotations_notes():
    print "Print all quotations and notes about active book."
    work_id = get_current_book()
    if work_id == None:
        print "You must select an active book [-a] before viewing quotations and notes."
        return None
    connection = sqlite3.connect('reading_notes.db')
    cursor = connection.cursor()
    for row in cursor.execute('''SELECT * from note where work_id = ?''', (work_id,)):
        print "--- %d ---\n" % row[0]
        if row[1] != None:
            print "Quotation: %s\n" % row[1]
        if row[2] != None:
            print "Note: %s\n" % row[2]
        print "On page %d\n\n" % row[3]

def delete_record(args):
    work_id = get_current_book()
    record_ids = []
    if work_id == None:
        print "You must select an active book [-a] before deleting a record."
        return None
    try:
        record_id = int(args[0])
    except:
        print "Invalid quotation/note ID. Must be an integer."
        return None
    connection = sqlite3.connect('reading_notes.db')
    cursor = connection.cursor()
    for row in cursor.execute('''SELECT note_id FROM note WHERE work_id =?''', (work_id, )):
        record_ids.append(row[0])
    if record_id in record_ids:
        cursor.execute('''DELETE FROM note WHERE note_id=?''', (record_id, ))
        connection.commit()
        connection.close()
        print "Successfully deleted record #%d" % record_id
    else:
        print "Couldn't find that record. Try again."

#search goodreads API for a query. If a relevant query is found, return
#relevant book info as an array.
def search_book(query):
    #NEEDS GOODREADS API KEY. ENTER IN CONFIG.TXT
    f = open('config.txt', 'r')
    api_key = string.split(f.readline(), '=')[1]
    print "API KEY IS %s" % api_key
    search_results = []
    #make http request
    search = httplib.HTTPConnection('www.goodreads.com')
    search.request("GET", "/search.xml?key=%s&q=%s" % (api_key, query[0]))
    response = search.getresponse().read()
    #now parse
    tree = etree.fromstring(response)
    titles = tree.findall('.//title')
    authors = tree.findall('.//name')
    print titles
    print authors
    for i in range(0, len(titles)-1):
        search_results.append(('%s' % titles[i].text, '%s' % authors[i].text))
    return search_results

def choose_search_book(results):
    count = 0
    while count < len(results):
        print "Found a book called \"%s\" by %s. Choose this book? (Y/N). Press Q to stop." % (results[count][0], results[count][1])
        valid = False
        while valid == False:
            choice = raw_input()
            if choice == "Y" or choice == "y":
                #ADD THE BOOK
                connection = sqlite3.connect('reading_notes.db')
                cursor = connection.cursor()
                cursor.execute('''INSERT INTO work (author, title) values(?, ?)''', (results[count][0], results[count][1]))
                cursor.execute('''SELECT work_id FROM work WHERE author=? AND title=?''', (results[count][0], results[count][1]))
                book_id = cursor.fetchone()
                print "BOOK ID IS %s" % book_id
                connection.commit()
                connection.close()
                #change active book to the new one we added
                f = open('book_state.txt', 'w')
                f.write('%s' % book_id)
                f.close()
                return None
            elif choice == "N" or choice == "n":
                #DON'T ADD THE BOOK
                valid = True
                count += 1
            elif choice == "Q" or choice == "q":
                return None
            else:
                print "Invalid option. Choose Y/N."

def search_book_option(args):
    choose_search_book(search_book(args))
def pass_args(args):
    if args.printquotationsnotes != None:
        print_quotations_notes()
    if args.insert != None:
        insert_book_manual()
    if args.bookinfo != None:
        print_book_info()
    if args.active != None:
        change_active_book()
    if args.search != None:
        search_book_option(args.search)
    if args.quotation != None:
        add_quotation(args.quotation)
    if args.note != None:
        add_note(args.note)
    if args.quotationnote != None:
        add_quotation_with_note(args.quotationnote)
    if args.delete != None:
        delete_record(args.delete)

def main():
    parser = argparse.ArgumentParser(description='Manage reading notes from the CL.')
    parser.add_argument('-q', '--quotation', nargs=2, help='Enter [\'quotation\'] [page #]')
    parser.add_argument('-b', '--bookinfo', nargs='*', help='Prints info about the currently active book.')
    parser.add_argument('-s', '--search', nargs=1, help='Search for book info. Enter the book title or author.')
    parser.add_argument('-n', '--note', nargs=2, help='Enter a reading note.')
    parser.add_argument('-i', '--insert', nargs='*', help='Insert a book manually rather than searching.')
    parser.add_argument('-a', '--active', nargs='*', help='Change the active book. Enter None for no active book.')
    parser.add_argument('-qn', '--quotationnote', nargs=3, help="[\'quotation\'] [\'note\'] [page #]")
    parser.add_argument('-p', '--printquotationsnotes', nargs='*', help="Print all quotations and notes for active book.")
    parser.add_argument('-d', '--delete', nargs=1, help="Delete quotation/note with given ID number. To see all quotations/notes with IDs for active book, use [-p]")
    args = parser.parse_args()
    pass_args(args)


if __name__=='__main__':
    main()
