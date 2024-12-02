import os
from itertools import groupby
from operator import attrgetter
from popup_widgets.OperationPopup import OperationPopup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior

from common.widgets import CustomLabel

from file_operation.file_search import file_search
from common.utils import open_file_by_default_app, open_file_in_dir
from common.config import NORMAL_SIZE, BIG_SIZE, SMALL_SIZE
from model.FileInfoModel import FileInfo

class FileSearchPopup(OperationPopup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = '文件搜索'

    def prepare_widgets(self):
        input_layout = BoxLayout(orientation='horizontal', size_hint=(1.0, 0.3))
        input_label = CustomLabel(text='关键字', font_size=BIG_SIZE, size_hint=(0.1, 1.0), valign='center', halign='center')
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
            tg = ToggleButton(group='search', text=key, size_hint=(1.0, 0.5), font_size=BIG_SIZE)
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
            result_list = file_search(self.path_text, self.opt_dict[opt], text_input)
            result_popup = Popup(title='搜索结果', title_size=30)
            pop_main_layout = BoxLayout(orientation='vertical')
            scroll_view = LazyScrollView(size_hint=(1.0, 0.95), do_scroll_x=False, do_scroll_y=True,
                                     bar_width=10, bar_color=[0.75, 0.75, 0.75, 1],
                                     bar_inactive_color=[0.5, 0.5, 0.5, 1], scroll_wheel_distance=120,
                                     bar_pos_y='right', scroll_type=['bars'])
            if opt in [self.search_by_key, self.search_by_spent]:
                result_groups = groupby(result_list, key=lambda x: '搜索结果')
            else:
                if opt == self.search_by_same_spent:
                    sorted_results = sorted(result_list, key=attrgetter('duration', 'file_size'))
                    group_key = 'duration'
                elif opt == self.search_by_same_size:
                    sorted_results = sorted(result_list, key=attrgetter('file_size'))
                    group_key = 'file_size'
                result_groups = groupby(sorted_results, key=attrgetter(group_key))
            for title, items in result_groups:
                items = list(items)
                if opt in [self.search_by_same_spent, self.search_by_same_size] and len(items) < 2:
                    continue
                item_label = CustomLabel(text=str(title), font_size=30, size_hint_y=None, height=120, halign='center', valign='center')
                scroll_view.add_lazy_item(item_label)
                # result_list_layout.add_widget(item_label)
                for item in items:
                    item_widget = LazyItem(item, self.path_text)
                    scroll_view.add_lazy_item(item_widget)

            close_btn = Button(text='关闭', size_hint=(1.0, 0.05), font_size=BIG_SIZE)
            close_btn.bind(on_press=result_popup.dismiss)

            scroll_view.on_scroll()
            pop_main_layout.add_widget(scroll_view)
            pop_main_layout.add_widget(close_btn)
            result_popup.add_widget(pop_main_layout)
            result_popup.open()
        except Exception as e:
            self.show_error_pop_up(str(e))


class LazyImage(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loaded = False  # 是否已加载图片
        self.release_image()  # 初始化时释放资源

    def load_image(self, source_path):
        if not self.loaded:
            self.source = source_path
            self.reload()
            self.loaded = True

    def release_image(self):
        if self.loaded:
            self.source = ""
            self.loaded = False


class LazyItem(BoxLayout):
    def __init__(self, file_obj: FileInfo, base_path: str, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=100, **kwargs)
        self.file_obj = file_obj
        # self.img_widget = None
        self.base_path = base_path
        self.img_widget = LazyImage(size_hint=(0.2, 1.0))
        self.file_path_widget = CustomLabel(text=file_obj.path.replace(base_path, '').strip('\\'), size_hint=(0.8, 1.0), font_size=BIG_SIZE)
        self.file_size_widget = CustomLabel(text='{}m'.format(round(file_obj.file_size / 1024 / 1024, 2)), size_hint=(0.1, 1.0), font_size=NORMAL_SIZE)

        self.refactor_widget = Button(text="修改", size_hint=(0.1, 1.0), font_size=NORMAL_SIZE)
        self.find_path_widget = Button(text="位置", size_hint=(0.1, 1.0), font_size=NORMAL_SIZE)
        self.delete_widget = Button(text='删除', size_hint=(0.1, 1.0), font_size=NORMAL_SIZE)

        self.file_path_widget.bind(on_touch_down=self.open_file)
        self.refactor_widget.bind(on_press=self.refactor_file)
        self.find_path_widget.bind(on_press=self.open_file_dir)
        self.delete_widget.bind(on_press=self.remove_item)

        self.img_widget.bind(on_press=self.open_big_img)
        self.add_widget(self.img_widget)
        self.add_widget(self.file_path_widget)
        self.add_widget(self.file_size_widget)
        self.add_widget(self.refactor_widget)
        self.add_widget(self.find_path_widget)
        self.add_widget(self.delete_widget)

    def load_resources(self):
        if self.file_obj.thumbnail:
            self.img_widget.load_image(self.file_obj.thumbnail)
        else:
            self.img_widget.unbind(self.open_big_img)

    def release_resources(self):
        self.img_widget.release_image()

    def open_big_img(self, instance):
        open_file_by_default_app(self.file_obj.image_path)

    def open_file_dir(self, instance: Button):
        open_file_in_dir(self.file_obj.path)

    def remove_item(self, instance: Button):
        os.remove(self.file_obj.path)
        instance.parent.parent.remove_widget(instance.parent)

    def open_file(self, instance, touch):
        if instance.collide_point(*touch.pos):
            open_file_by_default_app(self.file_obj.path)

    def refactor_file(self, instance):
        if instance.text == '修改':
            self.file_path_widget.unbind(on_touch_down=self.open_file)
            self.file_path_widget.reset_widget()
            instance.text = '确认'
        else:
            self.file_path_widget.bind(on_touch_down=self.open_file)
            self.file_path_widget.set_widget()
            instance.text = '修改'
            new_path = os.path.join(self.base_path, self.file_path_widget.text)
            self.file_obj.refactor(new_path)


class LazyScrollView(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.image_layout.bind(minimum_height=self.image_layout.setter('height'))
        self.add_widget(self.image_layout)  # 确保 ScrollView 只有一个子控件

        self.items = []  # 存储所有 Item
        self.bind(scroll_y=self.on_scroll)

    def add_lazy_item(self, item):
        self.items.append(item)
        self.image_layout.add_widget(item)

    def on_scroll(self, *args):

        for item in self.items:
            if not item.parent or isinstance(item, CustomLabel):  # 跳过未挂载的控件
                continue

            # 获取 Item 的位置和尺寸
            right, item_top = item.to_window(item.x, item.y)
            item_bottom = item_top + item.height

            # 判断 Item 是否在可视区域内
            if (item_bottom > 0 and item_bottom < Window.height) or (item_top > 0 and item_top < Window.height):
                item.load_resources()  # 加载资源
            else:
                item.release_resources()  # 释放资源
