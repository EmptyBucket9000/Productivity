from kivy.app import App
from kivy.uix.screenmanager import Screen
from lib import Queries
from lib import Navigation
from lib import MiscFuns
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.properties import DictProperty
from shutil import copyfile
from kivy.properties import ListProperty, ObjectProperty
import sqlite3, datetime, math

conn = sqlite3.connect("./Assets/db_productivity.sqlite3", detect_types=sqlite3.PARSE_DECLTYPES)
conn.execute('pragma foreign_keys=on')
c = conn.cursor()


class CodeSnippetsScreen(Screen):
    pass


class NewCodeSnippetScreen(Screen):
    pass


class NewCodeSnippetTagScreen(Screen):
    data = DictProperty({})
    __events__ = ('on_submit',)

    def on_parent(self, widget, parent):
        gd = App.get_running_app()
        if gd.glob_dict['edit']:
            self.code_tag_id = gd.glob_dict['code_tag_id']
            self.code_tag_name = gd.glob_dict['code_tag_name']
            code_tag_data = Queries.get_code_tag_data(self.code_tag_id)
            self.data['code_tag_excerpt'] = code_tag_data[1] if code_tag_data[1] else ""
        else:
            self.data = {}
            self.data['code_tag_name'] = ""
            self.data['code_tag_excerpt'] = ""
        self.data['orig'] = gd.glob_dict['orig']

    def on_submit(self, data):
        gd = App.get_running_app()
        code_tag_name = data['code_tag_name'] if data['code_tag_name'] else " "
        code_tag_excerpt = data['code_tag_excerpt'] if data['code_tag_excerpt'] else " "
        if gd.glob_dict['edit']:
            self.code_tag_id = gd.glob_dict['code_tag_id']
            self.code_tag_name = gd.glob_dict['code_tag_name']
            c.execute("""
                        UPDATE `tbl_code_tags`
                        SET `code_tag_name` = '{ctn}',
                            `code_tag_excerpt` = '{cte}'
                        WHERE `code_tag_id` = '{cid}'
                    """.format(cid=self.code_tag_id, ctn=self.code_tag_name, cte=code_tag_excerpt))
        else:
            code_tag_id = MiscFuns.get_id(16)
            c.execute("""
                        INSERT INTO `tbl_code_tags` (`code_tag_id`,`code_tag_name`,`code_tag_excerpt`)
                        VALUES (?,?,?)
                    """, (code_tag_id, code_tag_name, code_tag_excerpt))
        gd.glob_dict['edit'] = False
        conn.commit()
        Navigation.page_nav(dest=self.data['orig'], orig='new_code_tag', edit=False)