import os
from popup_widgets.OperationPopup import OperationPopup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image

from common.widgets import CustomLabel

from file_operation.file_search import file_search
from common.utils import open_file_by_default_app, generate_thumbnail


class FileSearchPopup(OperationPopup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = '文件搜索'

    def prepare_widgets(self):
        input_layout = BoxLayout(orientation='horizontal', size_hint=(1.0, 0.3))
        input_label = CustomLabel(text='关键字', font_size=25, size_hint=(0.1, 1.0), valign='center', halign='center')
        self.search_input = TextInput(size_hint=(0.9, 1.0))
        input_layout.add_widget(input_label, self.search_input)
        input_layout.add_widget(self.search_input)

        self.opt_toggles = []
        self.search_by_key = '文件名查找 (支持正则表达式)'
        self.search_by_spent = '按时长查找视频文件 (例: 00:00-03:00)'
        self.search_by_same_spent = '相同视频时长查找 (如需过滤文件, 支持正则表达式)'
        self.search_by_same_size = '相同文件大小查找 (如需过滤文件, 支持正则表达式)'
        self.opt_dict = {
            self.search_by_key: 'search_by_key',
            self.search_by_spent: 'search_by_spent',
            self.search_by_same_spent: 'search_by_same_spent',
            self.search_by_same_size: 'search_by_same_size'
        }

        for key in self.opt_dict:
            tg = ToggleButton(group='search', text=key, size_hint=(1.0, 0.5))
            tg.bind(on_release=self.on_toggle_btn_release)
            self.opt_toggles.append(tg)
        self.opt_toggles[0].state = 'down'

        self.widget_list.append(input_layout)
        for tg in self.opt_toggles:
            self.widget_list.append(tg)

    def get_params(self):
        if not self.path_text:
            raise Exception('未输入根目录路径!')
        selected_radio = list(filter(lambda i: i.state == 'down', self.opt_toggles))
        if selected_radio:
            selected_radio = selected_radio[0]
        else:
            raise Exception('未选择要进行的操作!')
        text_input = self.search_input.text
        if selected_radio.text in [self.search_by_key, self.search_by_spent] and not text_input:
            raise Exception('需要输入关键字(正则表达式)或时长区间!')
        if selected_radio.text == self.search_by_spent:
            times = text_input.split('-')
            if len(times) != 2:
                raise Exception('时长区间格式不正确')
            for i in times:
                t_split = i.split(':')
                if len(t_split) not in [2, 3]:
                    raise Exception('时间格式不符合')
                for t_s in t_split:
                    try:
                        t_s = int(t_s)
                    except Exception:
                        raise Exception('时间格式不正确')
                    if t_s > 60 and t_split.index(t_s) in [1, 2]:
                        raise Exception('时间格式不正确')
        return selected_radio.text, text_input

    def press_enter(self):
        try:
            opt, text_input = self.get_params()
            result = file_search(self.path_text, self.opt_dict[opt], text_input)
            result_popup = Popup(title='搜索结果', title_size=30)
            pop_main_layout = BoxLayout(orientation='vertical')
            scroll_view = ScrollView(size_hint=(1.0, 0.95), do_scroll_x=False, do_scroll_y=True,
                                     bar_width=10, bar_color=[0.75, 0.75, 0.75, 1],
                                     bar_inactive_color=[0.5, 0.5, 0.5, 1], scroll_wheel_distance=120,
                                     bar_pos_y='right', scroll_type=['bars'])
            result_list_layout = BoxLayout(orientation='vertical', size_hint_y=None, padding=[0, 0, 10, 0])
            result_list_layout.bind(minimum_height=result_list_layout.setter('height'))
            if opt in [self.search_by_key, self.search_by_spent]:
                for r in result:
                    item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=120)
                    file_label_layout = BoxLayout(orientation='horizontal', size_hint=(0.8, 1.0))
                    img_path = generate_thumbnail(r)
                    if img_path:
                        image = Image(source=img_path, size_hint=(0.2, 1.0))
                        file_label_layout.add_widget(image)
                    file_path_label = CustomLabel(text=r.replace(self.path_text, '').strip('\\'), size_hint=(0.8, 1.0), font_size=25)
                    file_size = round(os.path.getsize(r) / 1024 / 1024, 2)
                    size_label = CustomLabel(text='{}m'.format(file_size), size_hint=(0.1, 1.0), font_size=20)
                    file_label_layout.bind(on_touch_down=self.open_file)
                    file_label_layout.add_widget(file_path_label)
                    file_label_layout.add_widget(size_label)

                    open_dir_btn = Button(text='所在位置', size_hint=(0.1, 1.0))
                    open_dir_btn.bind(on_press=self.open_file_dir)
                    rm_btn = Button(text='删除', size_hint=(0.1, 1.0))
                    rm_btn.bind(on_press=self.remove_item_widget)
                    item_layout.add_widget(file_label_layout)
                    item_layout.add_widget(open_dir_btn)
                    item_layout.add_widget(rm_btn)
                    result_list_layout.add_widget(item_layout)
            else:
                for t in result:
                    if len(result[t]) < 2:
                        continue
                    item_label = CustomLabel(text=str(t), font_size=30, size_hint_y=None, height=120, halign='center', valign='center')
                    result_list_layout.add_widget(item_label)
                    for r in result[t]:
                        item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=100)
                        file_label_layout = BoxLayout(orientation='horizontal', size_hint=(0.8, 1.0))
                        img_path = generate_thumbnail(r)
                        if img_path:
                            image = Image(source=img_path, size_hint=(0.2, 1.0))
                            file_label_layout.add_widget(image)
                        file_path_label = CustomLabel(text=r.replace(self.path_text, '').strip('\\'), size_hint=(0.8, 1.0), font_size=25)
                        file_size = round(os.path.getsize(r) / 1024 / 1024, 2)
                        size_label = CustomLabel(text='{}m'.format(file_size), size_hint=(0.1, 1.0), font_size=20)
                        file_label_layout.bind(on_touch_down=self.open_file)
                        file_label_layout.add_widget(file_path_label)
                        file_label_layout.add_widget(size_label)
                        open_dir_btn = Button(text='所在位置', size_hint=(0.1, 1.0))
                        open_dir_btn.bind(on_press=self.open_file_dir)
                        rm_btn = Button(text='删除', size_hint=(0.1, 1.0))
                        rm_btn.bind(on_press=self.remove_item_widget)

                        item_layout.add_widget(file_label_layout)
                        item_layout.add_widget(open_dir_btn)
                        item_layout.add_widget(rm_btn)
                        result_list_layout.add_widget(item_layout)
            close_btn = Button(text='关闭', size_hint=(1.0, 0.05))
            close_btn.bind(on_press=result_popup.dismiss)
            scroll_view.add_widget(result_list_layout)
            pop_main_layout.add_widget(scroll_view)
            pop_main_layout.add_widget(close_btn)
            result_popup.add_widget(pop_main_layout)
            result_popup.open()
        except Exception as e:
            self.show_error_pop_up(str(e))

    def remove_item_widget(self, instance: Button):
        layout = list(filter(lambda i: isinstance(i, BoxLayout), instance.parent.children))[0]
        label = list(filter(lambda i: isinstance(i, CustomLabel), reversed(layout.children)))[0]
        path = os.path.join(self.path_text, label.text)
        os.remove(path)
        instance.parent.parent.remove_widget(instance.parent)

    def open_file_dir(self, instance: Button):
        layout = list(filter(lambda i: isinstance(i, BoxLayout), instance.parent.children))[0]
        label = list(filter(lambda i: isinstance(i, CustomLabel), reversed(layout.children)))[0]
        file_path = os.path.join(self.path_text, label.text)
        dir_path = os.path.split(file_path)[0]
        open_file_by_default_app(dir_path)

    def open_file(self, instance, touch):
        if instance.collide_point(*touch.pos):
            label = list(filter(lambda i: isinstance(i, CustomLabel), reversed(instance.children)))[0]
            file_path = os.path.join(self.path_text, label.text)
            open_file_by_default_app(file_path)
