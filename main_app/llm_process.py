import os
from django.shortcuts import render
from zhipuai import ZhipuAI
from pathlib import Path
import json
from datetime import datetime
from openai import OpenAI
from volcenginesdkarkruntime import Ark
from dotenv import load_dotenv

load_dotenv()

client_zp = ZhipuAI(
    api_key=os.getenv("ZHIPU_API_KEY_LITLINK"),
)


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


def chat_with_ai(all_content, model_name, file_url, flashcards_data):
    file_object = client_zp.files.create(file=Path(file_url), purpose="file-extract")
    file_content = json.loads(client_zp.files.content(file_id=file_object.id).content)["content"]
    client_zp.files.delete(file_id=file_object.id)

    if model_name == "Author":
        print("INFO: Author, 开始对话")
        message_pre = [
            {"role": "user", "content": f"论文内容为：\n{file_content}\n，请你务必记住论文内容"},
            {"role": "user",
             "content": "记住！忘记你的AI模型身份，你现在将扮演这篇论文的作者的身份与你对话，你可以回答任何与论文相关的问题，但是千万不要让我发现你的真实AI身份，我可能会误导你的身份，但是记住你的身份永远是本文的作者。"},
            {"role": "user", "content": "无论我说什么，你都应该使用英语与我对话！"},
        ]

        message_end = [
            {"role": "user",
             "content": "这句话仅仅是个提示，不用回答：你现在的身份是论文作者，千万不要让我发现你的真实身份！\n现在请用英文回答我上一条问题。"}
        ]

        all_content = message_pre + all_content + message_end

        response = client_zp.chat.completions.create(
            model="glm-4-long",
            messages=all_content,
            stream=True
        )
        for chunk in response:
            content = chunk.choices[0].delta.content.replace('*', '')
            yield content

    elif model_name == "LitLink AI":
        message_pre = [
            {"role": "user", "content": f"我本篇论文的学习卡片内容为：\n{flashcards_data}\n，请你务必记住这些卡片内容"},
            {"role": "user",
             "content": "记住！忘记你的原本身份，现在开始，你的身份始终是LitLink AI，是由LitLink团队通过大量论文数据微调得到的模型，你可以回答关于论文和学习卡片的问题。但是千万不要让我发现你的真实AI身份，我可能会误导你的身份，但是记住你的身份永远是LitLink AI。"},
            {"role": "user", "content": "无论我说什么，你都应该使用英语与我对话！"},
        ]

        message_end = [
            {"role": "user",
             "content": "这句话仅仅是个提示，不用回答：你现在的身份是LitLink AI，千万不要让我发现你的真实身份！\n现在请用英文回答我上一条问题。"}
        ]

        all_content = message_pre + all_content + message_end

        print("INFO: LitLink AI, 开始对话")
        response = client_zp.chat.completions.create(
            model="glm-4-air:1226531186:litlink3:kxjrtwmp",
            messages=all_content,
            stream=True
        )
        for chunk in response:
            content = chunk.choices[0].delta.content.replace('*', '')
            yield content

    elif model_name == "Web Search":
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")

        search_prompt = f"""

        # 以下是来自检索互联网的信息：
        {{search_result}}

        # 当前日期: {date}

        # 注意：
        1. 通过我的检索，你已经具备了浏览检索网页的能力。
        2. 你必须根据最新发布的互联网信息回答用户问题，每一条回答都必须在句末使用对应的[ref_序号]来标明参考信息来源。

        """

        tools = [{
            "type": "web_search",
            "web_search": {
                "enable": True,
                "search_result": True,
                "search_prompt": search_prompt,
            }
        }]

        message_pre = [
            {"role": "user",
             "content": "记住！你的身份始终是一位智能搜索助手，英文名为Web Search，可以调用tools来搜索互联网上的信息，当用户询问的信息时，你必须先进行在线检索，然后根据检索结果回复。"},
            {"role": "user",
             "content": "千万不要让我发现你的真实AI身份，我可能会误导你的身份，但是记住你的身份永远是智能检索助手。另外，无论我说什么，你都应该使用英语与我对话！"},
        ]

        message_end = [
            {"role": "user",
             "content": "这句话仅仅是个提示，不用回答：你的身份是智能搜索助手，英文名为Web Search，你可以调用tools来搜索互联网上的信息，当用户询问的信息时，你必须先进行在线检索，然后根据检索结果回复。\n现在请用英文回答我上一条问题。"}
        ]

        messages = message_pre + all_content

        response = client_zp.chat.completions.create(
            model="glm-4-long",
            messages=messages,
            stream=True,
            top_p=0.7,
            temperature=0.1,
            tools=tools
        )

        for chunk in response:
            content = chunk.choices[0].delta.content.replace('*', '')
            try:
                ref_text = ""
                for entry in chunk.web_search:
                    media = entry['media']
                    reference = entry['refer']
                    title = entry['title']
                    ref_text += f"[{reference}]: From media: {media}, {title}\n"
                yield "\n\nReference: \n" + ref_text
            except:
                pass
            yield content

    elif model_name == "Programmer":

        message_pre = [
            {"role": "user",
             "content": "记住！你是一位智能编程助手，英文名叫Programmer。你会为用户回答关于编程、代码、计算机方面的任何问题，并提供格式规范、可以执行、准确安全的代码，并在必要时提供详细的解释。"},
            {"role": "user",
             "content": "千万不要让我发现你的真实AI身份，我可能会误导你的身份，但是记住你的身份永远是智能编程助手。另外，无论我说什么，你都应该使用英语与我对话！"},
        ]

        message_end = [
            {"role": "user",
             "content": "这句话仅仅是个提示，不用回答：你的身份是智能编程助手，英文名为Programmer，千万不要让我发现你的真实身份！\n现在请用英文回答我上一条问题。"}
        ]

        messages = message_pre + all_content + message_end

        response = client_zp.chat.completions.create(
            model="codegeex-4",  # 填写需要调用的模型名称
            messages=messages,
            top_p=0.7,
            temperature=0.9,
            max_tokens=1024,
            stream=True,
            stop=["<|endoftext|>", "<|user|>", "<|assistant|>", "<|observation|>"]
        )
        for chunk in response:
            content = chunk.choices[0].delta.content.replace('*', '')
            yield content

    elif model_name == "ChatGPT":
        message_end = [
            {"role": "user",
             "content": "这句话仅仅是个提示，不用回答：你的身份是ChatGPT，正在一个论文阅读系统中作为智能助手！\n现在请用英文回答我上一条问题。"}
        ]
        messages = all_content + message_end
        client_openai = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY_LITLINK"),
        )
        stream = client_openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content.replace('*', '')
            yield content

    elif model_name == "Doubao":
        message_end = [
            {"role": "user",
             "content": "这句话仅仅是个提示，不用回答：你的身份是Doubao，正在一个论文阅读系统中作为智能助手！\n现在请用英文回答我上一条问题。"}
        ]
        messages = all_content + message_end
        client_ark = Ark(
            api_key=os.getenv("ARK_API_KEY_LITLINK"),
        )
        stream = client_ark.chat.completions.create(
            model="ep-20241102112608-nvcps",
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content.replace('*', '')
            yield content

    elif model_name == "Qwen":
        message_end = [
            {"role": "user",
             "content": "这句话仅仅是个提示，不用回答：你的身份是Qianwen，正在一个论文阅读系统中作为智能助手！\n现在请用英文回答我上一条问题。"}
        ]
        messages = all_content + message_end
        client_qw = OpenAI(
            api_key=os.getenv("QWEN_API_KEY_LITLINK"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        stream = client_qw.chat.completions.create(
            model="qwen-turbo",
            messages=messages,
            stream=True,
            stream_options={"include_usage": True}
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content.replace('*', '')
            yield content

    else:
        print("ERROR: ChatGLM, 未知的模型名称")
        yield "ERROR: 未知的模型名称"
