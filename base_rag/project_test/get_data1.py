from playwright.sync_api import sync_playwright
from sqlmodel import Field, Session, SQLModel, create_engine,select
from conf import settings
import database
import time
import requests
class GetData:
    def click_item(self,cards,page):
        for i, card in enumerate(cards):
            img_list = []
            card.click()
            page.wait_for_timeout(10000)
            # 标题
            title = page.locator('title').first.text_content() or ""
            # 作者
            name = page.locator('.username').first.text_content() or ""
            # 描述
            desc = page.locator('.note-text').first.text_content() or ""
            # 喜欢
            like_count = page.locator('.like-lottie').text_content() or "0"
            # 评论
            contents = page.locator('.content').all_text_contents()[:10]
            # 收藏数
            collection_count = page.locator('#note-page-collect-board-guide').text_content() or "0"
            # 评论数
            reply_count = page.locator('.chat-wrapper').text_content() or "0"
            # 标签
            tags = page.locator('[id="hash-tag"]').all_text_contents()
            tags = ",".join(tags) if tags else ""
            # 图片
            image_elements = page.locator('[class="img-container"] img').all()
            for img in image_elements:
                url = img.get_attribute("src")
                if url:
                    try:
                        img_bytes = requests.get(url,timeout=2).content
                        img_list.append(img_bytes)
                    except Exception as e:
                        print(e)


            print(title)
            print(name)
            print(desc)
            print("like_count --> ", like_count)
            print(contents)
            print("collection_count --> ", collection_count)
            print("reply_count --> ", reply_count)
            print("tags --> ", tags)

            print(img_list)
            page.go_back()
            time.sleep(10)
            if i % 5 == 0:
                page.mouse.wheel(0, 800)
            try:
                database.Database(
                title=title,
                name=name,
                desc=desc,
                like_count=like_count,
                contents=str(contents),
                reply_count=reply_count,
                tags=tags,
                ).insert()
            except Exception as e:
                print(e)
    def get_data(self):
        with sync_playwright() as p:
            engine = create_engine(settings.url)
            database.SQLModel.metadata.create_all(engine)
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            # page.goto("https://www.xiaohongshu.com/")
            page.goto("https://www.xiaohongshu.com/search_result?keyword=%25E7%25A9%25BF%25E6%2590%25AD&source=unknown")
            page.wait_for_timeout(20000)
            while True:
                cards = page.locator('[class="cover mask ld"]').all()
                self.click_item(cards, page)


if __name__ == '__main__':
    GetData().get_data()