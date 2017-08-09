from kivy.app import App
from kivy.uix.screenmanager import Screen
from lib import Queries
from lib import Navigation
from lib import MiscFuns
# from lib import MiscFuns
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.properties import DictProperty
from shutil import copyfile
from kivy.properties import ListProperty, ObjectProperty
import sqlite3, datetime, math

conn = sqlite3.connect("./Assets/db_productivity.sqlite3", detect_types=sqlite3.PARSE_DECLTYPES)
conn.execute('pragma foreign_keys=on')
c = conn.cursor()


class JournalScreen(Screen):
    pass


class NewJournalEntryScreen(Screen):
    pass