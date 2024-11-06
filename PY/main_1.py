import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from threading import Lock

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from GSet import GSet

lock = Lock()  # 锁机制避免冲突
driver_queue = Queue()  # 驱动池和队列


def init_drivers(num_drivers, head_use):
	with ThreadPoolExecutor(max_workers=num_drivers) as executor:
		for driver in executor.map(lambda _: GSet().init_driver(head_use=head_use), range(num_drivers)):
			driver_queue.put(driver)


def find_links_for_search_key(search_key):
	# 从队列中获取一个可用的 driver
	driver = driver_queue.get()
	driver.get(f'https://www.ncbi.nlm.nih.gov/sra/?term={search_key}')
	timeout_set = 4
	Link_ALL = []

	def find_link():
		title_elements = WebDriverWait(driver, timeout_set).until(
			EC.presence_of_all_elements_located((By.CLASS_NAME, "title"))
		)
		for title_element in title_elements:
			Link_element = title_element.find_element(By.TAG_NAME, "a")
			Link = Link_element.get_attribute("href").replace("[accn]", "").strip()
			Link_ALL.append(Link)

	try:
		input_element = WebDriverWait(driver, timeout_set).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="pageno"]'))
		)
		max_page = input_element.get_attribute("last")

		for page in range(int(max_page)):
			print(f'{search_key}: {page + 1}/{max_page} 页')
			input_element = WebDriverWait(driver, timeout_set).until(
				EC.presence_of_element_located((By.XPATH, '//*[@id="pageno"]'))
			)
			input_element.clear()
			input_element.send_keys(str(page + 1))
			input_element.send_keys(Keys.RETURN)
			find_link()
	except Exception:
		find_link()

	print(f'{search_key} 共 {len(Link_ALL)} 个数据')
	driver_queue.put(driver)  # 任务完成后将 driver 放回队列
	return search_key, Link_ALL


Test_do = 0
head_use = 0
results = {}

Keys_save_path = GSet().Keys_save if Test_do == 0 else GSet().Keys_save_test

keys_data = pd.read_excel(GSet().Keys_save, header=0)['Need keys'].dropna().values
Keys_ALL = (
	['tetrachloromethane', 'trichloromethane', 'DCE'] if Test_do == 1
	else [str(key) for key in keys_data]
)
total_keys = len(Keys_ALL)
max_workers = 2 if Test_do == 1 else min(total_keys, os.cpu_count())

print('初始化 WebDriver 中')
init_drivers(max_workers, head_use)
print('初始化 WebDriver 完成')

with ThreadPoolExecutor(max_workers=max_workers) as executor:
	futures = {executor.submit(find_links_for_search_key, key): key for key in Keys_ALL}
	for i, future in enumerate(as_completed(futures), start=1):
		try:
			with lock:
				search_key, links = future.result()
				results[search_key] = links
			print(f"{i}/{total_keys} - {search_key} 完成")
		except Exception as e:
			print(f"错误: {futures[future]} 关键词未成功完成 - {e}")

# 关闭所有 WebDriver 实例
while not driver_queue.empty():
	driver = driver_queue.get()
	driver.quit()

output_file = GSet().Link_json_save
if os.path.exists(output_file):
	with open(output_file, 'r', encoding='utf-8') as f:
		existing_data = json.load(f)
else:
	existing_data = {}

for pollutant, new_data in results.items():
	if pollutant in existing_data:
		existing_data[pollutant].extend(new_data)
	else:
		existing_data[pollutant] = new_data

for pollutant in existing_data:
	existing_data[pollutant] = list(set(existing_data[pollutant]))

with open(output_file, 'w', encoding='utf-8') as f:
	json.dump(existing_data, f, ensure_ascii=False, indent=4)

print(f"数据更新到 {output_file}")
