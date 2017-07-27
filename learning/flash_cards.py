from kivy.app import App
from kivy.uix.screenmanager import Screen
from App.lib import Queries
from App.lib import Navigation
from App.lib import MiscFuns
from kivy.uix.popup import Popup
from kivy.properties import DictProperty
from shutil import copyfile
from kivy.properties import ListProperty, ObjectProperty
import sqlite3

conn = sqlite3.connect("./Assets/db_productivity.sqlite3")
conn.execute('pragma foreign_keys=on')
c = conn.cursor()


class FlashCardsScreen(Screen):

    def on_parent(self, Screen, parent):
        fc_deck_list = Queries.get_fc_deck_list()
        fc_decks = []
        for fc_deck in fc_deck_list:
            temp = {
                "fc_deck_id": str(fc_deck[0]),
                "fc_deck_name": fc_deck[1],
                "fc_deck_excerpt": fc_deck[2]
            }
            fc_decks.append(temp)
        self.fc_deck_rv.data = fc_decks


class FlashCardDeckStudyScreen(Screen):
    data = DictProperty({})

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        from random import shuffle
        self.fc_deck_id = gd.glob_dict['fc_deck_id']
        fc_list = Queries.get_fc_list(deck_id=self.fc_deck_id, data=True, study=False)
        shuffle(fc_list)
        # self.data['fc_id'] = fc_
        # self.data['fc_title'] =


class AllFlashCardsScreen(Screen):
    data = DictProperty({})

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        fc_order_by = gd.glob_dict['fc_order_by'] if 'fc_order_by' in gd.glob_dict else "fc_title"
        fc_list = []
        try:
            fc_full_list = Queries.get_fc_list(order_by=fc_order_by, order_by_dir="ASC")
            if len(fc_full_list) > 0:
                for fc in fc_full_list:
                    fc_deck_list = Queries.get_fc_deck_list(fc_id=fc[0])
                    fc_tag_list = Queries.get_fc_tag_list(fc_id=fc[0])
                    fc_tags = []
                    fc_decks = []
                    for fc_deck in fc_deck_list:
                        fc_decks.append(fc_deck[1])
                    for fc_tag in fc_tag_list:
                        fc_tags.append(fc_tag[1])
                    temp = {
                        "fc_id": str(fc[0]),
                        "fc_title": fc[1],
                        "fc_decks": ", ".join(fc_decks),
                        "fc_tags": ", ".join(fc_tags)
                    }
                    fc_list.append(temp)
                self.fc_rv.data = fc_list
            else:
                self.fc_rv.data = ""
        except sqlite3.Error as e:
            print("An error occurred:", e.args[0])


class FlashCardDeckScreen(Screen):
    data = DictProperty({})

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        try:
            self.fc_deck_id = gd.glob_dict['fc_deck_id']
            fc_deck_data = Queries.get_fc_deck_data(self.fc_deck_id)
            fc_deck_fc_list = Queries.get_fc_list(deck_id=self.fc_deck_id)
            fc_list = []
            if len(fc_deck_fc_list) > 0:
                for fc in fc_deck_fc_list:
                    temp = {
                        "fc_id": str(fc[0]),
                        "fc_title": (fc[1])
                    }
                    fc_list.append(temp)
                self.fc_rv.data = fc_list
            else:
                self.fc_rv.data = ""
            self.data['fc_deck_id'] = self.fc_deck_id
            self.data['fc_deck_name'] = fc_deck_data[0]
            self.data['fc_deck_excerpt'] = fc_deck_data[1]
        except sqlite3.Error as e:
            print("An error occurred:", e.args[0])


