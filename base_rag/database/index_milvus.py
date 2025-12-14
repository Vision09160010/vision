from base_rag.database.match_keyword_es import ESNote
from base_rag.rag_layer.embedding import get_embedding
from pymilvus import MilvusClient, DataType
from base_rag.database.items import NoteItem
from conf import settings

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


class VecIndex(metaclass=Singleton):
    def __init__(self, collection_name):
        self.client = MilvusClient(
            uri=settings.milvus_uri,
            user=settings.milvus_user,
            password=settings.milvus_password,
        )
        schema = self.client.create_schema()
        schema.add_field(field_name="es_id", datatype=DataType.VARCHAR, max_length=100, is_primary=True)
        schema.add_field(field_name="vec", datatype=DataType.FLOAT_VECTOR, dim=dimension)
        schema.add_field(field_name="parent", datatype=DataType.VARCHAR, max_length=65535)


        self.collection_name = collection_name
        if not self.client.has_collection(self.collection_name):
            self.client.create_collection(collection_name=self.collection_name,
                                          schema=schema,
                                          index_params=index_params)

    def insert(self, embeddings, docs, ids,):
        data = []
        for i, doc in enumerate(docs):
            data.append({
                "es_id": ids[i],
                "parent": doc,
                "vec": embeddings[i],
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
                                  output_fields=["es_id", "parent"])[0]
        # print(hits)
        return [NoteItem(id=hit.entity.get("es_id"), parent=hit.entity.get("parent"), score=hit.distance) for hit in hits]

    def load(self):


        for item in ESNote.scan():
            embed = get_embedding(item.child)
            VecIndex("notes").insert([embed.tolist()], [item.parent], [item.meta.id])
            print(item.meta.id, item.child, item.parent)


if __name__ == '__main__':
    vct = VecIndex("note")
    vct.load()













