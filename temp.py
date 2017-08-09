import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Line
kivy.require('1.9.1')


class Painting(Widget):
    line = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.line = True
            with self.canvas:
                touch.ud["my_line"] = Line(points=(touch.x, touch.y), width=thickness)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos) and self.line:
            touch.ud["my_line"].points += (touch.x, touch.y)

    def on_touch_up(self, touch):
        self.line = False


class Controller(BoxLayout):
    def __init__(self):
        super(Controller, self).__init__()

    def new_thickness(self, *args):
        t = args[1]
        global thickness
        thickness = t


class SimpleLine2App(App):

    def build(self):
        return Controller()

thickness = 1

if __name__ == "__main__":
    SimpleLine2App().run()