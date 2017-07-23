from kivy.app import App
from kivy.uix.screenmanager import Screen
from App.lib import Queries
from App.lib import Navigation
from App.lib import MiscFuns
from App.lib import LoadDialog
from kivy.uix.popup import Popup
from kivy.properties import DictProperty
from kivy.properties import ListProperty, ObjectProperty
from shutil import copyfile
import sqlite3

conn = sqlite3.connect("./Assets/db_productivity.sqlite3")
conn.execute('pragma foreign_keys=on')
c = conn.cursor()


class BooksScreen(Screen):

    def on_parent(self, Screen, parent):
        book_list = Queries.get_book_list()
        books = []
        for book in book_list:
            temp = {
                "book_id": book[0],
                "book_title": book[1],
                "primary_genre": str(book[2]) if book[2] else "",
                "read_status": str(book[3]) if book[3] else ""
            }
            books.append(temp)
        self.rv.data = books


class BookScreen(Screen):

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        self.book_id = gd.glob_dict['book_id']
        book_list = Queries.get_book_list()
        book_ids = [''.join(str(book_list[i][0])) for i in range(len(book_list))]
        ind = book_ids.index(self.book_id)

        if ind > 0:
            self.prev = book_ids[ind - 1]
        else:
            self.prev = book_ids[len(book_ids) - 1]
        if ind < len(book_ids) - 1:
            self.next = book_ids[ind + 1]
        else:
            self.next = book_ids[0]
        self.book_list = c.fetchall()

        book_data = Queries.get_book_data(self.book_id)
        publisher = Queries.get_publisher_data_by_id(book_data[3])
        publisher = publisher[0] if publisher else ""
        self.book_title = book_data[1]
        self.isbn = book_data[2] if book_data[2] else ""
        self.publisher = publisher
        self.year_published = str(book_data[4]) if book_data[4] else ""
        self.orig_year_published = str(book_data[5]) if book_data[5] else ""
        self.primary_genre = str.capitalize(book_data[6])
        self.secondary_genre = str.capitalize(book_data[7]) if book_data[7] else ""
        self.cover_front = book_data[8] if book_data[8] else ""
        self.cover_back = book_data[9] if book_data[9] else ""
        self.read_status = str(book_data[10]) if book_data[10] else ""
        self.rating = str(book_data[11]) if book_data[11] else ""
        self.notes = book_data[12] if book_data[12] else ""
        self.btn_notes = "View Notes" if book_data[12] else "No Notes"
        self.textbook = book_data[13]
        self.timestamp = book_data[14]

        book_author = Queries.get_book_author_data(self.book_id)
        self.author_list = ""
        for i in range(len(book_author)):
            first = book_author[i][1] + " "
            middle = book_author[i][2] + " " if book_author[i][2] != " " else ""
            last = book_author[i][3] + ", "
            self.author_list += first + middle + last
        self.author_list = self.author_list[:-2]

        book_user_notes = Queries.get_book_user_notes(self.book_id)

        book_notes = []
        if book_user_notes:
            for note in book_user_notes:
                temp = {
                    "note_id": str(note[0]),
                    "note_title": note[1],
                    "note_excerpt": note[2],
                    "note_full": str(note[3]) if note[3] else "",
                    "btn_full_notes": "Full Notes" if note[3] != " " else "No Notes"
                }
                book_notes.append(temp)
        else:
            temp = {
                "note_id": "",
                "note_title": "Click 'Add Note' below to add notes.",
                "note_excerpt": "",
                "note_full": "",
                "btn_full_notes": "No Notes"
            }
            book_notes.append(temp)
        self.rv_note.data = book_notes

    @staticmethod
    def confirm_book_delete(book_id):
        gd = App.get_running_app()
        gd.glob_dict['delete_book_id'] = book_id
        popup = DeleteBookConfirmationPopup()
        popup.open()

    @staticmethod
    def confirm_book_note_delete(note_id):
        gd = App.get_running_app()
        gd.glob_dict['delete_book_note_id'] = note_id
        popup = DeleteBookNoteConfirmationPopup()
        popup.open()