class NewFlashCardDeckScreen(Screen):
    data = DictProperty({})
    __events__ = ('on_submit',)

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        if gd.glob_dict['edit']:
            self.fc_deck_id = gd.glob_dict['fc_deck_id']
            # self.fc_deck_name = gd.glob_dict['fc_deck_name'] if 'fc_deck_name' in gd.glob_dict else ""
            fc_deck_data = Queries.get_fc_deck_data(self.fc_deck_id)
            self.data['fc_deck_name'] = fc_deck_data[0] if fc_deck_data[0] else ""
            self.data['fc_deck_excerpt'] = fc_deck_data[1] if fc_deck_data[1] else ""
        else:
            self.data = {}
            self.data['fc_deck_name'] = ""
            self.data['fc_deck_excerpt'] = ""
        self.data['orig'] = gd.glob_dict['orig']

    def on_submit(self, data):
        gd = App.get_running_app()
        fc_deck_name = data['fc_deck_name'] if data['fc_deck_name'] else " "
        fc_deck_excerpt = data['fc_deck_excerpt'] if data['fc_deck_excerpt'] else " "
        if gd.glob_dict['edit']:
            self.fc_deck_id = gd.glob_dict['fc_deck_id']
            # self.fc_deck_name = gd.glob_dict['fc_deck_name']
            c.execute("""
                        UPDATE `tbl_learning_flash_cards_decks`
                        SET `fc_deck_name` = '{fdn}',
                            `fc_deck_excerpt` = '{fde}'
                        WHERE `fc_deck_id` = '{fdid}'
                    """.format(fdid=self.fc_deck_id, fdn=fc_deck_name, fde=fc_deck_excerpt))
        else:
            fc_deck_id = MiscFuns.get_id(16)
            c.execute("""
                        INSERT INTO `tbl_learning_flash_cards_decks` (`fc_deck_id`,`fc_deck_name`,`fc_deck_excerpt`)
                        VALUES (?,?,?)
                    """, (fc_deck_id, fc_deck_name, fc_deck_excerpt))
        gd.glob_dict['edit'] = False
        conn.commit()
        Navigation.page_nav(dest=self.data['orig'], orig='flash_cards', edit=False)


class NewFlashCardScreen(Screen):
    data = DictProperty({})
    data_fc_tag_ids = DictProperty({})
    data_fc_deck_ids = DictProperty({})
    __events__ = ('on_submit',)
    fc_tag_spinner_list = ListProperty(None)
    fc_deck_spinner_list = ListProperty(None)

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        self.fc_tag_spinner_list = []
        fc_tag_list = Queries.get_fc_tag_list()
        if len(fc_tag_list) > 0:
            for fc_tag in fc_tag_list:
                self.fc_tag_spinner_list.append(fc_tag[1])
                self.data_fc_tag_ids[fc_tag[1]] = fc_tag[0]
        else:
            self.fc_tag_spinner_list.append("")
        self.fc_deck_spinner_list = []
        fc_deck_list = Queries.get_fc_deck_list()
        if len(fc_deck_list) > 0:
            for fc_deck in fc_deck_list:
                self.fc_deck_spinner_list.append(fc_deck[1])
                self.data_fc_deck_ids[fc_deck[1]] = fc_deck[0]
        else:
            self.fc_deck_spinner_list.append("")
        if gd.glob_dict['edit']:
            self.fc_id = gd.glob_dict['fc_id']
            fc_data = Queries.get_fc_data(self.fc_id)
            fc_tags = Queries.get_fc_tag_list(fc_id=self.fc_id)
            if len(fc_tags) > 0:
                self.fc_tags = ""
                for tag in fc_tags:
                    self.fc_tags += str(tag[1]) + ";"
                self.fc_tags = self.fc_tags[:-1]
            else:
                self.fc_tags = ""
            fc_decks = Queries.get_fc_decks_from_fc(self.fc_id)
            if len(fc_tags) > 0:
                self.fc_decks = ""
                for deck in fc_decks:
                    self.fc_decks += str(deck[0]) + ";"
                self.fc_decks = self.fc_decks[:-1]
            else:
                self.fc_decks = ""
            self.data['fc_tags'] = self.fc_tags
            self.data['fc_decks'] = self.fc_decks
            self.data['fc_title'] = fc_data[0]
            self.data['fc_front'] = fc_data[1] if fc_data[1] else ""
            self.data['fc_back'] = fc_data[2] if fc_data[2] else ""
            self.data['fc_difficulty'] = fc_data[3]
        else:
            self.data = {}
            self.data['fc_title'] = ""
            self.data['fc_front'] = ""
            self.data['fc_back'] = ""
            self.data['fc_difficulty'] = ""
            if 'fc_tags' in self.data:
                del self.data['fc_tags']
        self.data['orig'] = gd.glob_dict['orig']

    def get_spinner_lists(self):
        pass

    def on_submit(self, data):
        gd = App.get_running_app()
        self.data['orig'] = gd.glob_dict['orig']
        title = data['fc_title'] if 'fc_title' in data else " "
        front = data['fc_front'] if 'fc_front' in data else " "
        back = data['fc_back'] if 'fc_back' in data else " "
        difficulty = data['fc_difficulty'] if 'fc_difficulty' in data else 0
        if gd.glob_dict['edit']:
            self.fc_id = gd.glob_dict['fc_id']
            try:
                c.execute("""
                            UPDATE `tbl_learning_flash_cards`
                            SET `fc_title` = '{ft}',
                                `fc_front` = '{ff}',
                                `fc_back` = '{fb}',
                                `fc_difficulty` = '{l}'
                            WHERE `fc_id` = '{fcid}'
                        """.format(ft=title, ff=front, fb=back, l=difficulty, fcid=self.fc_id))
                conn.commit()
            except sqlite3.Error as e:
                print("An error occurred:", e.args[0])
            gd.glob_dict['edit'] = False
        else:
            self.fc_id = MiscFuns.get_id(16)
            try:
                c.execute("""
                            INSERT INTO `tbl_learning_flash_cards` (`fc_id`,`fc_title`,`fc_front`,`fc_back`,`fc_difficulty`)
                            VALUES (?,?,?,?,?)
                        """, (self.fc_id, title, front, back, difficulty))
                conn.commit()
            except sqlite3.Error as e:
                print("An error occurred:", e.args[0])

        if 'fc_tags' in data:
            tags = data['fc_tags'].split(';') if data['fc_tags'] else ""
            for fc_tag in tags:
                try:
                    c.execute("""
                                INSERT INTO `tbl_learning_map_fc_fc_tags` (`fc_id`,`fc_tag_id`)
                                VALUES (?,?)
                            """, (self.fc_id, self.data_fc_tag_ids[fc_tag]))
                    conn.commit()
                except sqlite3.Error as e:
                    print("An error occurred:", e.args[0])

        if 'fc_decks' in data:
            decks = data['fc_decks'].split(';') if data['fc_decks'] else ""
            for fc_deck in decks:
                try:
                    c.execute("""
                                INSERT INTO `tbl_learning_map_fc_fc_decks` (`fc_id`,`fc_deck_id`)
                                VALUES (?,?)
                            """, (self.fc_id, self.data_fc_deck_ids[fc_deck]))
                    conn.commit()
                except sqlite3.Error as e:
                    print("An error occurred:", e.args[0])

        # self.data.clear()
        data.clear()
        self.data.clear()
        self.data_fc_tag_ids.clear()
        self.data_fc_deck_ids.clear()

        # Navigation.page_nav(dest='empty')
        Navigation.page_nav(dest='flash_cards', orig='new_flash_card', edit=False, del_cls='NewFlashCardScreen')


