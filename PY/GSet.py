import os.path

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class GSet:
	def __init__(self):
		self.my_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		self.Data_temp = os.path.join(self.my_path, 'Data', 'Data_temp')
		self.Data_fin = os.path.join(self.my_path, 'Data', 'Data_fin')

		self.Link_json_save = os.path.join(self.Data_temp, 'Link_results.json')
		self.Link_json_save_test = os.path.join(self.Data_temp, 'Link_results_test.json')

		self.DeepData_json_save = os.path.join(self.Data_temp, 'DeepData_results.json')
		self.DeepData_json_save_test = os.path.join(self.Data_temp, 'DeepData_results_test.json')

		self.Translated_json_save = os.path.join(self.Data_temp, 'Translated_results.json')
		self.Translated_json_save_test = os.path.join(self.Data_temp, 'Translated_results_test.json')

		self.Keys_save = os.path.join(self.my_path, 'Keys_ALL.xlsx')
		self.Keys_save_test = os.path.join(self.my_path, 'Keys_ALL_test.xlsx')

	# 初始化浏览器的设置
	def init_driver(self, head_use=1):
		options = Options()
		if head_use == 0: options.add_argument("--headless")  # 无头模式
		# options.add_argument("--disable-gpu")  # 禁用 GPU 加速（有时会提高稳定性）
		options.add_argument("--no-sandbox")  # 防止沙盒问题（在某些系统上可能需要）

		# 创建 Edge 服务
		edge_service = EdgeService(EdgeChromiumDriverManager().install())
		driver = webdriver.Edge(service=edge_service, options=options)
		return driver


def GSet_init():
	return GSet()
