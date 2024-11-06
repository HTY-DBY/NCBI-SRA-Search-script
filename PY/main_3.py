import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from PY.GSet import GSet
from PY.Translate import translate_my

Test_do = 0

DeepData_json_save_path = GSet().DeepData_json_save_test if Test_do == 1 else GSet().DeepData_json_save

# 读取 JSON 数据
with open(DeepData_json_save_path, 'r', encoding='utf-8') as f:
	json_data = json.load(f)


# 定义翻译函数
def translate_entry(entry):
	fields = [entry['Title'], entry['Submitted'], entry['Design'], entry['Study'], entry['Library']]
	translations = translate_my(fields)
	return {
		'translated_Title': translations[0],
		'translated_Submitted': translations[1],
		'translated_Design': translations[2],
		'translated_Study': translations[3],
		'translated_Library': translations[4]
	}


# 使用线程池进行并发翻译
total_entries = len(json_data)
with ThreadPoolExecutor(max_workers=14) as executor:
	# 提交翻译任务并保存 future 对象
	futures = {executor.submit(translate_entry, entry): key for key, entry in json_data.items()}
	for i, future in enumerate(as_completed(futures), start=1):
		key = futures[future]  # 获取对应的键
		try:
			# 获取翻译结果
			translated = future.result()
			json_data[key].update(translated)
			print(f"翻译进度 {i}/{total_entries} - {json_data[key]['Title']}")  # 打印每个条目翻译完成的信息
		except Exception as e:
			print(f"错误: {key} 关键词未成功完成 - {e}")

output_file_path = GSet().Translated_json_save if Test_do == 0 else GSet().Translated_json_save_test
if os.path.exists(output_file_path):
	with open(output_file_path, 'r', encoding='utf-8') as f:
		existing_data = json.load(f)
else:
	existing_data = {}

with open(output_file_path, 'w', encoding='utf-8') as f:
	json.dump(json_data, f, ensure_ascii=False, indent=4)
print(f"数据更新到 {output_file_path}")
