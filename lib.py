from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
import string, random, sqlite3

conn = sqlite3.connect("./Assets/db_productivity.sqlite3")
conn.execute('pragma foreign_keys=on')
c = conn.cursor()

class Queries:

    @staticmethod
    def remove_fc_from_deck(fc_id):
        gd = App.get_running_app()
        c.execute("""
                    DELETE
                    FROM    `tbl_learning_map_fc_fc_decks`
                    WHERE   `fc_id` = '{fcid}'
                        AND `fc_deck_id` = '{fdid}'
                """.format(fcid=fc_id, fdid=gd.glob_dict['fc_deck_id']))
        Navigation.page_nav(dest='empty')
        Navigation.page_nav(dest='flash_card_deck', orig='flash_card_deck')

    @staticmethod
    def get_fc_deck_data(fc_deck_id):
        c.execute("""
                    SELECT  `fc_deck_name`,`fc_deck_excerpt`
                    FROM    `tbl_learning_flash_cards_decks`
                    WHERE   `fc_deck_id` = '{fdid}'
                """.format(fdid=fc_deck_id))
        fc_deck_data = c.fetchone()
        return fc_deck_data

    @staticmethod
    def get_fc_deck_list(**kwargs):
        if 'fc_id' in kwargs:
            c.execute("""
                        SELECT  `tbl_learning_flash_cards_decks`.`fc_deck_id`,
                                `tbl_learning_flash_cards_decks`.`fc_deck_name`
                        FROM    `tbl_learning_flash_cards_decks`,`tbl_learning_map_fc_fc_decks`
                        WHERE   `tbl_learning_flash_cards_decks`.`fc_deck_id` = `tbl_learning_map_fc_fc_decks`.`fc_deck_id`
                            AND `tbl_learning_map_fc_fc_decks`.`fc_id` = '{fcid}'
                    """.format(fcid=kwargs['fc_id']))
        else:
            c.execute("""
                        SELECT  `fc_deck_id`,`fc_deck_name`,`fc_deck_excerpt`
                        FROM    `tbl_learning_flash_cards_decks`
                    """)
        fc_deck_list = c.fetchall()
        return fc_deck_list

    @staticmethod
    def get_fc_decks_from_fc(fc_id):
        c.execute("""
                    SELECT  `tbl_learning_flash_cards_decks`.`fc_deck_name`
                    FROM    `tbl_learning_flash_cards_decks`, `tbl_learning_map_fc_fc_decks`
                    WHERE   `tbl_learning_map_fc_fc_decks`.`fc_id` = '{fcid}'
                        AND `tbl_learning_flash_cards_decks`.`fc_deck_id` = `tbl_learning_map_fc_fc_decks`.`fc_deck_id`
                    ORDER BY `tbl_learning_flash_cards_decks`.`fc_deck_name`
                """.format(fcid=fc_id))
        fc_tags = c.fetchall()
        return fc_tags

    @staticmethod
    def get_fc_list(**kwargs):
        data = kwargs['data'] if 'data' in kwargs else False
        study = kwargs['study'] if 'study' in kwargs else False
        """
        kwargs:
            data (bool): True pulls all card data, default False
            deck_id (int): Pulls data from a specific deck with id 'fc_deck_id'
            study (book): True pulls only those with it's next study date equal to today, default False
            order_by (str): Order by column
                order_by_dir (str): 'ASC' or 'DESC', required if 'order_by' in kwargs
        """

        # if 'fc_order_by' in kwargs:
        #     fc_order_by = kwargs['fc_order_by']
        #     c.execute("""
        #                 SELECT  `fc_id`,`fc_title`
        #                 FROM    `tbl_learning_flash_cards`
        #                 ORDER BY `{ob}`
        #             """.format(ob=fc_order_by))


        command = "SELECT `tbl_learning_flash_cards`.`fc_id`,`tbl_learning_flash_cards`.`fc_title`"
        if data:
            command += ",`tbl_learning_flash_cards`.`fc_front`,`tbl_learning_flash_cards`.`fc_back`"
            command += ",`tbl_learning_flash_cards`.`fc_difficulty`,`tbl_learning_flash_cards`.`fc_level`"
            command += ",`tbl_learning_flash_cards`.`fc_next_date`"
        command += "FROM `tbl_learning_flash_cards`"

        if 'deck_id' in kwargs:
            deck_id = kwargs['deck_id']
            command += ",`tbl_learning_map_fc_fc_decks`"
            command += "WHERE `tbl_learning_flash_cards`.`fc_id` = `tbl_learning_map_fc_fc_decks`.`fc_id`"
            command += "AND `tbl_learning_map_fc_fc_decks`.`fc_deck_id` = '{fdid}'".format(fdid=deck_id)

        if study:
            import datetime
            today = datetime.datetime.today()
            today = "{y}-{m}-{d}".format(y=today.year, m=today.strftime('%m'), d=today.strftime('%d'))
            command += "AND `tbl_learning_flash_cards`.`fc_next_date` = '{t}'".format(t=today)

        if 'order_by' in kwargs:
            order_by = kwargs['order_by']
            order_by_dir = kwargs['order_by_dir']
            command += "ORDER BY `{ob}` {obd}".format(ob=order_by, obd=order_by_dir)

        c.execute(command)

        #     if 'data' in kwargs:
        #         if 'study' in kwargs:
        #             import datetime
        #             today = datetime.datetime.now()
        #             today = "{y}-{m}-{d}".format(y=today.year, m=today.month, d=today.day)
        #             c.execute("""
        #                         SELECT  `tbl_learning_flash_cards`.`fc_id`,`tbl_learning_flash_cards`.`fc_title`,
        #                                  `tbl_learning_flash_cards`.`fc_front`,`tbl_learning_flash_cards`.`fc_back`,
        #                                  `tbl_learning_flash_cards`.`fc_difficulty`,`tbl_learning_flash_cards`.`fc_level`,
        #                                  `tbl_learning_flash_cards`.`fc_next_date`
        #                         FROM     `tbl_learning_flash_cards`,`tbl_learning_fc_fc_decks`
        #                         WHERE    `tbl_learning_flash_cards`.`fc_id` = `tbl_learning_fc_fc_decks`.`fc_id`
        #                             AND  `tbl_learning_fc_fc_decks`.`fc_deck_id` = '{fdid}'
        #                             AND  `tbl_learning_flash_cards`.`fc_next_date` = {t}
        #                     """.format(fdid=fc_deck_id, t=today))
        #         else:
        #             c.execute("""
        #                         SELECT  `tbl_learning_flash_cards`.`fc_id`,`tbl_learning_flash_cards`.`fc_title`,
        #                                  `tbl_learning_flash_cards`.`fc_front`,`tbl_learning_flash_cards`.`fc_back`,
        #                                  `tbl_learning_flash_cards`.`fc_difficulty`,`tbl_learning_flash_cards`.`fc_level`,
        #                                  `tbl_learning_flash_cards`.`fc_next_date`
        #                         FROM     `tbl_learning_flash_cards`,`tbl_learning_fc_fc_decks`
        #                         WHERE    `tbl_learning_flash_cards`.`fc_id` = `tbl_learning_fc_fc_decks`.`fc_id`
        #                             AND  `tbl_learning_fc_fc_decks`.`fc_deck_id` = '{fdid}'
        #                     """.format(fdid=fc_deck_id))
        #     else:
        #         c.execute("""
        #                     SELECT  `tbl_learning_flash_cards`.`fc_id`,`tbl_learning_flash_cards`.`fc_title`,
        #                     FROM    `tbl_learning_map_fc_fc_decks`,`tbl_learning_flash_cards`
        #                     WHERE   `tbl_learning_map_fc_fc_decks`.`fc_deck_id` = '{fdid}'
        #                         AND `tbl_learning_map_fc_fc_decks`.`fc_id` = `tbl_learning_flash_cards`.`fc_id`
        #                 """.format(fdid=fc_deck_id))
        #
        # if 'fc_tag_id' in kwargs and 'data' in kwargs:
        #     fc_tag_id = kwargs['fc_tag_id']
        #     c.execute("""
        #                 SELECT  `tbl_learning_flash_cards`.`fc_id`,`tbl_learning_flash_cards`.`fc_title`,
        #                          `tbl_learning_flash_cards`.`fc_front`,`tbl_learning_flash_cards`.`fc_back`,
        #                          `tbl_learning_flash_cards`.`fc_difficulty`
        #                 FROM     `tbl_learning_flash_cards`,`tbl_learning_fc_fc_tags`
        #                 WHERE    `tbl_learning_flash_cards`.`fc_id` = `tbl_learning_fc_fc_tags`.`fc_id`
        #                      AND `tbl_learning_fc_fc_tags`.`fc_tag_id` = '{ftid}'
        #             """.format(ftid=fc_tag_id))
        #
        # if 'fc_tag_id' in kwargs and not 'data' in kwargs:
        #     fc_tag_id = kwargs['fc_tag_id']
        #     c.execute("""
        #                 SELECT  `tbl_learning_flash_cards`.`fc_id`,`tbl_learning_flash_cards`.`fc_title`
        #                 FROM    `tbl_learning_map_fc_fc_tags`,`tbl_learning_flash_cards`
        #                 WHERE   `tbl_learning_map_fc_fc_tags`.`fc_tag_id` = '{ftid}'
        #                     AND `tbl_learning_map_fc_fc_tags`.`fc_id` = `tbl_learning_flash_cards`.`fc_id`
        #             """.format(ftid=fc_tag_id))

        fc_list = c.fetchall()
        return fc_list

    @staticmethod
    def get_fc_data(fc_id):
        c.execute("""
                    SELECT  `fc_title`,`fc_front`,`fc_back`,`fc_difficulty`
                    FROM    `tbl_learning_flash_cards`
                    WHERE   `fc_id` = '{fcid}'
                """.format(fcid=fc_id))
        fc_data = c.fetchone()
        return fc_data

    @staticmethod
    def get_fc_tag_list(**kwargs):
        if 'fc_id' in kwargs:
            c.execute("""
                        SELECT  `tbl_learning_flash_cards_tags`.`fc_tag_id`,
                                `tbl_learning_flash_cards_tags`.`fc_tag_name`
                        FROM    `tbl_learning_flash_cards_tags`, `tbl_learning_map_fc_fc_tags`
                        WHERE   `tbl_learning_map_fc_fc_tags`.`fc_id` = '{fcid}'
                            AND `tbl_learning_flash_cards_tags`.`fc_tag_id` = `tbl_learning_map_fc_fc_tags`.`fc_tag_id`
                        ORDER BY `tbl_learning_flash_cards_tags`.`fc_tag_name`
                    """.format(fcid=kwargs['fc_id']))
        else:
            c.execute("""
                        SELECT  `fc_tag_id`,`fc_tag_name`
                        FROM    `tbl_learning_flash_cards_tags`
                    """)
        fc_tag_list = c.fetchall()
        return fc_tag_list

    @staticmethod
    def get_fc_tag_data(fc_tag_id):
        c.execute("""
                    SELECT  `fc_tag_name`,`fc_tag_excerpt`
                    FROM    `tbl_learning_flash_cards_tags`
                    WHERE   `fc_tag_name` = '{fcid}'
                """.format(fcid=fc_tag_id))
        fc_tag_data = c.fetchone()
        return fc_tag_data

    @staticmethod
    def get_book_data(book_id):
        c.execute("""
                    SELECT  `tbl_books`.`book_id`,`tbl_books`.`book_title`,`tbl_books`.`isbn`,`tbl_books`.`publisher`,
                            `tbl_books`.`year_published`,`tbl_books`.`original_year_published`,
                            `tbl_books`.`primary_genre`,`tbl_books`.`secondary_genre`,`tbl_books`.`cover_front`,
                            `tbl_books`.`cover_back`,`tbl_books`.`read_status`,`tbl_books`.`rating`,`tbl_books`.`notes`,
                            `tbl_books`.`textbook`,`tbl_books`.`timestamp`,
                            `tbl_book_publishers`.`publisher_name`
                    FROM    `tbl_books`,`tbl_book_publishers`
                    WHERE   `tbl_books`.`book_id` = '{bid}'
                """.format(bid=book_id))
        book_data = c.fetchone()
        return book_data

    @staticmethod
    def get_book_author_data(book_id):
        c.execute("""
                    SELECT  `tbl_book_authors`.`author_id`,`tbl_book_authors`.`author_first`,
                            `tbl_book_authors`.`author_middle`,`tbl_book_authors`.`author_last`
                    FROM    `tbl_book_authors`,`tbl_map_author_book`
                    WHERE   `tbl_map_author_book`.`tmab_book_id` = '{bid}'
                        AND `tbl_book_authors`.`author_id` = `tbl_map_author_book`.`tmab_author_id`
                """.format(bid=book_id))
        book_author = c.fetchall()
        return book_author

    @staticmethod
    def get_book_list():
        c.execute("""
                    SELECT  `book_id`,`book_title`,`primary_genre`,`read_status`
                    FROM    `tbl_books`
                    ORDER BY `tbl_books`.`book_title`
                """)
        book_list = c.fetchall()
        return book_list

    @staticmethod
    def get_book_user_notes(book_id):
        c.execute("""
                    SELECT  `note_id`,`tbn_note_title`,`tbn_note_excerpt`,`tbn_note_full`
                    FROM    `tbl_book_notes`
                    WHERE   `tbn_book_id` = '{bid}'
                """.format(bid=book_id))
        book_user_notes = c.fetchall()
        return book_user_notes

    @staticmethod
    def get_book_note_data(note_id):
        c.execute("""
                    SELECT  `tbn_note_title`,`tbn_note_excerpt`,`tbn_note_full`
                    FROM    `tbl_book_notes`
                    WHERE   `note_id` = '{nid}'
                """.format(nid=note_id))
        return c.fetchone()

    @staticmethod
    def get_author_list():
        c.execute("""
                    SELECT  `author_id`,`author_first`, `author_middle`,`author_last`
                    FROM    `tbl_book_authors`
                    ORDER BY `author_last`
                """)
        author_list = c.fetchall()
        return author_list

    @staticmethod
    def get_author_data(author_id):
        c.execute("""
                    SELECT  `author_id`,`author_first`, `author_middle`,`author_last`
                    FROM    `tbl_book_authors`
                    WHERE   `author_id` = '{aid}'
                    ORDER BY `author_last`
                """.format(aid=author_id))
        author_list = c.fetchall()
        return author_list

    @staticmethod
    def get_publisher_list():
        c.execute("""
                    SELECT  `publisher_id`,`publisher_name`
                    FROM    `tbl_book_publishers`
                    ORDER BY `publisher_name`
                """)
        publisher_list = c.fetchall()
        return publisher_list

    @staticmethod
    def get_publisher_data(publisher_name):
        c.execute("""
                    SELECT  `publisher_name`
                    FROM    `tbl_book_publishers`
                    WHERE   `publisher_name` = '{pn}'
                """.format(pn=publisher_name))
        publisher_data = c.fetchone()
        return publisher_data

    @staticmethod
    def get_publisher_data_by_id(publisher_id):
        c.execute("""
                    SELECT  `publisher_name`
                    FROM    `tbl_book_publishers`
                    WHERE   `publisher_id` = '{pid}'
                """.format(pid=publisher_id))
        publisher_data = c.fetchone()
        return publisher_data
