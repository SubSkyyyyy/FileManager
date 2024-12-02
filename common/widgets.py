from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout


class CustomLabel(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_widget()
    def bind_on_touch_down(self, on_touch_down):
        self.bind(on_touch_down=on_touch_down)

    def unbind_on_touch_down(self):
        self.on_touch_down = super().on_touch_down

    def set_widget(self):
        self.readonly = True
        self.background_color = (0, 0, 0, 1)
        self.foreground_color = (1, 1, 1, 1)
        self.cursor_color = (0, 0, 0, 0)
        self.border = [0, 0, 0, 0]

    def reset_widget(self):
        self.readonly = False
        self.background_color = [1, 1, 1, 1]
        self.foreground_color = [0, 0, 0, 1]
        self.cursor_color = [0, 0, 0, 1]
        self.border = [4, 4, 4, 4]

class MenuForm(GridLayout):
    pass


class PathInput(BoxLayout):
    pass
