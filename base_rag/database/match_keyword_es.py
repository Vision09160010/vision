import warnings
from base_rag.database.items import NoteItem
warnings.filterwarnings("ignore")
from elasticsearch_dsl import Document, Keyword, Text, connections
from conf import settings
connections.create_connection(hosts=settings.es_host,
                              verify_certs = False,
                              ssl_assert_hostname = False,
                              http_auth = (settings.es_user, settings.es_password),
                              )
class ESNote(Document):
    title = Text(analyzer='smartcn')
    body = Text(analyzer='smartcn')
    tags = Keyword()

    class Index:
        name = 'notes'
        settings = {
          "number_of_shards": 2,
        }

    def save(self, ** kwargs):
        if self.body is not None:
            self.lines = len(self.body.split())
        else:
            self.lines = 0
        return super(ESNote, self).save(** kwargs)


    @classmethod
    def query(cls, text):
        items = cls.search().query("match", child=text)[:10].execute()
        return [NoteItem(id=item.meta.id, parent=item.parent,clid=item.child,score=item.meta.score) for item in items]

    @classmethod
    def scan(self):
        s = self.search()
        for item in s.scan():
            yield item
