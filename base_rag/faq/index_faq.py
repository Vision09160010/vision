from typing import List
from base_rag.rag_layer.embedding import get_embedding
from pymilvus import MilvusClient, DataType
from base_rag.database.items import FAQItem
from conf import settings
from uuid import uuid1
import simple_pickle as sp
dimension = 1024
search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
index_params = MilvusClient.prepare_index_params()
index_params.add_index(
    field_name="vec",
    index_type="IVF_FLAT",
    index_name="inverted_index",
    metric_type="IP",
    params={"nlist": 128},
)


class Singleton(type):
    _instances = {}

    def __call__(cls, name):
        k = name
        if k not in cls._instances:
            cls._instances[k] = super(Singleton, cls).__call__(name)
        return cls._instances[k]


class FAQVecIndex(metaclass=Singleton):
    def __init__(self, collection_name):
        self.client = MilvusClient(
            uri=settings.milvus_uri,
            user=settings.milvus_user,
            password=settings.milvus_password,
        )
        schema = self.client.create_schema()
        schema.add_field(field_name="qid", datatype=DataType.VARCHAR, max_length=100, is_primary=True)
        schema.add_field(field_name="vec", datatype=DataType.FLOAT_VECTOR, dim=dimension)
        schema.add_field(field_name="query", datatype=DataType.VARCHAR, max_length=65535)
        schema.add_field(field_name="answer", datatype=DataType.VARCHAR, max_length=65535)


        self.collection_name = collection_name
        if not self.client.has_collection(self.collection_name):
            self.client.create_collection(collection_name=self.collection_name,
                                          schema=schema,
                                          index_params=index_params)

    def insert(self, embeddings, queries, answers,):
        data = []
        for i, doc in enumerate(queries):
            data.append({
                "qid": str(uuid1()),
                "query": doc,
                "vec": embeddings[i],
                "answer": answers[i],
            })

        if data:
            self.client.upsert(collection_name=self.collection_name, data=data)

    def search(self, vec, topk=3):
        vec = [vec.tolist()]
        hits = self.client.search(collection_name=self.collection_name,
                                  data=vec,
                                  anns_field="vec",
                                  limit=topk,
                                  search_params=search_params,
                                  output_fields=["qid", "query","answer"])[0]
        # print(hits)
        return [FAQItem(id=hit.entity.get("qid"), question=hit.entity.get("query"),answer=hit.entity.get("answer"), score=hit.distance) for hit in hits]

    def load(self,items: List[FAQItem]):
        for item in items:
            embed = get_embedding(item["query"])
            FAQVecIndex("faq").insert([embed.tolist()], [item['query']], [item['answer']])
            print(item['query'], item["answer"])


if __name__ == '__main__':
    # FAQVecIndex("faq").load(sp.read_pickle("../data/query_answers.pkl"))
    list1 = sp.read_pickle("../data/query_answers.pkl")
    for i,item in enumerate(list1):
        print(item)
        if i==4:
            break











