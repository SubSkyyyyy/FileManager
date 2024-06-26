from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox

from common.widgets import CustomLabel
from popup_widgets.OperationPopup import OperationPopup
from file_operation.file_rename import file_rename, file_suffix_change, rename_roll_back
from common.config import BIG_SIZE, NORMAL_SIZE, SMALL_SIZE


class FileRenamePopup(OperationPopup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = '文件重命名'
        self.roll_back_able = True

    def prepare_widgets(self):
        self.widget_list = []

        input_box_layout = BoxLayout(orientation='horizontal', size_hint=(1.0, 0.35))
        origin_pattern_label = CustomLabel(text='匹配文件名', size_hint=(0.2, 1.0), halign='center', valign='center')
        self.origin_pattern_input = TextInput(size_hint=(0.3, 1.0), font_size=NORMAL_SIZE)
        replace_pattern_label = CustomLabel(text='替换字符', size_hint=(0.2, 1.0), halign='center', valign='center')
        self.replace_pattern_input = TextInput(size_hint=(0.3, 1.0), font_size=NORMAL_SIZE)
        input_box_layout.add_widget(origin_pattern_label)
        input_box_layout.add_widget(self.origin_pattern_input)
        input_box_layout.add_widget(replace_pattern_label)
        input_box_layout.add_widget(self.replace_pattern_input)

        self.replace_option_dict = {
            '主文件名替换': 'main_file_name_replace',
            '文件名后缀替换': 'file_suffix_replace'
        }
        self.replace_option_radio = []
        for radio_text in self.replace_option_dict:
            toggle = ToggleButton(group='rename_option_choice', text=radio_text)
            toggle.bind(on_release=self.on_toggle_btn_release, on_press=self.on_toggle_btn_press)
            self.replace_option_radio.append(toggle)
        else:
            self.replace_option_radio[0].state = 'down'

        option_file_checkboxes = BoxLayout(orientation='horizontal', size_hint=(1.0, 0.2))
        dir_label = CustomLabel(text='文件夹名称替换', halign='center')
        self.dir_checkbox = CheckBox(size_hint=(0.2, 1.0))
        file_label = CustomLabel(text='文件名替换', halign='center')
        self.file_checkbox = CheckBox(size_hint=(0.2, 1.0))
        self.check_box_dict = {
            '文件名替换': self.file_checkbox,
            '文件夹名称替换': self.dir_checkbox
        }
        self.dir_checkbox.active = True
        self.file_checkbox.active = True
        self.bind_label_with_checkbox(dir_label)
        self.bind_label_with_checkbox(file_label)

        option_file_checkboxes.add_widget(dir_label)
        option_file_checkboxes.add_widget(self.dir_checkbox)
        option_file_checkboxes.add_widget(file_label)
        option_file_checkboxes.add_widget(self.file_checkbox)

        self.widget_list.append(input_box_layout)
        for toggle in self.replace_option_radio:
            self.widget_list.append(toggle)
        self.widget_list.append(option_file_checkboxes)

    def get_params(self):
        if not self.path_text:
            raise Exception('未输入根目录路径!')
        origin_pattern = self.origin_pattern_input.text
        target_format = self.replace_pattern_input.text
        option_selected = list(filter(lambda i: i.state == 'down', self.replace_option_radio))[0]
        replace_dir_name = self.dir_checkbox.active
        replace_file_name = self.file_checkbox.active
        return origin_pattern, target_format, option_selected.text, replace_dir_name, replace_file_name

    def press_enter(self):
        origin_pattern, target_format, opt, to_replace_dir_name, to_replace_file_name = self.get_params()
        try:
            if self.replace_option_dict[opt] == 'main_file_name_replace':
                file_rename(self.path_text, origin_pattern, target_format, to_replace_dir_name, to_replace_file_name)
            else:
                file_suffix_change(self.path_text, origin_pattern, target_format)
            self.show_finish_pop_up('重命名完成')
        except Exception as e:
            self.show_error_pop_up(str(e))

    def press_roll_back(self, instance):
        try:
            origin_pattern, target_format, opt, to_replace_dir_name, to_replace_file_name = self.get_params()
            rename_roll_back(self.path_text, origin_pattern, target_format)
            self.show_finish_pop_up('回退完成')
        except Exception as e:
            self.show_error_pop_up(str(e))

    def on_toggle_btn_press(self, instance):
        if self.replace_option_dict[instance.text] == 'main_file_name_replace':
            self.check_box_dict['文件名替换'].active = True
            self.check_box_dict['文件夹名称替换'].active = True
        else:
            self.check_box_dict['文件名替换'].active = True
            self.check_box_dict['文件夹名称替换'].active = False
