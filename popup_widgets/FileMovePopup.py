from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.checkbox import CheckBox

from common.config import RE_PATTERN
from common.widgets import CustomLabel
from popup_widgets.OperationPopup import OperationPopup
from file_operation.file_move import move_file, file_move_roll_back


class FileMovePopup(OperationPopup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.roll_back_able = True
        self.title = '文件移动'

    def prepare_widgets(self):
        # 输入行
        input_box = BoxLayout(orientation='horizontal', size_hint=(1.0, 0.35))
        origin_name_label = CustomLabel(text='源文件匹配', size_hint=(0.1, 1.0), font_size=20)
        self.origin_name_pattern_input = TextInput(size_hint=(0.3, 1.0), font_size=20)
        self.origin_name_pattern_input.bind(text=self.on_pattern_text_input_change)
        pattern_choices = ['视频', '图片']
        self.pattern_choice_radio = []
        for choice in pattern_choices:
            choice_radio = ToggleButton(text=choice, group='file_type_pattern', size_hint=(0.2 / len(pattern_choices), 1.0), font_size=18)
            choice_radio.bind(on_press=self.on_pattern_radio_press)
            self.pattern_choice_radio.append(choice_radio)

        target_name_label = CustomLabel(text='目标目录', size_hint=(0.1, 1.0), font_size=20)
        self.target_name_input = TextInput(size_hint=(0.3, 1.0))

        rename_with_parent_dir_label = CustomLabel(text='使用父目录名称', font_size=20, size_hint=(0.15, 1.0))
        self.rename_with_parent_dir_checkbox = CheckBox(size_hint=(0.05, 1.0))
        self.check_box_dict['使用父目录名称'] = self.rename_with_parent_dir_checkbox
        self.bind_label_with_checkbox(rename_with_parent_dir_label)

        # 将输入行的控件添加到input_box中
        input_box.add_widget(origin_name_label)
        input_box.add_widget(self.origin_name_pattern_input)
        for choice in self.pattern_choice_radio:
            input_box.add_widget(choice)
        input_box.add_widget(target_name_label)
        input_box.add_widget(self.target_name_input)
        input_box.add_widget(rename_with_parent_dir_label)
        input_box.add_widget(self.rename_with_parent_dir_checkbox)

        self.move_up = '移动各级目录的匹配文件到上级目录'
        self.move_to_target = '移动各级目录的匹配文件到搜索目录的指定路径'
        self.move_to_parent_folder = '移动各级目录的匹配文件到上级目录下的指定文件夹'
        self.move_single_file_to_parent_folder = '将各级目录下的单个文件移动到其父目录并重命名'

        self.opt_dict = {
            self.move_up: 'move_up',
            self.move_to_target: 'move_to_target',
            self.move_to_parent_folder: 'move_to_parent_folder',
            self.move_single_file_to_parent_folder: 'move_single_file_to_parent_folder'
        }

        height = 0.6
        # 操作按钮
        t_btn = ToggleButton(text=self.move_up, group='g1', state='down', size_hint=(1.0, height))
        t_btn.bind(on_release=self.on_toggle_btn_release, on_press=self.on_toggle_btn_press)

        t_btn2 = ToggleButton(text=self.move_to_target, group='g1', size_hint=(1.0, height))
        t_btn2.bind(on_release=self.on_toggle_btn_release, on_press=self.on_toggle_btn_press)

        t_btn3 = ToggleButton(text=self.move_to_parent_folder, group='g1', size_hint=(1.0, height))
        t_btn3.bind(on_release=self.on_toggle_btn_release, on_press=self.on_toggle_btn_press)

        t_btn4 = ToggleButton(text=self.move_single_file_to_parent_folder, group='g1', size_hint=(1.0, height))
        t_btn4.bind(on_release=self.on_toggle_btn_release, on_press=self.on_toggle_btn_press)

        self.operation_toggle = [t_btn, t_btn2, t_btn3, t_btn4]

        # 将所有控件添加到widget_list中
        self.widget_list.append(input_box)
        self.widget_list.append(t_btn)
        self.widget_list.append(t_btn2)
        self.widget_list.append(t_btn3)
        self.widget_list.append(t_btn4)

    def on_pattern_radio_press(self, instance):
        self.origin_name_pattern_input.text = RE_PATTERN.get(instance.text, '')

    def on_pattern_text_input_change(self, instance, value):
        Clock.schedule_once(lambda dt: self.change_radio_status(), 0)

    def change_radio_status(self):
        for choice in self.pattern_choice_radio:
            if self.origin_name_pattern_input.text == RE_PATTERN.get(choice.text, ''):
                choice.state = 'down'
            else:
                choice.state = 'normal'

    def get_params(self):
        if not self.path_text:
            raise Exception('未输入根目录路径!')
        selected_radio = list(filter(lambda i: i.state == 'down', self.operation_toggle))
        if selected_radio:
            selected_radio = selected_radio[0]
        else:
            raise Exception('未选择要进行的操作!')
        if selected_radio.text != self.move_single_file_to_parent_folder and not self.origin_name_pattern_input.text:
            raise Exception('需要输入正则表达式!')
        if selected_radio.text in [self.move_to_target, self.move_to_parent_folder] and not self.target_name_input.text:
            raise Exception('需要输入目标路径的名称!')

        # 获取参数
        re_pattern = self.origin_name_pattern_input.text
        with_parent_dir_name = self.rename_with_parent_dir_checkbox
        target_path = self.target_name_input.text
        return selected_radio.text, target_path, re_pattern, with_parent_dir_name.active

    def press_enter(self):
        try:
            option_str, target_parth, re_pattern, with_parent_name = self.get_params()
            move_file(self.path_text, re_pattern, self.opt_dict[option_str], target_folder=target_parth, with_parent_name=with_parent_name)
            self.show_finish_pop_up('移动完成')
        except Exception as e:
            self.show_error_pop_up(e)

    def press_roll_back(self, instance):
        try:
            option_str, target_folder, re_pattern, with_parent_name = self.get_params()
            opt_str = self.opt_dict[option_str]
            file_move_roll_back(self.path_text, re_pattern, opt_str)
            self.show_finish_pop_up('回退完成')
        except Exception as e:
            self.show_error_pop_up(str(e))

    def on_toggle_btn_press(self, instance):
        if instance.text == self.move_single_file_to_parent_folder:
            self.rename_with_parent_dir_checkbox.active = True
            self.rename_with_parent_dir_checkbox.disabled = True
        else:
            self.rename_with_parent_dir_checkbox.active = False
            self.rename_with_parent_dir_checkbox.disabled = False
