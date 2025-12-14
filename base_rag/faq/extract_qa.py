import json

import simple_pickle as sp
from base_rag.rag_layer.llm import chat



def gen_qa():
    query_answers = []
    texts = sp.read_pickle("../data/split.pkl")
    system_prompt = '请根据用户输入的文案内容，产生相应的问题，并回答问题，注意问题要更偏向于营销，格式为json:[{"query":"","answer":""}],不要给多余的内容，不要解释'
    for text in texts:
        prompt = f"以下是文案的内容：{text['parent']}"
        query_answer_tmp = chat(query=prompt, system_prompt=system_prompt)
        query_answer_tmp = json.loads(query_answer_tmp)
        print(query_answer_tmp)
        query_answers.extend(query_answer_tmp)
    sp.write_pickle(query_answers, "../data/query_answers.pkl")




if __name__ == '__main__':
    gen_qa()