from django.shortcuts import render
from zhipuai import ZhipuAI
from pathlib import Path
import json

client_zp = ZhipuAI(api_key="f3478448c98f521a5029ea6cbde7ecd0.JoYoUgsBLMflLhcM")


def upload_process(file_url):
    file_object = client_zp.files.create(file=Path(file_url), purpose="file-extract")
    file_content = json.loads(client_zp.files.content(file_id=file_object.id).content)["content"]
    client_zp.files.delete(file_id=file_object.id)

    # 标题生成
    yield "{StartTitle}"
    response_name = client_zp.chat.completions.create(model='glm-4-flash', messages=[
        {"role": "user", "content": file_content},
        {"role": "user", "content": "请为这篇论文生成一个简短的英文标题，直接输出内容即可，不要有多余的描述或符号。"}
    ], stream=True)

    for chunk in response_name:
        content = chunk.choices[0].delta.content.replace('*', '')
        yield content

    # 简要概括生成
    yield "{StartContent}"
    response_detail = client_zp.chat.completions.create(model='glm-4-flash', messages=[
        {"role": "user", "content": file_content},
        {"role": "user", "content": "请用简短的一句话（使用英文）概括论文，直接输出内容即可，不要有多余的描述或符号。"}
    ], stream=True)

    for chunk in response_detail:
        content = chunk.choices[0].delta.content.replace('*', '')
        yield content

    # 摘要生成
    yield "{StartSummary}"
    response_summary = client_zp.chat.completions.create(model='glm-4-flash', messages=[
        {"role": "user", "content": file_content},
        {"role": "user",
         "content": "请生成一段论文的英文摘要，说明论文的主要内容和创新点，直接输出摘要的正文内容即可，不要有多余的描述或符号。"}
    ], stream=True)

    for chunk in response_summary:
        content = chunk.choices[0].delta.content.replace('*', '')
        yield content

    # 生成完成通知
    yield "{Done}"
    print("INFO: Auto Fill, AI 生成完成")


def generate_avatar(content):
    response = client_zp.images.generations(
        model="cogView-3-plus",
        prompt="生成一个头像，头像的内容是：" + content,  # 填写生成头像的文本提示
    )
    return response.data[0].url


def new_flashcard(file_url):
    file_object = client_zp.files.create(file=Path(file_url), purpose="file-extract")
    file_content = json.loads(client_zp.files.content(file_id=file_object.id).content)["content"]
    client_zp.files.delete(file_id=file_object.id)

    # 生成请求消息，包含提示词和文件内容
    message_content = f"""
    请阅读文件中的内容，并根据以下要求进行分析：

    1. 识别文件中对理解整体内容至关重要的重点句子。这些句子应该帮助读者抓住文档的核心思想、重要信息、创新点、关键概念和未来研究规划。
    2. 论文中的创新点至关重要，一篇论文一般有若干个创新点，所有的创新点的核心句子都应该被作为重点句子。
    3. 每个重点句子应尽量涵盖完整的思想，不宜过长或过短，尽量按照顺序提取句子。
    4. 对于每个句子，提供一句简短的解释，说明这个句子值得注意的地方以及对理解文件内容的帮助。
    5. 给且仅给出5个最重要的句子，确保给出的句子是与原文对应部分完全相同的内容。

    文件内容如下：
    {file_content}

    输出格式要求：
    {{
        "key_sentences": [
        {{
            "title": "这里是重点句子的标题，应该简单的用英语概括这个重点句子",
            "content": "这里是重点句子，和原文内容保持完全一致。",
            "ai_analysis": "这里是对句子的分析，使用英文说明为什么要选择这个句子为重点句子。"
        }},
        {{
            "title": "这里是重点句子的标题，应该简单的用英语概括这个重点句子",
            "content": "这里是重点句子，和原文内容保持完全一致。",
            "ai_analysis": "这里是对句子的分析，使用英文说明为什么要选择这个句子为重点句子。"
        }},
        // 可根据实际情况添加更多句子
        ]
    }}
    
    注意：直接输出 JSON 格式的数据即可，不需要包含其他内容。
    """

    response = client_zp.chat.completions.create(
        model="glm-4-air:1226531186:litlink3:kxjrtwmp",
        messages=[
            {"role": "user", "content": message_content}
        ],
    )

    print("INFO: Flashcard, AI 生成完成")
    flashcard_content = response.choices[0].message.content.strip()
    flashcard_content = flashcard_content.replace("```json", "").replace("```", "").strip()

    return json.loads(flashcard_content)


def get_embeddings(sentence):
    response = client_zp.embeddings.create(
        model="embedding-3",
        input=sentence,
        dimensions=256,
    )
    result = response.data[0].embedding
    print("INFO: Embedding, 获取到的句子向量为：", result)
    return result
