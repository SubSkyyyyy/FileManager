from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox

from common.config import CLOSE, ENTER, ROLL_BACK
from common.widgets import CustomLabel


class OperationPopup(Popup):

    # def __init__(self, path_text: str = '', **kwargs):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.path_text = StringProperty('')
        # self.path_text = path_text
        self.widget_list: list = []
        self.roll_back_able = False
        self.check_box_dict = {}

    def init_main(self):
        self.prepare_widgets()
        self.main_body = BoxLayout(orientation='vertical')
        self.path_label = CustomLabel(size_hint=(1.0, 0.25), font_size=30)
        self.main_body.add_widget(self.path_label)

        if self.widget_list:
            for widget in self.widget_list:
                self.main_body.add_widget(widget)

        bottom_layout = BoxLayout(orientation='horizontal', size_hint=(1.0, 0.18))
        btn_enter = Button(text=ENTER, size_hint=(0.5, 1.0))
        btn_enter.bind(on_release=self.execute_enter_event)
        btn_close = Button(text=CLOSE, size_hint=(0.5, 1.0))
        btn_close.bind(on_release=self.dismiss)
        bottom_layout.add_widget(btn_enter)
        bottom_layout.add_widget(btn_close)
        if self.roll_back_able:
            btn_roll_back = Button(text=ROLL_BACK, size_hint=(0.5, 1.0))
            # btn_close.bind(on_release=self.dismiss)
            btn_roll_back.bind(on_press=self.press_roll_back)
            bottom_layout.add_widget(btn_roll_back)
        self.main_body.add_widget(bottom_layout)
        self.add_widget(self.main_body)

    def press_enter(self):
        pass

    def prepare_widgets(self):
        pass

    def press_roll_back(self, instance):
        pass

    def on_toggle_btn_release(self, instance):
        instance.state = 'down'

    def show_finish_pop_up(self, msg='操作完成'):
        finish_pop_up = Popup(title='完成', size_hint=(0.5, 0.5), title_size=25)
        finish_box_layout = BoxLayout(orientation='vertical')
        finish_text = CustomLabel(text=msg, size_hint=(1.0, 0.8), halign='center')
        finish_ensure_btn = Button(text='确认', size_hint=(1.0, 0.2), halign='center')
        finish_ensure_btn.bind(on_press=finish_pop_up.dismiss)
        finish_box_layout.add_widget(finish_text)
        finish_box_layout.add_widget(finish_ensure_btn)
        finish_pop_up.add_widget(finish_box_layout)
        finish_pop_up.open()


    def execute_enter_event(self, instance):
        try:
            self.press_enter()
        except Exception as e:
            error_popup = Popup(title='错误', size_hint=(0.5, 0.5), title_size=25)
            error_box = BoxLayout(orientation='vertical')
            error_info_label = CustomLabel(text=str(e), halign='center', valign='center')
            btn_dismiss = Button(text='确认', size_hint=(1.0, 0.2), halign='center')
            btn_dismiss.bind(on_release=error_popup.dismiss)
            error_box.add_widget(error_info_label)
            error_box.add_widget(btn_dismiss)
            error_popup.add_widget(error_box)
            error_popup.open()

    def bind_label_with_checkbox(self, label: CustomLabel):
        label.bind(on_touch_down=self.check_opt_by_label)


    def check_opt_by_label(self, instance, touch):
        if instance.collide_point(*touch.pos):
            checkbox = self.check_box_dict[instance.text]
            checkbox.active = not checkbox.active

    def show_error_pop_up(self, error_msg):
        finish_pop_up = Popup(title='错误', size_hint=(0.5, 0.5), title_size=25)
        finish_box_layout = BoxLayout(orientation='vertical')
        finish_text = CustomLabel(text=error_msg, size_hint=(1.0, 0.8), halign='center')
        finish_ensure_btn = Button(text='确认', size_hint=(1.0, 0.2), halign='center')
        finish_ensure_btn.bind(on_press=finish_pop_up.dismiss)
        finish_box_layout.add_widget(finish_text)
        finish_box_layout.add_widget(finish_ensure_btn)
        finish_pop_up.add_widget(finish_box_layout)
        finish_pop_up.open()

    def on_toggle_btn_press(self, instance):
        pass
