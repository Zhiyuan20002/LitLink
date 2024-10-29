from django.shortcuts import render
from zhipuai import ZhipuAI
from pathlib import Path
import json

# 填写您自己的APIKey
client = ZhipuAI(api_key="99add806d43fccd92fe4bfb29f517c48.Z7YqjFR39IGwjFtb")

# 格式限制：.PDF .DOCX .DOC .XLS .XLSX .PPT .PPTX .PNG .JPG .JPEG .CSV .PY .TXT .MD .BMP .GIF
# 大小：单个文件50M、总数限制为100个文件
file_object = client.files.create(file=Path("../media/example1.pdf"), purpose="file-extract")

# 获取文本内容
file_content = json.loads(client.files.content(file_id=file_object.id).content)["content"]

# 删除文件
result = client.files.delete(
    file_id=file_object.id
)

# 生成请求消息，包含提示词和文件内容
# message_content = f"""
# 请阅读文件中的内容，并根据以下要求进行分析：
#
# 1. 识别文件中对理解整体内容至关重要的重点句子。这些句子应该帮助读者抓住文档的核心思想、重要信息、创新点、关键概念和未来研究规划。
# 2. 确保每个重点句子都是独立的，不要将多个句子合并成一个。
# 3. 论文中的创新点至关重要，一篇论文一般有若干个创新点，所有的创新点的核心句子都应该被作为重点句子。
# 4. 每个重点句子应尽量涵盖完整的思想，不宜过长或过短，尽量按照顺序提取句子。
# 5. 对于每个句子，提供一句简短的解释，说明这个句子值得注意的地方以及对理解文件内容的帮助。
# 6. 至少给出10个重点句子。
#
# 文件内容如下：
# {file_content}
#
# 输出格式要求：
# {{
#     "key_sentences": [
#     {{
#         "sentence": "这里是重点句子。",
#         "explanation": "这里是句子的解释，说明其重要性。"
#     }},
#     {{
#         "sentence": "这里是另一个重点句子。",
#         "explanation": "这里是句子的解释，说明其重要性。"
#     }}
#     // 可根据实际情况添加更多句子
#     ]
# }}
# """

message_content = f"""
Please read the contents of the document and analyze it according to the following requirements:

1. Identify key sentences in the document that are essential to understanding the overall content. These sentences should help the reader to capture the document's core ideas, important information, innovations, key concepts, and plans for future research.
2. ensure that each focused sentence stands alone and that multiple sentences are not combined into one.
3. the innovations in the paper are crucial; a paper usually has several innovations, and all the sentences that are central to the innovations should be used as focus sentences.
4. Each key sentence should try to cover the complete idea, should not be too long or too short, and try to extract the sentences in order.
5. For each sentence, provide a short explanation of what is noteworthy about the sentence and how it contributes to the understanding of the content of the document.
6. Give at least 10 key sentences.

The content of the file is as follows:
{file_content}

Output formatting requirements:
{{
    "key_sentences": [
    {{
        "number": 1
        "sentence": "Here are the key sentences." ,
        "explanation": "Here is the explanation of the sentence, explaining its importance."
    }},
    {{
        "number": 2
        "sentence": "Here is another focused sentence." ,
        "explanation": "Here is an explanation of the sentence that shows its importance."
    }}
        // More sentences can be added as appropriate
    ]
}}
"""

# # 向模型发送请求并获取响应
# response = client.chat.completions.create(
#     model="glm-4-flash:1226531186:litlink1:z4mhitwv",
#     # model="glm-4-airx:1226531186:litlink2:r6eaqpsr",
#     # model='glm-4-flash',
#     # model="glm-4-long",
#
#     messages=[
#         {"role": "user", "content": message_content}
#     ],
# )
#
# # 获取并打印模型的响应内容
# result = response.choices[0].message.content
# print(result)

response = client.chat.completions.create(
    model="glm-4",  # 请填写您要调用的模型名称
    messages=[
        {"role": "system", "content": "你是一个乐于回答各种问题的小助手，你的任务是提供专业、准确、有洞察力的建议。"},
        {"role": "user",
         "content": "我对太阳系的行星非常感兴趣，尤其是土星。请提供关于土星的基本信息，包括它的大小、组成、环系统以及任何独特的天文现象。"},
    ],
    stream=True,
)
for chunk in response:
    print(chunk.choices[0].delta.content, end="")
