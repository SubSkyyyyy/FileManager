from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout

class BaseScreen(Screen):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.main_layout = BoxLayout(orientation='vertical')
		self.prepare_widgets()
		self.add_widget(self.main_layout)

	def prepare_widgets(self):
		pass

	def add_widgets(self, parent_widget: Widget, children_widgets: list):
		for children_widget in children_widgets:
			parent_widget.add_widget(children_widget)
