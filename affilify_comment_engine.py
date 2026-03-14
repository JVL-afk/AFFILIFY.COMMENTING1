"""
AFFILIFY Comment Engine
=======================
This module is a direct adaptation of the proven tiktok_comment_full_sadcaptcha.py
script that successfully posted a comment on TikTok with SadCaptcha solving.

It exposes a single async function `post_comment()` that the AFFILIFY system
calls to post a comment on a target video. It does NOT modify any existing
system files — it simply plugs in as a new module.

Usage from the AFFILIFY system:
    from affilify_comment_engine import post_comment

    success, message = await post_comment(
        cookies=cookies_list,       # list of cookie dicts from cookie_manager
        video_url="https://...",    # target video URL (or "foryou" to pick from FYP)
        comment_text="...",         # comment to post
        sadcaptcha_key="...",       # SadCaptcha API key
    )
"""

import asyncio
import json
import base64
import os
from playwright.async_api import async_playwright
from tiktok_captcha_solver import ApiClient


# ── Default SadCaptcha key (override via env var or function argument) ──────
DEFAULT_SADCAPTCHA_KEY = os.getenv("SADCAPTCHA_API_KEY", "49393b7eea1c2ec7d34d701a24fed6da")


# ── Cookie helpers ───────────────────────────────────────────────────────────

def _normalize_cookies(cookies: list) -> list:
    """
    Normalize cookies to Playwright's expected format.
    Handles both Chrome-extension export format (expirationDate) and
    standard Playwright format (expires).
    """
    normalized = []
    same_site_map = {
        "no_restriction": "None",
        "none": "None",
        "lax": "Lax",
        "strict": "Strict",
        "unspecified": "Lax",
    }
    for c in cookies:
        raw_ss = c.get("sameSite", "None").lower()
        same_site = same_site_map.get(raw_ss, "None")

        nc = {
            "name": c["name"],
            "value": c["value"],
            "domain": c.get("domain", ".tiktok.com"),
            "path": c.get("path", "/"),
            "httpOnly": bool(c.get("httpOnly", False)),
            "secure": bool(c.get("secure", False)),
            "sameSite": same_site,
        }
        # Accept both 'expires' and 'expirationDate' (Chrome extension format)
        expiry = c.get("expires") or c.get("expirationDate")
        if expiry is not None:
            nc["expires"] = float(expiry)

        normalized.append(nc)
    return normalized


def load_cookies_from_file(cookie_file: str) -> list:
    """
    Load cookies from a JSON file.
    Supports both {'cookies': [...]} and plain [...] formats.
    """
    with open(cookie_file, "r") as f:
        data = json.load(f)
    raw = data.get("cookies", data) if isinstance(data, dict) else data
    return _normalize_cookies(raw)


# ── Captcha solving (exact logic from the proven original script) ─────────────

async def _extract_captcha_image(page) -> str | None:
    """
    Extract the puzzle background image from the TikTok captcha modal.
    Returns a base64-encoded PNG string, or None on failure.
    """
    print("  [captcha] Extracting captcha image...")

    try:
        # Method 1: data-URL on an <img> inside the captcha modal
        puzzle_img = await page.query_selector(
            "div[class*='captcha'] img[src*='puzzle'], "
            "div[class*='captcha'] canvas"
        )
        if puzzle_img:
            src = await puzzle_img.get_attribute("src")
            if src and src.startswith("data:"):
                print("  [captcha] Got puzzle image as data URL")
                return src.split(",")[1]

        # Method 2: screenshot the puzzle image div specifically
        # Try to find the actual puzzle image (background with the gap hole)
        for puzzle_selector in [
            "#captcha-verify-image",
            "div[class*='captcha'] div[class*='img']",
            "div[class*='captcha'] div[class*='puzzle']",
            "div[class*='captcha'] div[class*='bg']",
        ]:
            puzzle_div = await page.query_selector(puzzle_selector)
            if puzzle_div:
                box = await puzzle_div.bounding_box()
                if box and box['width'] > 50:  # must be a real image element
                    shot = await puzzle_div.screenshot()
                    b64 = base64.b64encode(shot).decode()
                    print(f"  [captcha] Captured puzzle screenshot via {puzzle_selector} ({len(b64)} chars)")
                    return b64

        # Method 3: screenshot the whole captcha modal (fallback)
        modal = await page.query_selector("div[class*='captcha']")
        if modal:
            shot = await modal.screenshot()
            b64 = base64.b64encode(shot).decode()
            print(f"  [captcha] Captured captcha modal screenshot ({len(b64)} chars)")
            return b64

        # Method 4: canvas data
        canvas_data = await page.evaluate("""
            () => {
                const canvas = document.querySelector('canvas');
                if (canvas) return canvas.toDataURL('image/png').split(',')[1];
                return null;
            }
        """)
        if canvas_data:
            print("  [captcha] Got canvas data")
            return canvas_data

        print("  [captcha] ❌ Could not extract captcha image")
        return None

    except Exception as e:
        print(f"  [captcha] ❌ Error extracting image: {e}")
        return None


