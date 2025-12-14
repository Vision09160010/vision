from base_rag.data_processor_utils.ocr_processor import ModelProcessor
import os
from tqdm import tqdm
import openai
import simple_pickle as sp
from base_rag.data_processor_utils.text_split_processor import split_text
from base_rag.database.match_keyword_es import *
client = openai.Client(api_key=settings.api_key,base_url=settings.base_url)
max_len = 512
class DataProcessor:
    # 2. 图片转文字(使用OCR将图片转成文本)
    def img2text_preprocess(self, img_path):
        images = os.listdir(img_path)
        model_process = ModelProcessor()
        model = model_process.load_PaddleOCRVL()
        for i,image in enumerate(tqdm(images)):
            model_process.img2text(model,f"img_path/{image}")


    #
    # 3. 拼接md文件
    def concat_text(self):

        text = ""
        for file in os.listdir("./output"):
            content = sp.read_data(f"./output/{file}")
            text += ''.join(content).strip()
        sp.write_data(text, f"../data/result.md")


    # 4. 切分文档(调用大模型)
    # def split_txt(self):
    #     text = sp.read_data("./data/result.md")
    #     response = client.chat.completions.create(
    #         model=settings.model_name,
    #         messages=[
    #             {"role": "system",
    #              "content": '将文本分割成一篇篇文章，供检索使用，长度不要超过512，返回json: ["文章1","文章2",……]'},
    #             {"role": "user", "content": f"以下是文章：\n\n{text}"},
    #         ],
    #         temperature=0,
    #         response_format={"type": "json_object", "schema": {"type": "array", "items": {"type": "string"}}}
    #     )
    #     print(response.choices[0].message.content)
    #     text_list = json.loads(response.choices[0].message.content)
    #     sp.write_pickle(text_list, f"./data/results/result.pkl")

    # 4. 切分,拼接 文档
    def split_t(self):
        text = sp.read_data("../data/result.md")
        params = split_text(str(text))
        sp.write_pickle(params, "./data/results/split_text.pkl")
        sp.write_data(params, "./data/results/split_text.md")

    def data2es(self):
        article = ESNote()
        datas = sp.read_pickle(f"./data/results/split_text.pkl")
        for data in datas:
            article.child = data['child']
            article.parent = data['parent']
        article.save()


if __name__ == '__main__':
    process = DataProcessor()
    # for i in range(423):
    #     process.img2text_preprocess(f"./data/ggl_images")

    # process.split_txt()
    # process.split_t()
    # process.concat_text()
    process.data2es()
