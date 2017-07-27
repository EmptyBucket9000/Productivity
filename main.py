import kivy
kivy.require('1.10.0')
from kivy.config import Config
Config.set('graphics', 'width', '1300')
Config.set('graphics', 'height', '800')
import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.factory import Factory
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from App.learning import flash_cards as fc
from App.media import books

# Connect to the database
conn = sqlite3.connect("./Assets/db_productivity.sqlite3")
conn.execute('pragma foreign_keys=on')
c = conn.cursor()


class HomeScreen(Screen):
    pass
class HelpScreen(Screen):
    pass
class MultiSelectSpinner(Button):

    dropdown = ObjectProperty(None)
    values = ListProperty([])
    selected_values = ListProperty([])

    def __init__(self, **kwargs):
        # self.values.clear()
        # self.selected_values.clear()
        self.bind(dropdown=self.update_dropdown)
        self.bind(values=self.update_dropdown)
        super(MultiSelectSpinner, self).__init__(**kwargs)
        self.bind(on_release=self.toggle_dropdown)

    def toggle_dropdown(self, *args):
        if self.dropdown.parent:
            self.dropdown.dismiss()
        else:
            self.dropdown.open(self)

    def update_dropdown(self, *args):
        if not self.dropdown:
            self.dropdown = DropDown()
        values = self.values
        if values:
            if self.dropdown.children:
                self.dropdown.clear_widgets()
            for value in values:
                b = Factory.MultiSelectOption(text=value)
                b.bind(state=self.select_value)
                self.dropdown.add_widget(b)

    def select_value(self, instance, value):
        if value == 'down':
            if instance.text not in self.selected_values:
                self.selected_values.append(instance.text)
        else:
            if instance.text in self.selected_values:
                self.selected_values.remove(instance.text)

    def on_selected_values(self, instance, value):
        if value:
            self.text = ';'.join(value)
        else:
            self.text = ''
class EmptyScreen(Screen):
    pass
class ProductivityApp(App):
    glob_dict = {}
    glob_dict['edit'] = False
    glob_dict['cur_page'] = 'home'
    sm = ScreenManager(transition=NoTransition())

    def build(self):
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(HelpScreen(name='help'))
        self.sm.add_widget(EmptyScreen(name='empty'))

        self.sm.add_widget(books.BooksScreen(name='books'))
        self.sm.add_widget(books.BookScreen(name='book'))
        self.sm.add_widget(books.NewBookScreen(name='new_book'))
        self.sm.add_widget(books.NewBookNoteScreen(name='new_book_note'))
        self.sm.add_widget(books.NewAuthorScreen(name='new_book_author'))
        self.sm.add_widget(books.NewPublisherScreen(name='new_book_publisher'))

        self.sm.add_widget(fc.FlashCardsScreen(name='flash_cards'))
        self.sm.add_widget(fc.AllFlashCardsScreen(name='all_flash_cards'))
        self.sm.add_widget(fc.FlashCardDeckScreen(name='flash_card_deck'))
        self.sm.add_widget(fc.FlashCardDeckStudyScreen(name='flash_card_deck_study'))
        self.sm.add_widget(fc.NewFlashCardScreen(name='new_flash_card'))
        self.sm.add_widget(fc.NewFlashCardTagScreen(name='new_flash_card_tag'))
        self.sm.add_widget(fc.NewFlashCardDeckScreen(name='new_flash_card_deck'))

        return self.sm

if __name__ == '__main__':
    ProductivityApp().run()