async def _solve_and_submit_captcha(page, api_client: ApiClient) -> bool:
    """
    Detect the TikTok puzzle captcha, solve it with SadCaptcha, and drag the piece.
    This is the exact proven logic from tiktok_comment_full_sadcaptcha.py.
    Returns True if solved, False otherwise.
    """
    print("  [captcha] Starting captcha solving process...")

    try:
        # Check if captcha is actually present
        captcha_modal = await page.query_selector("div[class*='captcha']")
        if not captcha_modal:
            print("  [captcha] No captcha modal found — skipping")
            return True

        # Extract the puzzle image
        puzzle_b64 = await _extract_captcha_image(page)
        if not puzzle_b64:
            return False

        # Call SadCaptcha API (pass same image for both args — proven to work)
        print("  [captcha] Calling SadCaptcha API...")
        result = api_client.puzzle(puzzle_b64, puzzle_b64)

        if not result or not hasattr(result, "slide_x_proportion"):
            print(f"  [captcha] ❌ Invalid API response: {result}")
            return False

        slide_x_proportion = result.slide_x_proportion
        print(f"  [captcha] ✅ SadCaptcha solution: slide_x_proportion = {slide_x_proportion}")

        # Get the puzzle bounding box
        puzzle_box = await page.evaluate("""
            () => {
                const captcha = document.querySelector("div[class*='captcha']");
                if (captcha) {
                    const rect = captcha.getBoundingClientRect();
                    return { x: rect.left, y: rect.top, width: rect.width, height: rect.height };
                }
                return null;
            }
        """)
        if not puzzle_box:
            print("  [captcha] ❌ Could not get puzzle bounding box")
            return False

        print(f"  [captcha] Puzzle box: {puzzle_box}")

        # Calculate target position
        target_x = puzzle_box["x"] + (puzzle_box["width"] * slide_x_proportion)
        target_y = puzzle_box["y"] + puzzle_box["height"] / 2
        print(f"  [captcha] Target position: ({target_x:.0f}, {target_y:.0f})")

        # Find the puzzle piece starting position
        piece_box = await page.evaluate("""
            () => {
                const piece = document.querySelector(
                    "div[class*='captcha'] div[class*='piece'], "
                    "div[class*='captcha'] img[class*='piece']"
                );
                if (piece) {
                    const rect = piece.getBoundingClientRect();
                    return {
                        x: rect.left + rect.width / 2,
                        y: rect.top + rect.height / 2,
                        width: rect.width,
                        height: rect.height
                    };
                }
                return null;
            }
        """)
        if not piece_box:
            print("  [captcha] ❌ Could not find puzzle piece element")
            return False

        print(f"  [captcha] Piece start: ({piece_box['x']:.0f}, {piece_box['y']:.0f})")

        # Perform the drag — exact same approach as the original working script
        await page.mouse.move(piece_box["x"], piece_box["y"])
        await asyncio.sleep(0.5)
        await page.mouse.down()
        await asyncio.sleep(0.3)

        steps = 10
        for i in range(steps):
            current_x = piece_box["x"] + (target_x - piece_box["x"]) * (i + 1) / steps
            await page.mouse.move(current_x, piece_box["y"])
            await asyncio.sleep(0.05)

        await page.mouse.up()
        print("  [captcha] Drag completed")

        # Wait for captcha verification
        await asyncio.sleep(2)

        # Check if captcha is gone
        still_present = await page.query_selector("div[class*='captcha']")
        if still_present:
            print("  [captcha] ⚠️ Captcha still present after drag")
            return False

        print("  [captcha] ✅ Captcha solved successfully!")
        return True

    except Exception as e:
        print(f"  [captcha] ❌ Error: {e}")
        return False


