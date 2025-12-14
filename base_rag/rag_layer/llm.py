import openai
from conf import settings
client = openai.Client(api_key=settings.api_key,base_url=settings.base_url)

def chat(query,history,system_prompt="你是一个热点文案撰写专家，根据提供的信息分析出热点营销的模板，之后请根据用户的问题完成相应热点营销文案的生成。要求：新颖，以引流为主。"):
    if history is None:
        history = []
    response = client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content":system_prompt},
            *history,
            {"role": "user", "content": query},
        ],
        temperature=0,
    )
    return response.choices[0].message.content
if __name__ == '__main__':
    # print(chat("请生成一篇关于美妆的文案"))
    pass
