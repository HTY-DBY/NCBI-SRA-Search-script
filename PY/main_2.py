import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from threading import Lock

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from PY.GSet import GSet
from PY.Other import load_json_my

lock = Lock()  # 锁机制避免冲突
driver_queue = Queue()  # 驱动池和队列


def init_drivers(num_drivers, head_use):
	with ThreadPoolExecutor(max_workers=num_drivers) as executor:
		for driver in executor.map(lambda _: GSet().init_driver(head_use=head_use), range(num_drivers)):
			driver_queue.put(driver)


# 从 Link_json_data 中删除与 formatted_data 重复的链接
def remove_duplicates(link_data, formatted_data):
	for compound, links in link_data.items():
		formatted_links = formatted_data.get(compound.capitalize(), [])
		# 保留不在 formatted_data 中的链接
		link_data[compound] = [link for link in links if link not in formatted_links]
	return link_data


# 定义一个获取 BioData、Library、Design 和 Study 的函数
def fetch_data(item):
	driver = driver_queue.get()
	Link = item[1]

	driver.get(Link)
	timeout_set = 4
	# 尝试获取 BioData，一定有
	try:
		elements = WebDriverWait(driver, timeout_set).until(
			EC.presence_of_all_elements_located((By.XPATH, '//*[@id="ResultView"]/table/tbody/tr/td[1]/a'))
		)
		BioData = elements[0].text if elements else None
	except Exception:
		BioData = None

	# 尝试获取 Title，一定有
	try:
		elements = WebDriverWait(driver, timeout_set).until(
			EC.presence_of_all_elements_located((By.XPATH, '//*[@id="maincontent"]/div/div[5]/p/b'))
		)
		Title = elements[0].text if elements else None
	except Exception:
		Title = None

	# 尝试获取 Library，不一定有
	try:
		elements = WebDriverWait(driver, timeout_set).until(
			EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.expand.showed.sra-full-data'))
		)
		Library = elements[0].text if elements else None
	except Exception:
		Library = None

	# 尝试获取 Design，不一定有
	try:
		elements = WebDriverWait(driver, timeout_set).until(
			EC.presence_of_all_elements_located((By.XPATH, '//*[@id="ResultView"]/div[1]/span'))
		)
		Design = elements[0].text if elements else None
	except Exception:
		Design = None

	# 尝试获取 Study，一定有
	try:
		elements = WebDriverWait(driver, timeout_set).until(
			EC.presence_of_all_elements_located((By.XPATH, '//*[@id="ResultView"]/div[3]/span'))
		)
		Study = elements[0].text.split("\n")[0] if elements else None
	except Exception:
		Study = None

	# 尝试获取 Submitted，一定有
	try:
		elements = WebDriverWait(driver, timeout_set).until(
			EC.presence_of_all_elements_located((By.XPATH, '//*[@id="ResultView"]/div[2]/span'))
		)
		Submitted = elements[0].text if elements else None
	except Exception:
		Submitted = None

	driver_queue.put(driver)  # 任务完成后将 driver 放回队列

	# 返回字典包含链接、BioData、Library、Design 和 Study
	return item[0], {"Link": Link.replace("[accn]", "").strip(), "Submitted": Submitted, "Design": Design,
					 "Study": Study, "Library": Library, "BioData": BioData, "Title": Title}


Test_do = 0
head_use = 0

# 根据条件选择 JSON 文件路径
Link_json_path = GSet().Link_json_save_test if Test_do == 1 else GSet().Link_json_save
DeepData_json_path = GSet().DeepData_json_save_test if Test_do == 1 else GSet().DeepData_json_save

# 读取 Link 和 DeepData JSON 数据
Link_json_data = load_json_my(Link_json_path)
DeepData_json_data = load_json_my(DeepData_json_path)

# 提取 DeepData 中的所有 Link
Fin_search_Link = {item['Link'] for item in DeepData_json_data.values()}  # 使用集合提高查找效率

# 使用字典推导式生成新字典，移除存在于 Fin_search_Link 中的链接
new_dict = {
	key: [link for link in links if link not in Fin_search_Link]
	for key, links in Link_json_data.items()
}

# 过滤掉没有链接的项
new_dict = {k: v for k, v in new_dict.items() if v}  # 过滤掉值为空的项

split_str = '-->'
# 生成新的字典，组合键
Link_ALL = {f'{key}{split_str}{link}': link for key, links in new_dict.items() for link in links}

total_keys = len(Link_ALL)
max_workers = 2 if Test_do == 1 else min(total_keys, os.cpu_count())
# %%
if total_keys != 0:

	print('初始化 WebDriver 中')
	init_drivers(max_workers, head_use)
	print('初始化 WebDriver 完成')

	# for search_key in new_dict:
	# 	Link_ALL = new_dict[search_key]
	# 使用线程池并行获取数据
	print(f'开始搜寻')
	results = {}
	# %%
	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		futures = {executor.submit(fetch_data, key): key for key in Link_ALL.items()}
		for i, future in enumerate(as_completed(futures), start=1):
			try:
				with lock:
					search_key, search_dict = future.result()
					results[search_key] = search_dict
				print(f"{i}/{total_keys} - {search_key} 完成")
			except Exception as e:
				print(f"错误: {futures[future]} 未成功 - {e}")
	# %%
	existing_data = load_json_my(DeepData_json_path)

	for index, item in enumerate(results.items()):
		if item[0] not in existing_data:
			existing_data[item[0]] = item[1]

	# 将更新后的数据写回 JSON 文件
	with open(DeepData_json_path, 'w', encoding='utf-8') as f:
		json.dump(existing_data, f, ensure_ascii=False, indent=4)

	print(f"数据更新到 {DeepData_json_path}")
else:
	print(f'无需更新')
