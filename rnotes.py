#!/usr/bin/env python
import argparse
import sqlite3
import httplib
from lxml import etree
import string
import subprocess
import urllib
# Return the ID# of the currently active book
def get_current_book():
    """Print the ID of the currently active book.

    """
    f = open('book_state.txt', 'r')
    current = f.readline()
    if current == "None":
        # No active book, return None.
        return None
    else:
        return int(current)

# Manually insert a book by entering each field
# one-by-one.
def insert_book_manual():
    """Manually enter a book into the DB.

    """
    print "Add a book. If you don't want to enter data in a particular field, \
            leave it blank and press enter."
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
    print "URL is:"
    url = raw_input()
    print "Genre is:"
    genre = raw_input()
    print "Number of pages is (enter 0 if N/A):"
    try:
        # Was the page number legit?
        pages = raw_input()
        if pages != "":
            pages = int(pages)
    except:
        print "Numeric values only. Try again."
    # Connect to DB
    connection = sqlite3.connect('reading_notes.db')
    cursor = connection.cursor()
    # Insert all the data.
    cursor.execute('''INSERT INTO work(author, isbn, title, publisher, pub_year, genre, pages, url) VALUES(?, ?, ?, ?, ?, ?, ?, ?)''', (author, isbn, name, publisher, pub_date, genre, pages, url))
    connection.commit()
    connection.close()

# Print the title and author of the currently active book
def print_book_info():
    """Print the active book's information.

    """
    book_id = get_current_book()
    if book_id == None:
        print "There is no active book. Please add a book by searching."
    else:
        connection = sqlite3.connect('reading_notes.db')
        cursor = connection.cursor()
        # Get rows with matching book ID
        cursor.execute("SELECT * FROM work WHERE work_id =?", (book_id, ))
        book = cursor.fetchone()
        print "Active book is %s by %s" % (book[3], book[1])

# Change the active book by selecting another book ID
def change_active_book():
    """Select a new book to make active.

    """
    valid_ids = []
    connection = sqlite3.connect('reading_notes.db')
    cursor = connection.cursor()
    # Loop through all works and display on screen.
    for row in cursor.execute('''SELECT * FROM work'''):
        print "Book ID %d is %s by %s" % (row[0], row [3], row[1])
        valid_ids.append(row[0])
    print "Now select an active book by entering its ID:"
    try:
        selection = raw_input()
        file = open('book_state.txt', 'w')
        if selection == "None":
            # Active book to be reset
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
    """Add a quotation from the active book to the DB.

    """
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
    """Add a reading note about the active book to the DB.

    """
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
    """Add both a quotation and a reading note to the active book

    """
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
    """Print all quotations/notes for the active book

    """
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
    """Delete the active book from the DB

    """
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
    """Search for book information via the Goodreads API.

    """
    #NEEDS GOODREADS API KEY. ENTER IN CONFIG.TXT
    f = open('config.txt', 'r')
    api_key = string.split(f.readline(), '=')[1]
    print "API KEY IS %s" % api_key
    search_results = []
    the_query = urllib.urlencode({'key' : api_key, 'q' : query[0]})
    #make http request
    search = httplib.HTTPConnection('www.goodreads.com')
    search.request("GET", "/search.xml?%s" % the_query)
    response = search.getresponse().read()
    print response
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
    """Accept or reject a book search and add the book to the DB.

    """
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

def write_current_to_tex():
    """Write notes/quotations to .pdf via LaTeX

    """
    book = get_current_book()
    if book == None:
        print "You must select an active book [-a] before exporting to TeX."
        return None
    connection = sqlite3.connect('reading_notes.db')
    cursor = connection.cursor()
    # author should be [0], title [1]
    book_details = cursor.execute('''SELECT author, title FROM work WHERE work_id=?''', (book, )).fetchone()
    print "What would you like to name the file?"
    file_name = raw_input()
    f = open('%s.tex' % file_name, 'w')
    f.write("\documentclass{article}\\author{%s}\\title{%s}\date{\\today}\\begin{document}\maketitle\section{Reading Notes}""" % (book_details[0], book_details[1]))
# iterate over notes for this book
    for row in cursor.execute('''SELECT * from note where work_id =?''', (book, )):
        f.write('\subsection{%d}' % row[0])
        if row[1] != "":
            f.write('''
                Quotation: %s
                \\newline''' % row[1])
        if row[2] != "":
            f.write('''
                Note: %s
                \\newline''' % row[2])
        f.write(' On page %d' % row[3])
    f.write('\end{document}')
    f.close()
    return file_name

def compile_and_export_tex(filename):
    """Compile/export a .tex file to .pdf

    """
    file_name = "%s.tex" % filename
    subprocess.call(['pdflatex', file_name])
    return None


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
    if args.exportpdf != None:
        compile_and_export_tex(write_current_to_tex())

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
    parser.add_argument('-x', '--exportpdf', nargs='*', help='Export current book\'s notes as pdf via LaTeX.')
    args = parser.parse_args()
    pass_args(args)


if __name__=='__main__':
    main()
