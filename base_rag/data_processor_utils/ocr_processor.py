from paddleocr import ChartParsing
from paddleocr import PaddleOCRVL
class ModelProcessor:
    def img2text(self,model,img_path):

        output = model.predict(img_path)
        for res in output:
            res.print()
            # res.save_to_json(save_path="output")
            res.save_to_markdown(save_path=f"output{res.id}.md")

    def chart_analyse(self,model,img_path):

        results = model.predict(
            input={"image": img_path},
            batch_size=1
        )

        for res in results:
            # res.save_to_json(f"./output/res.json")
            res.save_to_markdown(save_path=f"output{res.id}.md")
            print(res)
            print(res['result'])

    def load_PaddleOCRVL(self):
        return PaddleOCRVL()

    def load_ChartParsing(self):
        return ChartParsing(model_name="PP-Chart2Table")
if __name__ == '__main__':

    processor = ModelProcessor()
    model = processor.load_PaddleOCRVL()

