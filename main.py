import os

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout

from popup_widgets.FileMovePopup import FileMovePopup
from popup_widgets.FileRenamePopup import FileRenamePopup
from popup_widgets.FileScrapyPopup import FileScrapyPopup
from popup_widgets.FileSearchPopup import FileSearchPopup
from popup_widgets.OperationPopup import OperationPopup
from kivy.config import Config
# from kivy.metrics import dp
# label.font_size = dp(16)
Config.set('graphics', 'multisamples', '4')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'width', '1920')
Config.set('graphics', 'height', '1080')

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
        return main_page
    #     from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
    #     from views.file_manage.file_manage_view import FileManageScreen
    #     layout = BoxLayout(orientation='vertical')
    #     self.sm = ScreenManager()
    #     self.sm.add_widget(FileManageScreen(name='测试'))
    #     # layout.add_widget(self.sm)
    #     return self.sm
    #
    #
    #     # main_page = MenuPage()
    #     # print(os.environ)
    #     # return main_page
    # def switch_screen(self, instance):
    #     self.sm.current_screen = '测试'


if __name__ == '__main__':
    MainApp().run()
