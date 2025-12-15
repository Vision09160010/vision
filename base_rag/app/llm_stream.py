from openai import AsyncClient
from conf import settings
client = AsyncClient(api_key=settings.api_key,base_url=settings.base_url)
from base_rag.logs.log import logger
async def async_chat(query,history,system_prompt):
    if history is None:
        history = []
    stream = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content":system_prompt},
            *history,
            {"role": "user", "content": query},
        ],
        temperature=0,
        stream =  True
    )
    return stream
if __name__ == '__main__':
    pass
