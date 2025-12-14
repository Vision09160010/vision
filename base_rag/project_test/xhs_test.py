import requests
from playwright.sync_api import sync_playwright
from sqlalchemy.sql.base import elements


def get_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.xiaohongshu.com/search_result?keyword=%25E7%25B2%2589%25E5%25BA%2595%25E6%25B6%25B2&source=unknown")
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
        page.wait_for_selector('[class="cover mask ld"]')
        elements = page.locator('[class="cover mask ld"]').all()
        for i,elem in enumerate(elements):
            elem.click()
            page.wait_for_timeout(6000)
            page.wait_for_selector('#detail-title.title')
            title = page.locator("#detail-title.title").text_content()
            note = page.locator("#detail-desc.desc").text_content()
            tags = page.locator(".tag").all_text_contents()
            img_container = page.locator(".img-container img").all()
            urls = []
            for n,node in enumerate(img_container):
                url = node.get_attribute("src") or node.get_attribute("data-src")
                urls.append(url)
                img = requests.get(url).content
                page.wait_for_selector(".img-container img", timeout=5000)
                with open(f"../data/imgs/{i}_{n}.png", mode="wb") as img_file:
                    img_file.write(img)

            print(f"title --> {title}")
            print(f"note --> {note}")
            print(f"tag --> {tags}")
            print(f"urls --> {urls}")
            page.wait_for_timeout(1500)



            page.go_back()
            if i+1 % 5 == 0:
                page.mouse.wheel(0, 500)
                page.wait_for_timeout(1500)

            page.wait_for_timeout(3000)
            page.mouse.wheel(0, 1080)
            page.wait_for_timeout(5000)
            page.wait_for_selector('.title')
        page.wait_for_timeout(1500000)
        browser.close()

if __name__ == '__main__':
    get_data()