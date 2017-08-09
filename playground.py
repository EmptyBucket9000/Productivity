from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.stencilview import StencilView
from kivy.graphics import Color, Ellipse, Line
from kivy.properties import DictProperty
from random import random

class PlaySpace(Screen):
    pass

class DrawSpace(StencilView):

    def on_touch_down(self, touch):
        gd = App.get_running_app()
        try:
            self.c = [gd.glob_dict['r'], gd.glob_dict['g'], gd.glob_dict['b'], gd.glob_dict['a']]
        except:
            self.c = [0, 0, 0, 1]
        try:
            self.line_width = gd.glob_dict['line_width']
        except:
            self.line_width = 1.5
        ud = touch.ud
        if 'pressure' in touch.profile:
            ud['pressure'] = touch.pressure
            self.line_width = (touch.pressure * 100000) ** 2

        # with self.ids['cid'].canvas:
        with self.canvas:
            Color(self.c[0], self.c[1], self.c[2], self.c[3])
            ud['line'] = Line(points=(touch.x, touch.y), width=self.line_width)

    def on_touch_move(self, touch):
        ud = touch.ud
        ud['line'].points += [touch.x, touch.y]

        # if pressure changed create a new point instruction
        if 'pressure' in ud:
            if not .95 < (touch.pressure / ud['pressure']) < 1.05:
                self.line_width = (touch.pressure * 100000) ** 2
                with self.canvas:
                    Color(self.c[0], self.c[1], self.c[2], self.c[3])
                    ud['line'] = Line(points=(touch.x, touch.y), width=self.line_width)

    @staticmethod
    def set_color(rgba):
        gd = App.get_running_app()
        gd.glob_dict['r'] = rgba[0]
        gd.glob_dict['g'] = rgba[1]
        gd.glob_dict['b'] = rgba[2]
        gd.glob_dict['a'] = rgba[3]

    @staticmethod
    def set_line_width(line_width):
        gd = App.get_running_app()
        gd.glob_dict['line_width'] = line_width

    @staticmethod
    def save(id,file):
        print(id)
        id.export_to_png(file)