from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import DictProperty
from lib import Queries
from lib import Navigation
import string, random, sqlite3, os

conn = sqlite3.connect("./Assets/db_productivity.sqlite3", detect_types=sqlite3.PARSE_DECLTYPES)
conn.execute('pragma foreign_keys=on')
c = conn.cursor()


class NewCodingLanguageScreen(Screen):
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