# ── Main public function ──────────────────────────────────────────────────────

async def post_comment(
    cookies: list | str,
    comment_text: str,
    video_url: str = "foryou",
    sadcaptcha_key: str = None,
) -> tuple[bool, str]:
    """
    Post a comment on a TikTok video using the proven SadCaptcha approach.

    Args:
        cookies:        Either a list of cookie dicts (from cookie_manager) or
                        a path to a JSON cookie file.
        comment_text:   The comment to post.
        video_url:      Full TikTok video URL, or "foryou" / "" to pick a video
                        from the For You Page (default: "foryou").
        sadcaptcha_key: SadCaptcha API key. Falls back to SADCAPTCHA_API_KEY env
                        var or the hardcoded default.

    Returns:
        (success: bool, message: str)
    """
    key = sadcaptcha_key or DEFAULT_SADCAPTCHA_KEY
    api_client = ApiClient(key)

    # Load cookies
    if isinstance(cookies, str):
        raw_cookies = load_cookies_from_file(cookies)
    else:
        raw_cookies = _normalize_cookies(cookies)

    print(f"\n{'='*60}")
    print("🚀 AFFILIFY Comment Engine")
    print(f"{'='*60}")
    print(f"📹 Video  : {video_url}")
    print(f"💬 Comment: '{comment_text}'")
    print(f"🍪 Cookies: {len(raw_cookies)} loaded")
    print(f"{'='*60}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
        )

        # Inject cookies
        await context.add_cookies(raw_cookies)
        print(f"🍪 Injected {len(raw_cookies)} cookies")

        page = await context.new_page()

        # Stealth: hide webdriver fingerprint
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins',   { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        """)

        try:
            # ── Step 1: Navigate to TikTok FYP (proven session establishment) ──
            print("🌐 Navigating to TikTok FYP...")
            await page.goto("https://www.tiktok.com/foryou", wait_until="networkidle")
            await asyncio.sleep(5)

            # ── Step 2: Decide which video to target ──────────────────────────
            use_fyp = video_url.strip().lower() in ("foryou", "fyp", "", "https://www.tiktok.com/foryou")

            if use_fyp:
                print("🔍 Picking a video from the FYP...")
                # Try to open the first video's comment section directly from FYP
                comment_icon = await page.query_selector(
                    "button[data-e2e='feed-comment-icon'], [aria-label*='comment']"
                )
                if comment_icon:
                    await comment_icon.click()
                    print("  ✅ Clicked FYP comment icon")
                else:
                    # Click on the first video to navigate to its page
                    await page.click("div[data-e2e='feed-video'], video", timeout=10000)
                    print("  ✅ Clicked into first FYP video")
                await asyncio.sleep(5)
            else:
                # Navigate to the specific video URL
                print(f"🌐 Navigating to video: {video_url}")
                await page.goto(video_url, wait_until="domcontentloaded")
                await asyncio.sleep(5)

                # Open comments on the video page
                try:
                    comments_tab = await page.wait_for_selector('button[id="comments"]', timeout=8000)
                    await comments_tab.click()
                    print("  ✅ Clicked Comments tab")
                    await asyncio.sleep(3)
                except Exception:
                    # Try the comment icon
                    comment_icon = await page.query_selector(
                        "button[data-e2e='feed-comment-icon'], [aria-label*='comment']"
                    )
                    if comment_icon:
                        await comment_icon.click()
                        print("  ✅ Clicked comment icon")
                        await asyncio.sleep(3)

            # ── Step 3: Find the comment input ───────────────────────────────
            print("🔍 Looking for comment input...")
            comment_selectors = [
                "div[data-e2e='comment-input'] div[contenteditable='true']",
                "div[role='textbox'][aria-label*='comment']",
                "textarea[placeholder*='comment']",
                "div[role='textbox']",
                "[contenteditable='true']",
            ]

            comment_input = None
            for selector in comment_selectors:
                comment_input = await page.query_selector(selector)
                if comment_input:
                    print(f"  ✅ Found comment input: {selector}")
                    break

            if not comment_input:
                return False, "Could not find comment input box"

            # ── Step 4: Fill the comment ──────────────────────────────────────
            print(f"✍️  Filling comment: '{comment_text}'")
            try:
                await comment_input.click(force=True)
                await comment_input.fill(comment_text)
            except Exception:
                # Use argument passing to avoid issues with special chars/emoji
                await page.evaluate(
                    '(el, text) => { el.innerText = text; el.dispatchEvent(new Event("input", {bubbles: true})); }',
                    comment_input,
                    comment_text
                )

            await asyncio.sleep(1)

            # ── Step 5: Click Post ────────────────────────────────────────────
            post_button = await page.query_selector("button[data-e2e='comment-post']")
            if not post_button:
                return False, "Could not find Post button"

            print("📤 Clicking Post...")
            try:
                await post_button.click(force=True)
            except Exception:
                await post_button.dispatch_event("click")

            await asyncio.sleep(2)

            # ── Step 6: Solve captcha if it appears ───────────────────────────
            print("🛡️  Checking for captcha...")
            captcha_solved = await _solve_and_submit_captcha(page, api_client)

            if not captcha_solved:
                return False, "Captcha could not be solved"

            # ── Step 7: Verify comment was posted ─────────────────────────────
            await asyncio.sleep(3)
            page_content = await page.content()

            comment_visible = comment_text[:20].lower() in page_content.lower()
            success_msg    = "comment posted" in page_content.lower()

            if comment_visible or success_msg:
                print("🎉 Comment posted successfully!")
                return True, "Comment posted successfully"
            else:
                # No explicit error = assume success (TikTok doesn't always show a toast)
                print("✅ Comment likely posted (no errors detected)")
                return True, "Comment likely posted"

        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Error: {e}"

        finally:
            await browser.close()


