"""
Diagnostic: inspect the rotation captcha DOM to find all image elements and their sources.
"""
import asyncio
import json
import os
import base64
from playwright.async_api import async_playwright

COOKIES_FILE = "/home/ubuntu/upload/pasted_content.txt"
VIDEO_URL = "https://www.tiktok.com/@realjayllnn/video/7586112300378033422"

async def main():
    with open(COOKIES_FILE) as f:
        raw = json.load(f)
    if isinstance(raw, dict):
        raw = raw.get("cookies", [])

    cookies = []
    for c in raw:
        cookie = {
            "name": c.get("name", ""),
            "value": c.get("value", ""),
            "domain": c.get("domain", ".tiktok.com"),
            "path": c.get("path", "/"),
        }
        exp = c.get("expirationDate") or c.get("expires")
        if exp:
            cookie["expires"] = float(exp)
        ss = c.get("sameSite", "")
        ss_map = {"no_restriction": "None", "unspecified": "Lax", "lax": "Lax", "strict": "Strict", "none": "None"}
        cookie["sameSite"] = ss_map.get(str(ss).lower(), "Lax")
        if cookie["name"] and cookie["value"]:
            cookies.append(cookie)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        await context.add_cookies(cookies)
        page = await context.new_page()

        # Warm up
        await page.goto("https://www.tiktok.com", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        # Navigate to video
        await page.goto(VIDEO_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        # Click comment icon
        comment_icon = await page.query_selector("span[data-e2e='comment-icon']")
        if comment_icon:
            await comment_icon.click()
            await asyncio.sleep(2)

        # Find comment input
        comment_input = await page.query_selector("div[data-e2e='comment-input'] div[contenteditable='true']")
        if comment_input:
            await comment_input.click()
            await page.keyboard.type("affilify.eu", delay=50)
            await asyncio.sleep(1)

        # Click post
        post_btn = await page.query_selector("button[data-e2e='comment-post']")
        if post_btn:
            await post_btn.click()
            await asyncio.sleep(3)

        # Now inspect the captcha DOM
        print("\n=== CAPTCHA DOM INSPECTION ===")
        
        # Check all images in captcha
        img_info = await page.evaluate("""
            () => {
                const captchaEls = document.querySelectorAll('div[class*="captcha"], div[id*="captcha"]');
                const results = [];
                captchaEls.forEach(el => {
                    const imgs = el.querySelectorAll('img');
                    imgs.forEach(img => {
                        results.push({
                            src_type: img.src ? (img.src.startsWith('data:') ? 'base64' : img.src.startsWith('http') ? 'url' : 'other') : 'none',
                            src_preview: img.src ? img.src.substring(0, 100) : '',
                            src_len: img.src ? img.src.length : 0,
                            class: img.className,
                            id: img.id,
                            width: img.offsetWidth,
                            height: img.offsetHeight,
                            natural_w: img.naturalWidth,
                            natural_h: img.naturalHeight,
                        });
                    });
                });
                return results;
            }
        """)
        
        print(f"Found {len(img_info)} images in captcha:")
        for i, img in enumerate(img_info):
            print(f"  [{i}] type={img['src_type']} len={img['src_len']} class='{img['class']}' id='{img['id']}' size={img['width']}x{img['height']} natural={img['natural_w']}x{img['natural_h']}")
            if img['src_preview']:
                print(f"       src_preview: {img['src_preview']}")

        # Check canvas elements
        canvas_info = await page.evaluate("""
            () => {
                const captchaEls = document.querySelectorAll('div[class*="captcha"], div[id*="captcha"]');
                const results = [];
                captchaEls.forEach(el => {
                    const canvases = el.querySelectorAll('canvas');
                    canvases.forEach(c => {
                        results.push({
                            class: c.className,
                            id: c.id,
                            width: c.width,
                            height: c.height,
                        });
                    });
                });
                return results;
            }
        """)
        print(f"\nFound {len(canvas_info)} canvas elements in captcha:")
        for c in canvas_info:
            print(f"  class='{c['class']}' id='{c['id']}' size={c['width']}x{c['height']}")

        # Check the captcha title
        title = await page.evaluate("""
            () => {
                const el = document.querySelector('div[class*="captcha"] h2, div[class*="captcha"] p, div[class*="captcha"] div[class*="title"]');
                return el ? el.innerText : 'NOT FOUND';
            }
        """)
        print(f"\nCaptcha title: '{title}'")

        # Take a screenshot
        os.makedirs("/home/ubuntu/diagnostics", exist_ok=True)
        await page.screenshot(path="/home/ubuntu/diagnostics/rotation_inspect.png")
        print("\nScreenshot saved to /home/ubuntu/diagnostics/rotation_inspect.png")

        await browser.close()

asyncio.run(main())
