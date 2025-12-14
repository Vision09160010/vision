import requests
from tqdm import tqdm
import simple_pickle as sp
from base_rag.database.database import MysqlNote
from base_rag.database.match_keyword_es import ESNote
from base_rag.data_processor_utils.ocr_processor import ModelProcessor
from processors.text_split_processor import split_text

class DataProcessor:
    # 1.查询mysql获取图片链接
    def get_url(self):
        mysql_note = MysqlNote()
        rows = mysql_note.query_all()
        for i, row in enumerate(rows):
            urls = row.images_url
            url_list = [url for url in urls.replace("'", "").split(",")]
            for n, url in enumerate(url_list):
                self.download(url, f"./data/imgs/{i}_{n}.jpg")

    # 2.下载图片
    def download(self, url, save_path):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
        except Exception as e:
            print(e)

    # 3.OCR识别图片
    def ocr_images(self, urls):
        modelscope = ModelProcessor()
        modelscope.img2text(modelscope.load_PaddleOCRVL(), "./data/imgs")

    # 4.MySQL读取数据并拼接文本
    def mysql_to_text(self):
        rows = MysqlNote.query_all()
        text = ""
        for row in tqdm(rows):
            # 拼接
            text += f"{row.title}"
            text += f"{row.note}"
        sp.write_data(text, "../data/result.md")

    # 5.切分
    def split_all(self):
        text = sp.read_data("../data/result.md")
        text = "".join(para for para in text)
        paras = split_text(text)

        sp.write_pickle(paras, "../data/split.pkl")
        text1 = "".join(str(para) for para in paras)
        sp.write_data(text1, "../data/split.txt")

    # 6.写入ES
    def data2es(self):
        datas = sp.read_pickle(f"../data/split.pkl")
        for data in datas:
            article = ESNote()
            article.child = data['child']
            article.parent = data['parent']
            print(data['parent'])
            article.save()



if __name__ == '__main__':
    process = DataProcessor()
    # process.get_url()
    # process.mysql_to_text()
    # process.split_all()
    process.data2es()

