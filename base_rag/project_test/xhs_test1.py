
import os
import time
import requests
from playwright.sync_api import sync_playwright, TimeoutError

IMG_DIR = "./data/imgs"
os.makedirs(IMG_DIR, exist_ok=True)


def open_detail(context, elem):
    # 尝试打开新页
    try:
        with context.expect_page(timeout=8000) as new_page_info:
            elem.click(force=True)
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded")
        return new_page
    except TimeoutError:
        # 页面没跳出来，说明是当前页跳转
        elem.click(force=True)
        return context.pages[-1]


def wait_safe(page, selector):
    try:
        page.wait_for_selector(selector, timeout=15000)
        return True
    except TimeoutError:
        return False


def safe_img_download(url, save_path, retry=3):
    for _ in range(retry):
        try:
            data = requests.get(url, timeout=10).content
            with open(save_path, "wb") as f:
                f.write(data)
            return True
        except Exception:
            time.sleep(1)
    return False


def get_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        page = context.new_page()
        page.goto("https://www.xiaohongshu.com/search_result?keyword=%E7%B2%89%E5%BA%95%E6%B6%B2")
        page.wait_for_timeout(20000)

        cards = page.locator('[class="cover mask ld"]').all()

        for i, elem in enumerate(cards):
            print(f"\n>>> 正在采集第 {i} 条帖子")

            detail_page = open_detail(context, elem)

            if not wait_safe(detail_page, "#detail-title.title"):
                print("标题加载失败，跳过")
                detail_page.close()
                continue

            title = detail_page.locator("#detail-title.title").text_content() or ""
            note = detail_page.locator("#detail-desc.desc").text_content() or ""
            tags = detail_page.locator(".tag").all_text_contents()

            imgs = detail_page.locator(".img-container img").all()
            urls = []

            for n, node in enumerate(imgs):
                url = node.get_attribute("src") or node.get_attribute("data-src")
                if not url:
                    continue

                urls.append(url)

                save_path = f"{IMG_DIR}/{i}_{n}.png"
                ok = safe_img_download(url, save_path)
                if not ok:
                    print(f"    × 图片下载失败: {url}")
                else:
                    print(f"    ✓ 图片保存: {save_path}")

            print(f"title: {title}")
            print(f"note: {note}")
            print(f"tags: {tags}")
            print(f"urls: {urls}")

            detail_page.close()
            page.bring_to_front()
            page.wait_for_timeout(1000)
if __name__ == '__main__':
    get_data()