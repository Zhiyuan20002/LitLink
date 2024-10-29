from zhipuai import ZhipuAI
from datetime import datetime

client = ZhipuAI(api_key="99add806d43fccd92fe4bfb29f517c48.Z7YqjFR39IGwjFtb")


# 联网搜索模型
def web_search_agent(messages):
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d")

    search_prompt = f"""

    # 以下是来自互联网的信息：
    {{search_result}}

    # 当前日期: {formatted_date}

    # 要求：
    根据最新发布的信息回答用户问题，当回答引用了参考信息时，必须在句末使用对应的[ref_序号]来标明参考信息来源。

    """

    tools = [{
        "type": "web_search",
        "web_search": {
            "enable": True,
            "search_query": "根据问题要求检索相关信息并回答用户的提问",
            "search_result": True,
            "search_prompt": search_prompt
        }
    }]

    messages_init = [
        {
            "role": "user",
            "content": "你的身份是“联网搜索模型”，根据上下文内容，解决用户@你时所提出的问题，不要回答与你无关的问题"
        }
    ]

    messages = messages.append(messages_init)

    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=messages,
        top_p=0.7,
        temperature=0.1,
        tools=tools
    )

    result = response.choices[0].message.content
    return result


# Litlink论文模型
def litlink_v2_agent(messages):
    messages_init = [
        {
            "role": "user",
            "content": "你的身份是“Litlink论文模型”，根据上下文内容，解决用户@你时所提出的问题，不要回答与你无关的问题"
        }
    ]

    messages = messages.append(messages_init)

    response = client.chat.completions.create(
        model="glm-4-airx:1226531186:litlink2:r6eaqpsr",
        messages=messages,
    )

    result = response.choices[0].message.content
    return result
