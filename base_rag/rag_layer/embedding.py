from openai import OpenAI
import numpy as np
client = OpenAI(
    base_url="http://localhost:6006/v1",
    api_key="1111"  # vLLM 默认不需要认证，但需要提供任意值
)
def get_embedding(text, model="bge-m3"):
    """获取文本嵌入向量"""
    try:
        response = client.embeddings.create(model=model, input=text)
        return np.array(response.data[0].embedding)
    except Exception as e:
        print(f"获取嵌入失败: {e}")
        return None