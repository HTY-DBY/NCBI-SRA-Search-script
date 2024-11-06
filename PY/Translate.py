from typing import List

import torch
from transformers import MarianMTModel, MarianTokenizer

# 检查是否有可用的GPU，并设置设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 加载模型和分词器
model_name = 'Helsinki-NLP/opus-mt-en-zh'
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name).to(device)  # 将模型移到GPU


def translate_my(texts: List[str]) -> List[str]:
	"""
	翻译文本列表。

	:param texts: 要翻译的文本列表
	:return: 翻译后的文本列表
	"""
	texts = [text if text is not None else '' for text in texts]

	try:
		# 编码输入文本
		inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True).to(device)  # 将输入移到GPU
		translated = model.generate(**inputs)  # 翻译
		# 解码翻译结果
		translated_texts = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
		return translated_texts
	except Exception as e:
		print(f"翻译时出现错误: {e}")
		return []


if __name__ == "__main__":
	# 要翻译的文本
	texts = ["you are a good man", "Hello, how are you?", "This is a test."]
	translated_texts = translate_my(texts)

	# 输出翻译结果
	for original, translated in zip(texts, translated_texts):
		print(f"原文: {original} -> 翻译: {translated}")
