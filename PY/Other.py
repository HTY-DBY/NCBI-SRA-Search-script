# 读取 JSON 数据
import json
import os


def load_json_my(file_path):
	if os.path.exists(file_path):
		with open(file_path, 'r', encoding='utf-8') as f:
			return json.load(f)
	return {}
