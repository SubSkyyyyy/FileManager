from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from common.widgets import CustomLabel
from views.basescreen import BaseScreen

class FileManageScreen(BaseScreen):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def prepare_widgets(self):
		input_layout = BoxLayout(orientation='horizontal', size_hint=(1.0, 0.1))
		path_label = CustomLabel(size_hint=(0.1, 1.0), text='路径:')
		self.path_input = TextInput(size_hint=(0.5, 1.0))
		keyword_label = CustomLabel(size_hint=(0.1, 1.0), text='关键字:')
		self.keyword_input = TextInput(size_hint=(0.1, 1.0))
		param_label = CustomLabel(size_hint=(0.1, 1.0), text='参数:')
		self.param_input = TextInput(size_hint=(0.1, 1.0))

		self.add_widgets(input_layout, [path_label, self.path_input, keyword_label, self.keyword_input, param_label, self.param_input])

		move_block_layout = BoxLayout(orientation='vertical', size_hint=(1.0, 0.3))
		move_title = CustomLabel(size_hint=(1.0, 0.3), text='移动操作')
		move_option_layout = BoxLayout(orientation='horizontal', size_hint=(1.0, 0.7))
		self.move_to_up_btn = Button(text='移动到上一层(可重命名)', size_hint=(0.2, 1.0))
		self.move_to_target_btn = Button(text='移动到指定目录', size_hint=(0.2, 1.0))
		self.add_widgets(move_option_layout, [self.move_to_up_btn, self.move_to_target_btn])
		self.add_widgets(move_block_layout, [move_title, move_option_layout])

		rename_block_layout = BoxLayout(orientation='vertical', size_hint=(1.0, 0.3))
		rename_title = CustomLabel(size_hint=(1.0, 0.3), text='重命名')
		rename_option_layout = BoxLayout(orientation='horizontal', size_hint=(1.0, 0.7))
		self.rename_to_upper_btn = Button(text='文件名转大写', size_hint=(0.2, 1.0))
		self.rename_to_lower_btn = Button(text='文件名转小写', size_hint=(0.2, 1.0))
		self.rename_to_target_format_btn = Button(text='文件名正则替换', size_hint=(0.2, 1.0))
		self.rename_to_add_suffix_prefix_btn = Button(text='文件名加前后缀', size_hint=(0.2, 1.0))
		self.add_widgets(rename_option_layout, [self.rename_to_upper_btn, self.rename_to_lower_btn, self.rename_to_target_format_btn, self.rename_to_add_suffix_prefix_btn])
		self.add_widgets(rename_block_layout, [rename_title, rename_option_layout])


		search_block_layout = BoxLayout(orientation='vertical', size_hint=(1.0, 0.3))
		search_title = CustomLabel(size_hint=(1.0, 0.3), text='重命名')
		search_option_layout = BoxLayout(orientation='horizontal', size_hint=(1.0, 0.7))
		self.search_by_re = Button(text='正则查找', size_hint=(0.2, 1.0))
		self.search_by_time = Button(text='视频时长查找', size_hint=(0.2, 1.0))
		self.search_by_same_time = Button(text='相同时长视频', size_hint=(0.2, 1.0))
		self.search_by_same_size = Button(text='相同大小文件', size_hint=(0.2, 1.0))
		self.add_widgets(search_option_layout, [self.search_by_re, self.search_by_time, self.search_by_same_time, self.search_by_same_size])
		self.add_widgets(search_block_layout, [search_title, search_option_layout])

		self.roll_back_btn = Button(text='回退', size_hint=(1.0, 0.1))
		self.add_widgets(self.main_layout, [input_layout, move_block_layout, rename_block_layout, search_block_layout, self.roll_back_btn])





