from base_rag.rag_layer.llm import chat
from base_rag.database.match_keyword_es import ESNote
from base_rag.rag_layer.embedding import get_embedding
from base_rag.database.index_milvus import VecIndex
from base_rag.faq.index_faq import FAQVecIndex
from base_rag.rag_layer.ranker import rank
from base_rag.database.cache_redis import QA
def main():
    history = []
    while True:
        query = input("请输入问题：")
        results = QA.find(QA.query==query).all()
        prompt = query
        answer = ""
        if results:
            answer = results[0].answer
            print(f"cache回答{answer}")
        else:
            query_vec = get_embedding(query)
            match_query = FAQVecIndex("faq").search(query_vec,topk=1)[0]
            if match_query.score > 0.82:
                print(f"FAQ回答:{match_query.answer}")
            else:
                prompt = f"请判断用户的问题是否需要搜索知识库，知识库中包含的数据有关于美妆，面霜、粉底液、护手霜等的热点模板，如果用户问题需要这些热点模板，请返回true，否则返回false。不要回复其他内容。这是是用户的问题：{query}"
                need_rag = chat(prompt,history)
                if need_rag.lower() == "true":
                    docs_vec = VecIndex("note").search(query_vec)
                    docs_es = ESNote.query(query)
                    docs = set(docs_vec+docs_es)

                    for doc in docs:
                        doc.score = rank(doc.parent,query)
                    filtered_docs = [doc for doc in docs if doc.score>0.7]
                    docs_ranked = sorted(filtered_docs, key=lambda x: rank(x.parent,query), reverse=True)
                    if docs_ranked:
                        print(f"搜索结果:{docs_ranked}")
                        # docs_ranked = docs_es
                        length = len(docs_ranked)
                        # if length % 2 == 0:
                        #     list1 = list(range(0, length, 2)) + list(range(length - 1, 0, -2))
                        # else:
                        #     list1 = list(range(0, length, 2)) + list(range(length - 2, 0, -2))
                        list1 = list(range(0, length, 2)) + list(range(length - 1, 0, -2)) if length % 2 == 0 else list(range(0, length, 2)) + list(range(length - 2, 0, -2))
                        reference = " ".join([docs_ranked[i].parent for i in list1])
                        prompt = f"请根据以下参考内容回答问题：\n{reference}\n问题：{query}\n答案："



                answer = chat(prompt,history)
                QA(query=query, answer=answer).save()
                print("回答：", answer)
                history.append({"role": "user", "content": query})
                history.append({"role": "assistant", "content": answer})

                # query : 我现在要卖A牌的面霜，请帮我写一篇营销文案
                # query : 我现在要卖B牌的面霜，请帮我写一篇营销文案
                # query : 我现在要卖C牌的护手霜，请帮我写一篇营销文案

                """
                {'query': '中免日上买不到DW粉底液，有什么其他购买渠道推荐吗？', 'answer': '除了中免日上，您可以考虑在官方品牌官网、天猫旗舰店、京东自营或大型百货专柜购买，以确保正品和售后服务。'}
                {'query': 'DW粉底液现在感觉太黄了，有什么类似但色号更合适的持妆粉底液推荐？', 'answer': '针对DW粉底液色号偏黄的问题，您可以尝试雅诗兰黛DW的升级版或同品牌其他系列，如雅诗兰黛沁水粉底液，它提供更多中性色调选项。另外，兰蔻持妆粉底液和阿玛尼权力粉底液也以持妆和色号多样著称，适合油皮且氧化暗沉问题较轻。'}
                {'query': '油痘肌在冬天如何选择持妆粉底液，避免氧化暗沉？', 'answer': '对于油痘肌，冬天选择持妆粉底液时，建议优先考虑控油和抗氧化的产品。例如，雅诗兰黛DW粉底液虽然色号可能偏黄，但其持妆效果显著。您可以搭配使用抗氧化妆前乳，并选择色号更贴近肤色的版本。其他推荐包括NARS自然光感粉底液和MAC定制无瑕粉底液，它们以持妆和减少暗沉而受欢迎。'}
                {'query': '双十一买了YSL恒久粉底液但觉得挑状态，有什么更适合日常使用的持妆粉底液推荐？', 'answer': '如果YSL恒久粉底液对状态要求较高，您可以考虑更稳定的选项。例如，雅诗兰黛DW粉底液以其全天候持妆著称，适合多种肤况。另外，欧莱雅Infallible粉底液和美宝莲Superstay粉底液是平价替代品，提供类似持妆效果且更易于日常使用。'}
                {'query': '冬天使用DW粉底液妆效惊艳，但快用完了，有什么类似产品可以替代？', 'answer': '鉴于您对DW粉底液在冬天的妆效满意，建议直接回购或尝试其升级版。如果寻求替代，兰蔻持妆粉底液和纪梵希柔雾哑光粉底液都是热门选择，它们提供类似持妆力和哑光妆效，适合油皮且色号选择更广。'}
                
                """
if __name__ == '__main__':
    main()