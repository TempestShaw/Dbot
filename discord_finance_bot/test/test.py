from playwright.async_api import async_playwright
import asyncio

async def fetch_plate_list():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto("https://www.moomoo.com/quote/us/concepts")
        await page.wait_for_selector(".base-pagination .item")
        
        # 點擊第一頁
        first_page_item = await page.query_selector(".base-pagination .item:nth-child(2)")
        if first_page_item:
            await first_page_item.click()
        
        # 捕獲 API 響應
        async def handle_response(response):
            if "get-plate-list" in response.url:
                try:
                    data = await response.json()
                    print("API data:", data)
                except:
                    print("Failed to parse JSON")

        # 注意這裡用 lambda 包 asyncio.create_task
        page.on("response", lambda resp: asyncio.create_task(handle_response(resp)))
        
        # 等待 API 完成
        await page.wait_for_timeout(5000)
        await browser.close()

asyncio.run(fetch_plate_list())