class Navigation:

    @staticmethod
    def page_nav(**kwargs):
        gd = App.get_running_app()
        if 'dest' in kwargs:
            if kwargs['dest'] == 'prev_page':
                dest = gd.glob_dict['orig']
            else:
                dest = kwargs['dest']
            gd.glob_dict['orig'] = gd.glob_dict['cur_page']
            gd.glob_dict['cur_page'] = dest
        else:
            dest = 'home'
        if 'clear' in kwargs:
            if kwargs['clear'] in gd.glob_dict:
                del gd.glob_dict[kwargs['clear']]
        gd.glob_dict['edit'] = kwargs['edit'] if 'edit' in kwargs else False
        if 'book_id' in kwargs:
            gd.glob_dict['book_id'] = kwargs['book_id']
        if 'fc_deck_id' in kwargs:
            gd.glob_dict['fc_deck_id'] = kwargs['fc_deck_id']
        if 'note_id' in kwargs:
            gd.glob_dict['note_id'] = kwargs['note_id']
        if 'fc_id' in kwargs:
            gd.glob_dict['fc_id'] = kwargs['fc_id']
        gd.sm.current = dest

    @staticmethod
    def book_view_pressed(book_id, orig):
        gd = App.get_running_app()
        gd.glob_dict['book_id'] = book_id
        gd.glob_dict['orig'] = orig
        gd.sm.current = 'empty'
        gd.sm.current = 'book'

    @staticmethod
    def edit_book_pressed(book_id, orig):
        gd = App.get_running_app()
        gd.glob_dict['book_id'] = book_id
        gd.glob_dict['orig'] = orig
        gd.glob_dict['edit'] = True
        gd.sm.current = 'new_book'

    @staticmethod
    def book_note_pressed(note_id):
        gd = App.get_running_app()
        gd.glob_dict['edit'] = False
        gd.glob_dict['note_id'] = note_id
        popup = BookNotePopup()
        popup.open()

    @staticmethod
    def confirm_flash_card_deck_delete(fc_deck_id):
        gd = App.get_running_app()
        gd.glob_dict['fc_deck_id'] = fc_deck_id
        popup = DeleteFlashCardDeckConfirmationPopup()
        popup.open()

    @staticmethod
    def confirm_flash_card_delete(fc_id):
        gd = App.get_running_app()
        gd.glob_dict['fc_id'] = fc_id
        popup = DeleteFlashCardConfirmationPopup()
        popup.open()

    @staticmethod
    def edit_book_note_pressed(note_id, orig):
        gd = App.get_running_app()
        gd.glob_dict['note_id'] = note_id
        gd.glob_dict['orig'] = orig
        gd.glob_dict['edit'] = True
        gd.sm.current = 'new_book_note'

    @staticmethod
    def edit_book_author_pressed(author_id):
        gd = App.get_running_app()
        gd.glob_dict['author_id'] = author_id
        gd.glob_dict['edit'] = True
        gd.sm.current = 'new_book_author'