class NewFlashCardTagScreen(Screen):
    data = DictProperty({})
    __events__ = ('on_submit',)

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        if gd.glob_dict['edit']:
            self.fc_tag_id = gd.glob_dict['fc_tag_id']
            self.fc_tag_name = gd.glob_dict['fc_tag_name']
            fc_tag_data = Queries.get_fc_tag_data(self.fc_tag_id)
            self.data['fc_tag_excerpt'] = fc_tag_data[1] if fc_tag_data[1] else ""
        else:
            self.data = {}
            self.data['fc_tag_name'] = ""
            self.data['fc_tag_excerpt'] = ""
        self.data['orig'] = gd.glob_dict['orig']

    def on_submit(self, data):
        gd = App.get_running_app()
        fc_tag_name = data['fc_tag_name'] if data['fc_tag_name'] else " "
        fc_tag_excerpt = data['fc_tag_excerpt'] if data['fc_tag_excerpt'] else " "
        if gd.glob_dict['edit']:
            self.fc_tag_id = gd.glob_dict['fc_tag_id']
            self.fc_tag_name = gd.glob_dict['fc_tag_name']
            c.execute("""
                        UPDATE `tbl_learning_flash_cards_tags`
                        SET `fc_tag_name` = '{ftn}',
                            `fc_tag_excerpt` = '{fte}'
                        WHERE `fc_tag_id` = '{ftid}'
                    """.format(ftid=self.fc_tag_id, ftn=self.fc_tag_name, fte=fc_tag_excerpt))
        else:
            fc_tag_id = MiscFuns.get_id(16)
            c.execute("""
                        INSERT INTO `tbl_learning_flash_cards_tags` (`fc_tag_id`,`fc_tag_name`,`fc_tag_excerpt`)
                        VALUES (?,?,?)
                    """, (fc_tag_id, fc_tag_name, fc_tag_excerpt))
        gd.glob_dict['edit'] = False
        conn.commit()
        Navigation.page_nav(dest=self.data['orig'], orig='flash_cards', edit=False)