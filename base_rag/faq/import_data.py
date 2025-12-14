import simple_pickle as sp
from index_faq import FAQVecIndex
from base_rag.database.items import FAQItem

query_answers = sp.read_pickle("../data/query_answers.pickle")
item_answers = [FAQItem(id="",question=query_answer["query"],answer=query_answer["answer"])for query_answer in query_answers]
FAQVecIndex("faq").load(item_answers)