class DeleteFlashCardDeckConfirmationPopup(Popup):

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        self.fc_deck_id = gd.glob_dict['fc_deck_id']
        c.execute("""
                    SELECT `fc_deck_name`
                    FROM `tbl_learning_flash_cards_decks`
                    WHERE `fc_deck_id` = '{fdid}'
                    """.format(fdid=self.fc_deck_id))
        try:
            self.fc_deck_name = c.fetchone()[0]
        except:
            self.gd = App.get_running_app()
            self.gd.sm.current = 'flash_cards'

    def on_confirm(self):
        gd = App.get_running_app()
        c.execute("""
                    DELETE
                    FROM `tbl_learning_flash_cards_decks`
                    WHERE `fc_deck_id` = '{fdid}'
                    """.format(fdid=self.fc_deck_id))
        conn.commit()
        gd.glob_dict['edit'] = False
        Navigation.page_nav(dest='empty')
        Navigation.page_nav(dest='flash_cards', orig='flash_cards')
        self.dismiss()

    def on_close(self):
        self.dismiss()


class DeleteFlashCardConfirmationPopup(Popup):

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        self.fc_id = gd.glob_dict['fc_id']
        c.execute("""
                    SELECT `fc_title`
                    FROM `tbl_learning_flash_cards`
                    WHERE `fc_id` = '{fcid}'
                    """.format(fcid=self.fc_id))
        try:
            self.fc_title = c.fetchone()[0]
        except:
            Navigation.page_nav(dest='flash_card_deck', orig='flash_card_deck', edit=False)

    def on_confirm(self):
        gd = App.get_running_app()
        c.execute("""
                    DELETE
                    FROM `tbl_learning_flash_cards`
                    WHERE `fc_id` = '{fcid}'
                    """.format(fcid=self.fc_id))
        conn.commit()
        if gd.glob_dict['cur_page'] != 'flash_card_deck':
            Navigation.page_nav(dest='flash_cards', edit=False)
        Navigation.page_nav(dest='empty')
        Navigation.page_nav(dest=gd.glob_dict['cur_page'], orig=gd.glob_dict['orig'], edit=False)
        self.dismiss()

    def on_close(self):
        self.dismiss()
class BookNotePopup(Popup):

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        self.note_id = gd.glob_dict['note_id']
        note_data = Queries.get_book_note_data((self.note_id))
        self.note_title = note_data[0] if note_data[0] else ""
        self.note_excerpt = note_data[1] if note_data[1] else ""
        self.note_full = note_data[2] if note_data[2] else ""

    def on_close(self):
        self.dismiss()
class MiscFuns:

    def get_id(n):
        new_id = ''.join(random.SystemRandom().choice(string.digits) for _ in range(n))
        return new_id
class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)