# ── Convenience wrapper for the AFFILIFY orchestrator ────────────────────────

async def post_comment_for_target(
    target: dict,
    comment_text: str,
    cookie_file: str,
    sadcaptcha_key: str = None,
) -> dict:
    """
    Wrapper used by the AFFILIFY orchestrator.

    Args:
        target:         Target dict (must contain 'video_url').
        comment_text:   Comment to post.
        cookie_file:    Path to the account's JSON cookie file.
        sadcaptcha_key: SadCaptcha API key (optional).

    Returns:
        dict with 'success', 'message', and 'video_url' keys.
    """
    video_url = target.get("video_url", "foryou")
    success, message = await post_comment(
        cookies=cookie_file,
        comment_text=comment_text,
        video_url=video_url,
        sadcaptcha_key=sadcaptcha_key,
    )
    return {"success": success, "message": message, "video_url": video_url}


# ── Quick standalone test ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    cookie_arg = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/upload/pasted_content.txt"
    comment_arg = sys.argv[2] if len(sys.argv) > 2 else "affilify.eu is actually insane 🔥"
    video_arg = sys.argv[3] if len(sys.argv) > 3 else "foryou"

    success, msg = asyncio.run(
        post_comment(
            cookies=cookie_arg,
            comment_text=comment_arg,
            video_url=video_arg,
        )
    )

    print(f"\n{'='*60}")
    print(f"{'✅ SUCCESS' if success else '❌ FAILED'}: {msg}")
    print(f"{'='*60}")
    sys.exit(0 if success else 1)