class NewBookScreen(Screen):

    data = DictProperty({})
    __events__ = ('on_submit',)
    loadfile = ObjectProperty(None)
    text_input = ObjectProperty(None)
    book_author_spinner_list = ListProperty(None)
    book_publisher_spinner_list = ListProperty(None)

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        self.book_author_spinner_list = []
        self.book_publisher_spinner_list = []
        author_list = Queries.get_author_list()
        for i in range(len(author_list)):
            author_id = author_list[i][0]
            first = author_list[i][1] if author_list[i][1] else " "
            middle = author_list[i][2] if author_list[i][2] != " " else " "
            last = author_list[i][3] if author_list[i][3] else " "
            if middle != " ":
                string = str(last) + ", " + str(first) + ", " + str(middle)
            else:
                string = str(last) + ", " + str(first)
            self.book_author_spinner_list.append(string)
        publisher_list = Queries.get_publisher_list()
        for i in range(len(publisher_list)):
            publisher_id = publisher_list[i][0]
            publisher_name = publisher_list[i][1]
            self.book_publisher_spinner_list.append(publisher_name)

        self.r = '0.5'
        if gd.glob_dict['edit']:
            self.book_id = gd.glob_dict['book_id']
            self.book_data = Queries.get_book_data(self.book_id)
            book_author = Queries.get_book_author_data(self.book_id)
            self.author = ""
            for author in book_author:
                self.author += str(author[3]) + ", " + str(author[1])
                self.author += ", {m};".format(str(author[2])) if author[2] != " " else ";"
            self.author = self.author[:-1]
            self.data['book_title'] = self.book_data[1]
            self.data['isbn'] = self.book_data[2] if self.book_data[2] else ""
            publisher = Queries.get_publisher_data_by_id(self.book_data[3])
            publisher = publisher[0] if publisher else ""
            self.data['publisher'] = publisher
            self.data['year_published'] = str(self.book_data[4]) if self.book_data[4] else ""
            self.data['original_year_published'] = str(self.book_data[5]) if self.book_data[5] else ""
            self.data['primary_genre'] = str.capitalize(self.book_data[6])
            self.data['secondary_genre'] = str.capitalize(self.book_data[7]) if self.book_data[7] else ""
            self.data['cover_front'] = self.book_data[8] if self.book_data[8] else ""
            self.data['cover_back'] = self.book_data[9] if self.book_data[9] else ""
            self.data['read_status'] = str(self.book_data[10]) if self.book_data[10] else ""
            self.data['rating'] = str(self.book_data[11]) if self.book_data[11] else ""
            self.data['notes'] = self.book_data[12] if self.book_data[12] else ""
            self.data['textbook'] = True if self.book_data[13] == 1 else False
            self.data['author'] = self.author
            self.new_book_insert_status.text = "Edit"
        else:
            self.new_book_insert_status.text = "Fill in as much as you can. To add notes, view the book after insertion."
            self.data = {}
            self.data['book_title'] = ""
            self.data['isbn'] = ""
            self.data['year_published'] = ""
            self.data['original_year_published'] = ""
            self.data['primary_genre'] = ""
            self.data['secondary_genre'] = ""
            self.data['cover_front'] = ""
            self.data['cover_back'] = ""
            self.data['read_status'] = ""
            self.data['rating'] = ""
            self.data['textbook'] = ""
            self.data['notes'] = ""
        self.data['orig'] = gd.glob_dict['orig']

    def get_spinner_lists(self):
        pass
        # return out_author, out_pub

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load_front(self):
        content = LoadDialog(load=self.load_front, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def load_front(self, path, filename):
        self.front_cover_input.text = filename[0]
        self.dismiss_popup()

    def show_load_back(self):
        content = LoadDialog(load=self.load_back, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def load_back(self, path, filename):
        self.back_cover_input.text = filename[0]
        self.dismiss_popup()

    def on_submit(self, data):
        gd = App.get_running_app()
        # try:
        if gd.glob_dict['edit']:
            book_id = self.book_id
        else:
            book_id = MiscFuns.get_id(16)
        if data['cover_front']:
            cover_front_ext = data['cover_front'].split('.')[-1]
            src = data['cover_front']
            dst = "./Assets/Book_Covers/" + str(data['book_title']).replace(" ", "_") + "_" + str(book_id) + \
                  "_front." + str(cover_front_ext)
            copyfile(src, dst)

        if data['cover_back']:
            cover_back_ext = data['cover_back'].split('.')[-1]
            src = data['cover_back']
            dst = "./Assets/Book_Covers/" + str(data['book_title']).replace(" ", "_") + "_" + str(book_id) + \
                  "_back." + str(cover_back_ext)
            copyfile(src, dst)

        if 'publisher' in data:
            publisher = Queries.get_publisher_data(data['publisher'].split(';')[0])[0] if data['publisher'] else ""
        else:
            publisher = ""
        book_title = data['book_title'] if data['book_title'] else ""
        isbn = data['isbn'] if data['isbn'] else ""
        year_published = data['year_published'] if data['year_published'] else ""
        original_year_published = data['original_year_published'] if data['original_year_published'] else ""
        primary_genre = data['primary_genre'] if data['primary_genre'] else ""
        secondary_genre = data['secondary_genre'] if data['secondary_genre'] else ""
        cover_front = data['cover_front'] if data['cover_front'] else ""
        cover_back = data['cover_back'] if data['cover_back'] else ""
        read_status = data['read_status'] if data['read_status'] else ""
        rating = data['rating'] if data['rating'] else ""
        notes = data['notes'] if data['notes'] else ""
        textbook = 1 if data['textbook'] else 0

        if gd.glob_dict['edit']:
            c.execute("""
                        UPDATE `tbl_books` 
                        SET `book_title` = '{bt}',
                            `isbn` = '{i}',
                            `publisher` = '{p}',
                            `year_published` = '{yp}',
                            `original_year_published` = '{oyp}',
                            `primary_genre` = '{pg}',
                            `secondary_genre` = '{sg}',
                            `cover_front` = '{cf}',
                            `cover_back` = '{cb}',
                            `read_status` = '{rs}',
                            `rating` = '{r}',
                            `notes` = '{n}',
                            `textbook` = '{t}'
                        WHERE `book_id` = '{bid}'
                    """.format(bt=book_title, bid=book_id, i=isbn, p=publisher, yp=year_published,
                               oyp=original_year_published, pg=primary_genre, sg=secondary_genre, cf=cover_front,
                               cb=cover_back, rs=read_status, r=rating, n=notes, t=textbook))
        else:
            c.execute("""
                        INSERT INTO `tbl_books` (`book_id`,`book_title`,`isbn`,`publisher`,`year_published`,
                                    `original_year_published`,`primary_genre`,`secondary_genre`,`cover_front`,
                                    `cover_back`,`read_status`,`rating`,`notes`,`textbook`)
                        VALUES      (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (book_id, book_title, isbn, publisher, year_published, original_year_published,
                          primary_genre, secondary_genre, cover_front, cover_back, read_status, rating, notes,
                          textbook,))
        conn.commit()
        temp = data['author'].split(';')
        for author in temp:
            t_author = author.split(',')
            author_first = t_author[1].replace(" ", "")
            author_middle = t_author[2] if len(t_author) > 2 else " "
            author_last = t_author[0]
            c.execute("""
                        SELECT `author_id`
                        FROM `tbl_book_authors`
                        WHERE `author_first` = '{f}' AND `author_middle` = '{m}' AND `author_last` = '{l}'
                    """.format(f=author_first, m=author_middle, l=author_last))

            author_id = c.fetchone()[0]
            self.data = {}
            try:
                c.execute("""
                            INSERT INTO `tbl_map_author_book`
                            VALUES (?,?)
                        """, (author_id, book_id,))
                self.data = {}
            except:
                pass
            conn.commit()
        self.new_book_insert_status.text = "New book successfully added/updated."
        self.r = '0'
        if gd.glob_dict['edit']:
            gd.glob_dict['edit'] = False
        Navigation.page_nav(dest='book', orig='books', edit=False)
        # except:
        #     self.new_book_insert_status.text = "Insertion Failed! Please check all your inputs."
        #     self.r = '1'


class NewBookNoteScreen(Screen):

    data = DictProperty({})
    __events__ = ('on_submit',)

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        self.data['orig'] = gd.glob_dict['orig']
        if gd.glob_dict['edit']:
            self.note_id = gd.glob_dict['note_id']
            note_data = Queries.get_book_note_data(self.note_id)
            self.data['tbn_note_title'] = note_data[0] if note_data[0] else ""
            self.data['tbn_note_excerpt'] = note_data[1] if note_data[1] else ""
            self.data['tbn_note_full'] = note_data[2] if note_data[2] else ""
        else:
            self.data = {}
            self.data['tbn_note_title'] = ""
            self.data['tbn_note_excerpt'] = ""
            self.data['tbn_note_full'] = ""

    def on_submit(self, data):
        gd = App.get_running_app()
        self.book_id = gd.glob_dict['book_id']
        tbn_note_title = data['tbn_note_title'] if data['tbn_note_title'] else " "
        tbn_note_excerpt = data['tbn_note_excerpt'] if data['tbn_note_excerpt'] else " "
        tbn_note_full = data['tbn_note_full'] if data['tbn_note_full'] else " "
        if not gd.glob_dict['edit']:
            note_id = MiscFuns.get_id(16)

        if gd.glob_dict['edit']:
            c.execute("""
                        UPDATE `tbl_book_notes`
                        SET `tbn_note_title` = '{tnt}',
                            `tbn_note_excerpt` = '{tne}',
                            `tbn_note_full` = '{tnf}'
                        WHERE `note_id` = '{nid}'
                    """.format(tnt=tbn_note_title, tne=tbn_note_excerpt, tnf=tbn_note_full, nid=self.note_id))
        else:
            c.execute("""
                        INSERT INTO `tbl_book_notes` (`note_id`,`tbn_book_id`,`tbn_note_title`,`tbn_note_excerpt`,
                                    `tbn_note_full`)
                        VALUES (?,?,?,?,?)
                    """, (note_id, self.book_id, tbn_note_title, tbn_note_excerpt, tbn_note_full))
        conn.commit()
        Navigation.page_nav(dest='book', orig='books', edit=False)

    @staticmethod
    def confirm_cancel_book_note():
        popup = CancelBookNoteConfirmationPopup()
        popup.open()


class NewAuthorScreen(Screen):
    data = DictProperty({})
    __events__ = ('on_submit',)

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        if gd.glob_dict['edit']:
            self.author_id = gd.glob_dict['author_id']
            author_data = Queries.get_author_data(self.author_id)
            self.data['author_first'] = author_data[0] if author_data[0] else ""
            self.data['author_middle'] = author_data[1] if author_data[1] else ""
            self.data['author_last'] = author_data[2] if author_data[2] else ""
        else:
            self.data = {}
            self.data['author_first'] = ""
            self.data['author_middle'] = ""
            self.data['author_last'] = ""
        self.data['orig'] = gd.glob_dict['orig']

    def on_submit(self, data):
        gd = App.get_running_app()
        author_first = data['author_first'] if data['author_first'] else " "
        author_middle = data['author_middle'] if data['author_middle'] else " "
        author_last = data['author_last'] if data['author_last'] else " "
        if gd.glob_dict['edit']:
            self.author_id = gd.glob_dict['author_id']
            c.execute("""
                        UPDATE `tbl_book_authors`
                        SET `author_first` = '{af}',
                            `author_middle` = '{am}',
                            `author_last` = '{al}'
                        WHERE `author_id` = '{aid}'
                    """.format(af=author_first, am=author_middle, al=author_last, aid=self.author_id))
        else:
            author_id = MiscFuns.get_id(16)
            c.execute("""
                        INSERT INTO `tbl_book_authors` (`author_id`,`author_first`,`author_middle`,`author_last`)
                        VALUES (?,?,?,?)
                    """, (author_id, author_first, author_middle, author_last))
        gd.glob_dict['edit'] = False
        conn.commit()
        Navigation.page_nav(dest=self.data['orig'], orig='books', edit=False)


class NewPublisherScreen(Screen):
    data = DictProperty({})
    __events__ = ('on_submit',)

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        if gd.glob_dict['edit']:
            self.publisher_name = gd.glob_dict['publisher_name']
            publisher_data = Queries.get_publisher_data(self.publisher_name)
            self.data['publisher_name'] = publisher_data[0] if publisher_data[0] else ""
        else:
            self.data = {}
            self.data['publisher_name'] = ""
        self.data['orig'] = gd.glob_dict['orig']

    def on_submit(self, data):
        gd = App.get_running_app()
        new_publisher_name = data['publisher_name'] if data['publisher_name'] else " "
        if gd.glob_dict['edit']:
            self.publisher_name = gd.glob_dict['publisher_name']
            c.execute("""
                        UPDATE `tbl_book_publishers`
                        SET `publisher_name` = '{npn}'
                        WHERE `publisher_name` = '{pn}'
                    """.format(npn=new_publisher_name, pn=self.publisher_name))
        else:
            c.execute("""
                        INSERT INTO `tbl_book_publishers` (`publisher_name`)
                        VALUES (?)
                    """, (new_publisher_name,))
        conn.commit()
        Navigation.page_nav(dest=self.data['orig'], orig='books', edit=False)


class DeleteBookNoteConfirmationPopup(Popup):

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        self.delete_note_id = gd.glob_dict['delete_book_note_id']
        c.execute("""
                    SELECT `tbn_note_title`
                    FROM `tbl_book_notes`
                    WHERE `note_id` = '{nid}'
                    """.format(nid=self.delete_note_id))
        try:
            self.note_title = c.fetchone()[0]
        except:
            self.gd = App.get_running_app()
            self.gd.sm.current = 'book'

    def on_confirm(self):
        gd = App.get_running_app()
        c.execute("""
                    DELETE
                    FROM `tbl_book_notes`
                    WHERE `note_id` = '{nid}'
                    """.format(nid=self.delete_note_id))
        conn.commit()
        self.dismiss()
        Navigation.page_nav(dest='empty')
        Navigation.page_nav(dest='book')

    def on_close(self):
        self.dismiss()


class DeleteBookConfirmationPopup(Popup):

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        self.delete_book_id = gd.glob_dict['delete_book_id']
        c.execute("""
                    SELECT `book_title`
                    FROM `tbl_books`
                    WHERE `book_id` = '{bid}'
                    """.format(bid=self.delete_book_id))
        try:
            self.book_title = c.fetchone()[0]
        except:
            self.gd = App.get_running_app()
            self.gd.sm.current = 'books'

    def on_confirm(self):
        gd = App.get_running_app()
        c.execute("""
                    DELETE
                    FROM `tbl_books`
                    WHERE `book_id` = '{bid}'
                    """.format(bid=self.delete_book_id))
        conn.commit()
        c.execute("""
                    SELECT `book_id`
                    FROM `tbl_books`
                    """)
        self.book_id = c.fetchone()[0]
        self.gd = App.get_running_app()
        self.gd.glob_dict['book_id'] = self.book_id
        gd.glob_dict['edit'] = False
        self.dismiss()

    def on_close(self):
        self.dismiss()


class CancelBookNoteConfirmationPopup(Popup):

    def on_parent(self, widget, parent):
        pass

    def on_confirm(self):
        gd = App.get_running_app()
        gd.sm.current = 'book'
        self.dismiss()

    def on_cancel(self):
        self.dismiss()