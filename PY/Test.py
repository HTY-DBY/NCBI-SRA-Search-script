from typing import List

from transformers import MarianMTModel, MarianTokenizer

# 加载模型和分词器
model_name = 'Helsinki-NLP/opus-mt-en-zh'
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)


def translate(texts: List[str]) -> List[str]:
	"""
	翻译文本列表。

	:param texts: 要翻译的文本列表
	:return: 翻译后的文本列表
	"""
	try:
		# 编码输入文本
		inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
		translated = model.generate(**inputs)  # 翻译
		# 解码翻译结果
		translated_texts = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
		return translated_texts
	except Exception as e:
		print(f"翻译时出现错误: {e}")
		return []


# 要翻译的文本
texts = ["you are a good man", "Hello, how are you?", "This is a test."]
translated_texts = translate(texts)
