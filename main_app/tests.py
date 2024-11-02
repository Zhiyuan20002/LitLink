from zhipuai import ZhipuAI

search_prompt = """

# 以下是来自互联网的信息：
{search_result}

# 当前日期: 2024-XX-XX

# 要求：
根据最新发布的信息回答用户问题，当回答引用了参考信息时，必须在句末使用对应的[ref_序号]来标明参考信息来源。

"""

client = ZhipuAI(api_key="f3478448c98f521a5029ea6cbde7ecd0.JoYoUgsBLMflLhcM")  # 填写您自己的APIKey

tools = [{
    "type": "web_search",
    "web_search": {
        "enable": True,
        "search_query": "最近国内有哪些新闻",
        "search_result": True,
        "search_prompt": search_prompt
    }
}]

response = client.chat.completions.create(
    model="glm-4-flash",  # 填写需要调用的模型名称
    messages=[
        {"role": "user", "content": "问：最近国内有哪些新闻，答："}
    ],
    top_p=0.7,
    temperature=0.1,
    tools=tools,
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content, end='')
    try:
        for entry in chunk.web_search:
            media = entry['media']
            reference = entry['refer']
            print(f"媒体：{media}，引用：{reference}")
    except:
        pass

# print(response.choices[0].message.content)
#
# for entry in response.web_search:
#     media = entry['media']
#     reference = entry['refer']
#     print(f"媒体：{media}，引用：{reference}")
