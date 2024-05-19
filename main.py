import os

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from popup_widgets.OperationPopup import OperationPopup
from popup_widgets.FileMovePopup import FileMovePopup
from popup_widgets.FileRenamePopup import FileRenamePopup
from popup_widgets.FileScrapyPopup import FileScrapyPopup
from popup_widgets.FileSearchPopup import FileSearchPopup

from common.widgets import MenuForm, PathInput

LabelBase.register(name="Roboto", fn_regular="font_family/xingcao.ttf")


class MenuPage(BoxLayout):
    def open_dialog(self, button_text: str, path_text: str):
        if not hasattr(self, button_text):
            btn_pop_mapping = {
                'file_move': FileMovePopup,
                'file_search': FileSearchPopup,
                'file_rename': FileRenamePopup,
                'file_scrapy': FileScrapyPopup
            }
            pop_up_class: type = btn_pop_mapping[button_text]
            pop_up: OperationPopup = pop_up_class()
            # pop_up.init_main_part()
            setattr(self, button_text, pop_up)
            pop_up.init_main()
        getattr(self, button_text).path_text = path_text
        getattr(self, button_text).path_label.text = path_text
        getattr(self, button_text).open()

    def get_path_input_text(self):
        return self.ids.path_input.text

    def on_file_move_press(self):
        self.open_dialog('file_move', self.get_path_input_text())

    def on_file_rename_press(self):
        self.open_dialog('file_rename', self.get_path_input_text())

    def on_file_search_press(self):
        self.open_dialog('file_search', self.get_path_input_text())

    def on_file_scrapy_press(self):
        self.open_dialog('file_scrapy', self.get_path_input_text())


class MainApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = '文件管理'
        
    def build(self):
        main_page = MenuPage()
        print(os.environ)
        return main_page


if __name__ == '__main__':
    MainApp().run()
