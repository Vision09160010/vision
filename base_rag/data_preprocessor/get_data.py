from playwright.sync_api import sync_playwright
from sqlmodel import create_engine
from conf import settings
from base_rag.database.database import MysqlNote,SQLModel


def get_data():
    with sync_playwright() as p:
        engine = create_engine(settings.url)
        SQLModel.metadata.create_all(engine)
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()

        # 粉底液
        # page.goto("https://www.xiaohongshu.com/search_result?keyword=%25E7%25B2%2589%25E5%25BA%2595%25E6%25B6%25B2&source=unknown")

        # 防晒霜
        # page.goto("https://www.xiaohongshu.com/search_result?keyword=%25E9%2598%25B2%25E5%2597%25AE%25E9%259C%259C&source=unknown")

        # 护肤品
        page.goto("https://www.xiaohongshu.com/search_result?keyword=%25E6%258A%25A4%25E8%2582%25A4%25E5%2593%2581&source=unknown")


        page.wait_for_timeout(15000)
        page.hover("[class ='filter']")
        page.wait_for_timeout(1500)
        page.hover("text='图文'")
        page.wait_for_timeout(1000)
        page.click('text="图文"')
        page.wait_for_timeout(5000)
        page.hover("[class ='filter']")
        page.wait_for_timeout(1500)
        page.hover("text='最多评论'")
        page.wait_for_timeout(1000)
        page.click('text="最多评论"')
        page.wait_for_timeout(1000)
        page.hover("text='一周内'")
        page.wait_for_timeout(1000)
        page.click('text="一周内"')
        page.wait_for_timeout(1000)
        page.hover('text="发现"')
        page.wait_for_timeout(1000)

        while True:
            page.wait_for_selector('[class="cover mask ld"]')
            cards = page.locator('[class="cover mask ld"]').all()

            for i, card in enumerate(cards):
                page.wait_for_timeout(5000)
                card.click()
                page.wait_for_timeout(5000)
                # 标题
                title = page.locator('#detail-title').text_content()
                # 正文
                note = page.locator('#detail-desc').text_content()
                # 图片
                images = page.locator('.img-container img').all()
                images_urls = []
                for n, node in enumerate(images):
                    url = node.get_attribute("src") or node.get_attribute("data-src")
                    images_urls.append(url)
                # 标签
                page.wait_for_timeout(5000)
                # tags = page.locator(".tag").all_text_contents()

                print(f"title --> {title}")
                print(f"note --> {note}")
                # print(f"tags --> {tags}")
                print(f"images_urls --> {images_urls}")
                page.go_back()
                page.wait_for_timeout(5000)
                if (i + 1) % 5 == 0:
                    page.mouse.wheel(0, 500)
                MysqlNote(title=title, note=note, images_url=",".join(url for i in images_urls)).insert()
                # database.Note(title=title, note=note, images_url=f"{images_urls}").insert()


if __name__ == '__main__':
    get_data()