"""
AFFILIFY Comment Engine
=======================
Receives a video URL, cookies, and comment text from the AFFILIFY system.
Executes the exact flow:
  1. Navigate to the video URL (with session warm-up)
  2. Find & click the comment icon  [multi-layer: DOM → Visual AI → coordinates]
  3. Find the comment text box      [multi-layer: DOM → Visual AI → coordinates]
  4. Fill the comment
  5. Click Post                     [multi-layer: DOM → Visual AI → coordinates]
  6. Detect & solve any captcha (SadCaptcha API)
  7. Verify the comment was posted

Element detection uses THREE layers:
  Layer 1 — DOM selectors (fast, exhaustive list)
  Layer 2 — Visual AI scan (Gemini Vision identifies elements by appearance)
  Layer 3 — Coordinate fallback (known screen regions)

Usage (standalone test):
  python3 affilify_comment_engine.py <cookies_file> <comment_text> <video_url>

Usage (from system):
  from affilify_comment_engine import post_comment
  success, message = await post_comment(cookies, comment_text, video_url)
"""

import asyncio
import base64
import json
import os
import sys
import time
from typing import Union

from playwright.async_api import async_playwright, Page

# ── SadCaptcha ────────────────────────────────────────────────────────────────
try:
    from tiktok_captcha_solver import ApiClient as SadCaptchaClient
    SADCAPTCHA_AVAILABLE = True
except ImportError:
    SADCAPTCHA_AVAILABLE = False

SADCAPTCHA_API_KEY = os.environ.get("SADCAPTCHA_API_KEY", "87a671dd2cdd4f843e140115acc8d582")

# ── Gemini Vision (for visual scanning) ───────────────────────────────────────
try:
    from openai import OpenAI as _OpenAI
    _vision_client = _OpenAI()  # uses OPENAI_API_KEY + base_url from env
    VISION_AVAILABLE = True
except Exception:
    VISION_AVAILABLE = False

VISION_MODEL = "gemini-2.5-flash"

# ── DOM Selectors (exhaustive, tried in order) ────────────────────────────────
COMMENT_ICON_SELECTORS = [
    "span[data-e2e='comment-icon']",
    "div[data-e2e='comment-icon']",
    "button[data-e2e='comment-icon']",
    "[data-e2e='browse-comment-icon']",
    "[data-e2e='feed-comment-icon']",
    "button[aria-label*='comment' i]",
    "div[aria-label*='comment' i]",
    "span[aria-label*='comment' i]",
    "div[class*='CommentIcon']",
    "span[class*='CommentIcon']",
    "svg[class*='comment' i]",
    "a[href*='comment']",
]

COMMENT_INPUT_SELECTORS = [
    "div[data-e2e='comment-input'] div[contenteditable='true']",
    "div[contenteditable='true'][data-e2e='comment-input']",
    "div[data-e2e='comment-input']",
    "div[class*='CommentInput'] div[contenteditable='true']",
    "div[class*='comment-input'] div[contenteditable='true']",
    "div[contenteditable='true'][placeholder*='comment' i]",
    "div[contenteditable='true'][aria-label*='comment' i]",
    "textarea[placeholder*='comment' i]",
    "textarea[data-e2e*='comment' i]",
    "input[placeholder*='comment' i]",
    "div[role='textbox'][aria-label*='comment' i]",
    "div[role='textbox']",
    "div[contenteditable='true']",
]

POST_BUTTON_SELECTORS = [
    "div[data-e2e='comment-post']",
    "button[data-e2e='comment-post']",
    "span[data-e2e='comment-post']",
    "div[class*='PostButton']",
    "button[class*='PostButton']",
    "div[class*='post-button' i]",
    "button[class*='post' i][type='submit']",
    "div[class*='post' i][role='button']",
    "button[aria-label*='post' i]",
    "div[aria-label*='post' i]",
]

CAPTCHA_SELECTORS = [
    "#captcha-verify-image",
    "div[id*='captcha']",
    "div[class*='captcha']",
    "div[class*='secsdk-captcha']",
    "div[class*='TUICaptcha']",
    "div[class*='captcha-verify']",
    "canvas[id*='captcha']",
]

LOGIN_BAR_SELECTORS = [
    "div[class*='comment-login-bar']",
    "div[class*='CommentLoginBar']",
    "div[class*='login-bar']",
    "p[class*='login-bar']",
]


# ── Visual AI Scanner ─────────────────────────────────────────────────────────

async def visual_find_element(page: Page, task: str, screenshot_bytes: bytes = None) -> tuple[int, int] | None:
    """
    Use Gemini Vision to find an element on screen.
    Returns (x, y) pixel coordinates of the element center, or None if not found.

    task: natural language description, e.g. "the comment bubble/speech bubble icon"
    """
    if not VISION_AVAILABLE:
        return None

    try:
        if screenshot_bytes is None:
            screenshot_bytes = await page.screenshot(type="png")

        img_b64 = base64.b64encode(screenshot_bytes).decode()

        prompt = (
            f"You are analyzing a screenshot of a TikTok web page (1280x800 pixels). "
            f"Find: {task}. "
            f"Reply ONLY with two integers separated by a comma: the X and Y pixel coordinates "
            f"of the CENTER of that element. "
            f"If you cannot find it, reply with: NOT_FOUND"
        )

        response = _vision_client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            max_tokens=50,
        )

        answer = response.choices[0].message.content.strip()
        if answer == "NOT_FOUND" or "not_found" in answer.lower():
            return None

        parts = answer.replace(" ", "").split(",")
        x, y = int(parts[0]), int(parts[1])
        return (x, y)

    except Exception as e:
        print(f"  [vision] Error: {e}")
        return None


async def find_and_click(page: Page, dom_selectors: list, visual_task: str,
                          fallback_coords: tuple = None, label: str = "") -> bool:
    """
    Multi-layer element finder and clicker.
    Layer 1: Try all DOM selectors.
    Layer 2: Visual AI scan.
    Layer 3: Coordinate fallback.
    Returns True if clicked successfully.
    """
    # Layer 1: DOM selectors
    for sel in dom_selectors:
        try:
            el = await page.query_selector(sel)
            if el and await el.is_visible():
                await el.click(force=True)
                print(f"  ✅ [{label}] DOM selector: {sel}")
                return True
        except Exception:
            continue

    # Layer 2: Visual AI scan
    print(f"  [vision] DOM selectors failed for [{label}], trying visual scan...")
    screenshot_bytes = await page.screenshot(type="png")
    coords = await visual_find_element(page, visual_task, screenshot_bytes)
    if coords:
        x, y = coords
        await page.mouse.click(x, y)
        print(f"  ✅ [{label}] Visual AI found at ({x}, {y})")
        return True

    # Layer 3: Coordinate fallback
    if fallback_coords:
        x, y = fallback_coords
        await page.mouse.click(x, y)
        print(f"  ⚠️  [{label}] Used coordinate fallback ({x}, {y})")
        return True

    print(f"  ❌ [{label}] All detection layers failed")
    return False


async def find_input(page: Page, dom_selectors: list, visual_task: str,
                     fallback_coords: tuple = None, label: str = ""):
    """
    Multi-layer element finder that returns the element (or None).
    For inputs we need the element handle, not just a click.
    """
    # Layer 1: DOM selectors
    for sel in dom_selectors:
        try:
            el = await page.query_selector(sel)
            if el and await el.is_visible():
                print(f"  ✅ [{label}] DOM selector: {sel}")
                return el
        except Exception:
            continue

    # Layer 2: Visual AI — click the found coordinates to focus, return a generic handle
    print(f"  [vision] DOM selectors failed for [{label}], trying visual scan...")
    screenshot_bytes = await page.screenshot(type="png")
    coords = await visual_find_element(page, visual_task, screenshot_bytes)
    if coords:
        x, y = coords
        await page.mouse.click(x, y)
        await asyncio.sleep(0.5)
        # After clicking, the focused element should be the input — get it via JS
        el = await page.evaluate_handle("() => document.activeElement")
        if el:
            print(f"  ✅ [{label}] Visual AI found at ({x}, {y}), using active element")
            return el

    # Layer 3: Coordinate fallback
    if fallback_coords:
        x, y = fallback_coords
        await page.mouse.click(x, y)
        await asyncio.sleep(0.5)
        el = await page.evaluate_handle("() => document.activeElement")
        if el:
            print(f"  ⚠️  [{label}] Coordinate fallback ({x}, {y}), using active element")
            return el

    return None


# ── Cookie helpers ─────────────────────────────────────────────────────────────

def load_cookies(source: Union[str, list]) -> list:
    """Load cookies from a file path or return the list directly."""
    if isinstance(source, list):
        return source
    if isinstance(source, dict):
        return source.get("cookies", [])
    with open(source, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "cookies" in data:
        return data["cookies"]
    raise ValueError(f"Unrecognised cookie format in {source}")


def normalize_cookies(raw: list) -> list:
    """Normalize cookies to Playwright-compatible format."""
    out = []
    for c in raw:
        cookie = {
            "name": c.get("name", ""),
            "value": c.get("value", ""),
            "domain": c.get("domain", ".tiktok.com"),
            "path": c.get("path", "/"),
            "httpOnly": c.get("httpOnly", False),
            "secure": c.get("secure", False),
        }
        # Handle expiry field variants
        exp = c.get("expirationDate") or c.get("expires") or c.get("expiry")
        if exp and exp > 0:
            cookie["expires"] = float(exp)

        # Normalize sameSite
        ss = c.get("sameSite", "")
        if isinstance(ss, str):
            ss_map = {
                "strict": "Strict",
                "lax": "Lax",
                "no_restriction": "None",
                "unspecified": "Lax",
                "none": "None",
            }
            cookie["sameSite"] = ss_map.get(ss.lower(), "Lax")

        if cookie["name"] and cookie["value"]:
            out.append(cookie)
    return out


# ── Overlay / Modal dismissal ─────────────────────────────────────────────────

async def dismiss_overlays(page: Page):
    """
    Aggressively dismiss any modal overlays that TikTok shows
    (e.g. "Introducing keyboard shortcuts", cookie banners, etc.)
    that would intercept pointer events and block our clicks.
    """
    # Selectors for close/dismiss buttons inside modals
    close_selectors = [
        "div[class*='TUXModal'] button",
        "div[class*='TUXModal'] [role='button']",
        "div[class*='modal' i] button[aria-label*='close' i]",
        "div[class*='Modal' i] button[aria-label*='close' i]",
        "button[aria-label='Close']",
        "button[aria-label='close']",
        "[data-testid='modal-close-button']",
        "div[class*='TUXModal-overlay']",
        # Keyboard shortcuts panel ("Introducing keyboard shortcuts!")
        "div[class*='DivShortcutContainer'] button",
        "div[class*='keyboard-shortcut'] button",
        "div[class*='ShortcutTip'] button",
        # Cookie / GDPR banners
        "button[id*='accept' i]",
        "button[class*='accept' i]",
        "div[class*='cookie'] button",
    ]

    dismissed = False
    for sel in close_selectors:
        try:
            el = await page.query_selector(sel)
            if el and await el.is_visible():
                await el.click(force=True)
                print(f"  ✅ [overlay] Dismissed via: {sel}")
                dismissed = True
                await asyncio.sleep(0.5)
                break
        except Exception:
            continue

    # Always press Escape as a safety net — harmless if nothing is open
    try:
        await page.keyboard.press("Escape")
        await asyncio.sleep(0.5)
    except Exception:
        pass

    # If a TUXModal overlay div is covering the screen, remove it via JS
    try:
        removed = await page.evaluate("""
            () => {
                let count = 0;
                // Remove full-screen overlay divs that block pointer events
                document.querySelectorAll(
                    'div[class*="TUXModal"], div[class*="modal-overlay"], div[class*="ModalOverlay"]'
                ).forEach(el => {
                    const style = window.getComputedStyle(el);
                    if (style.position === 'fixed' || style.position === 'absolute') {
                        el.remove();
                        count++;
                    }
                });
                return count;
            }
        """)
        if removed:
            print(f"  ✅ [overlay] Removed {removed} overlay element(s) via JS")
    except Exception:
        pass

    if not dismissed:
        # Try clicking the known position of the keyboard shortcuts × button
        # (top-right corner of the shortcuts panel at ~1229, 384)
        try:
            await page.mouse.click(1229, 384)
            await asyncio.sleep(0.3)
        except Exception:
            pass
        print("  [overlay] Overlay check complete")


# ── Captcha solver ─────────────────────────────────────────────────────────────

async def _human_drag_slider(page: Page, slider_el, distance_px: float):
    """Drag a slider element by a given number of pixels to the right."""
    box = await slider_el.bounding_box()
    if not box:
        print("  [drag] No bounding box for slider — skipping")
        return

    start_x = box["x"] + box["width"] / 2
    start_y = box["y"] + box["height"] / 2
    target_x = start_x + distance_px

    print(f"  [drag] Dragging from ({start_x:.0f},{start_y:.0f}) to ({target_x:.0f},{start_y:.0f}) [{distance_px:.0f}px]")

    # Method 1: Standard mouse drag with hover first
    await page.mouse.move(start_x, start_y)
    await asyncio.sleep(0.5)  # Hover to activate
    await page.mouse.down()
    await asyncio.sleep(0.3)

    steps = 50
    for i in range(steps + 1):
        t = i / steps
        ease = t * t * (3 - 2 * t)  # Smooth step
        cx = start_x + (target_x - start_x) * ease
        cy = start_y + (1 * ((i % 3) - 1))  # Tiny vertical jitter
        await page.mouse.move(cx, cy)
        await asyncio.sleep(0.012 + (0.008 if i % 7 == 0 else 0))

    await page.mouse.move(target_x, start_y)
    await asyncio.sleep(0.2)
    await page.mouse.up()
    await asyncio.sleep(1.5)

    # Check if slider actually moved by reading its position
    new_box = await slider_el.bounding_box()
    if new_box:
        moved = new_box["x"] - box["x"]
        print(f"  [drag] Slider moved by {moved:.0f}px (expected ~{distance_px:.0f}px)")
        if abs(moved) < 5:
            # Slider didn't move — try JS-based drag as fallback
            print("  [drag] Slider didn't move, trying JS dispatchEvent fallback...")
            await page.evaluate("""
                ([startX, startY, endX, endY]) => {
                    const el = document.getElementById('captcha_slide_button') ||
                               document.querySelector('button[id*=slide]') ||
                               document.querySelector('div[class*=captcha] button');
                    if (!el) return;
                    const rect = el.getBoundingClientRect();
                    const cx = rect.left + rect.width / 2;
                    const cy = rect.top + rect.height / 2;
                    
                    const makeEvent = (type, x, y) => new MouseEvent(type, {
                        bubbles: true, cancelable: true,
                        clientX: x, clientY: y,
                        screenX: x, screenY: y,
                        buttons: type === 'mouseup' ? 0 : 1,
                        button: 0,
                    });
                    
                    el.dispatchEvent(makeEvent('mousedown', cx, cy));
                    document.dispatchEvent(makeEvent('mousemove', cx + 10, cy));
                    document.dispatchEvent(makeEvent('mousemove', endX, cy));
                    document.dispatchEvent(makeEvent('mouseup', endX, cy));
                }
            """, [start_x, start_y, target_x, start_y])
            await asyncio.sleep(1.5)


async def _captcha_still_visible(page: Page) -> bool:
    for sel in CAPTCHA_SELECTORS:
        el = await page.query_selector(sel)
        if el and await el.is_visible():
            return True
    return False


async def _img_url_to_b64(page: Page, url: str) -> str | None:
    """
    Fetch an image URL via the browser's fetch() (same origin / cookies)
    and return its base64-encoded content, or None on failure.
    """
    try:
        b64 = await page.evaluate("""
            async (url) => {
                try {
                    const resp = await fetch(url, {credentials: 'include'});
                    if (!resp.ok) return null;
                    const buf = await resp.arrayBuffer();
                    const bytes = new Uint8Array(buf);
                    let binary = '';
                    for (let i = 0; i < bytes.byteLength; i++) {
                        binary += String.fromCharCode(bytes[i]);
                    }
                    return btoa(binary);
                } catch(e) { return null; }
            }
        """, url)
        return b64
    except Exception:
        return None


async def _extract_captcha_images(page: Page) -> list:
    """
    Extract captcha images from the DOM.
    Handles both:
      - Inline base64 (data:image/...) src attributes
      - External URL src attributes (fetched via browser fetch)
    Returns list of dicts: [{b64, len, w, h}, ...]  sorted largest first.
    """
    # Step 1: Grab all img elements inside captcha containers
    img_info = await page.evaluate("""
        () => {
            const imgs = Array.from(document.querySelectorAll(
                'div[class*="captcha"] img, div[id*="captcha"] img, ' +
                '#captcha-verify-image, canvas[id*="captcha"]'
            ));
            return imgs.map(img => ({
                src: img.src || '',
                w: img.offsetWidth,
                h: img.offsetHeight,
                naturalW: img.naturalWidth,
                naturalH: img.naturalHeight,
            }));
        }
    """)

    results = []
    for info in img_info:
        src = info.get("src", "")
        if not src:
            continue

        if src.startswith("data:"):
            # Inline base64
            b64 = src.split(",", 1)[1] if "," in src else None
            if b64 and len(b64) > 500:
                results.append({
                    "b64": b64,
                    "len": len(b64),
                    "w": info.get("w", 0),
                    "h": info.get("h", 0),
                })
        elif src.startswith("http"):
            # External URL — fetch via browser
            b64 = await _img_url_to_b64(page, src)
            if b64 and len(b64) > 500:
                results.append({
                    "b64": b64,
                    "len": len(b64),
                    "w": info.get("w", 0),
                    "h": info.get("h", 0),
                    "url": src,
                })

    # Sort by display area descending (largest display area = outer/background image)
    # This ensures the outer ring (210x210) comes before the inner piece (128x128)
    # even if the inner piece has more bytes
    results.sort(key=lambda x: x.get("w", 0) * x.get("h", 0), reverse=True)
    return results


async def _detect_captcha_type(page: Page) -> str:
    """
    Detect whether the captcha is 'rotation' or 'puzzle'.
    Strategy:
      1. Check the captcha title/heading text (most reliable)
      2. Check image dimensions — rotation has two similar-sized square images,
         puzzle has a wide background + small square piece
      3. Check for type-specific DOM class names
    Returns 'rotation', 'puzzle', or 'unknown'.
    """
    # Strategy 1: Read the captcha title text
    # Rotation: "Drag the slider to fit the puzzle" (but shows circular image)
    # Puzzle-slide: "Drag the slider to complete the puzzle" or similar
    # The most reliable signal is checking if there's a circular/donut image
    try:
        title_text = await page.evaluate("""
            () => {
                const headings = document.querySelectorAll(
                    'div[id*="captcha"] p, div[class*="captcha"] p, '
                    + 'div[id*="captcha"] h1, div[class*="captcha"] h1, '
                    + 'div[id*="captcha"] span, div[class*="captcha"] span'
                );
                for (const h of headings) {
                    const t = h.innerText.trim();
                    if (t.length > 5 && t.length < 200) return t;
                }
                return '';
            }
        """)
        if title_text:
            print(f"  [captcha] Title text: '{title_text}'")
    except Exception:
        title_text = ""

    # Strategy 2: Check image dimensions
    # Rotation captcha: img1 ~210x210, img2 ~128x128 (both roughly square, similar aspect ratio)
    # Puzzle captcha: img1 is wide rectangle (e.g. 340x170), img2 is small square piece
    imgs = await _extract_captcha_images(page)
    if len(imgs) >= 2:
        img1_w, img1_h = imgs[0].get('w', 1), imgs[0].get('h', 1)
        img2_w, img2_h = imgs[1].get('w', 1), imgs[1].get('h', 1)
        # Rotation: both images are roughly square (aspect ratio close to 1)
        # Puzzle: background is wide (aspect ratio > 1.5), piece is square
        bg_aspect = img1_w / max(img1_h, 1)
        if bg_aspect < 1.5:  # roughly square = rotation
            print(f"  [captcha] Image aspect ratio {bg_aspect:.2f} -> ROTATION")
            return "rotation"
        else:  # wide background = puzzle
            print(f"  [captcha] Image aspect ratio {bg_aspect:.2f} -> PUZZLE")
            return "puzzle"
    elif len(imgs) == 1:
        return "rotation"

    # Strategy 3: DOM class name indicators
    rotation_indicators = [
        "div[class*='captcha-verify-img-rotate']",
        "div[class*='rotate-captcha']",
        "div[class*='captcha-rotate']",
        "img[class*='rotate']",
    ]
    for sel in rotation_indicators:
        el = await page.query_selector(sel)
        if el and await el.is_visible():
            print(f"  [captcha] Rotation indicator found: {sel}")
            return "rotation"

    puzzle_indicators = [
        "div[class*='captcha-verify-img-slide']",
        "div[class*='puzzle-captcha']",
        "img[class*='piece']",
    ]
    for sel in puzzle_indicators:
        el = await page.query_selector(sel)
        if el and await el.is_visible():
            print(f"  [captcha] Puzzle indicator found: {sel}")
            return "puzzle"

    return "unknown"


async def solve_captcha(page: Page) -> bool:
    """
    Detect and solve TikTok captcha (rotation or puzzle-slide) using SadCaptcha API.
    Returns True if no captcha present OR captcha was solved successfully.
    """
    if not await _captcha_still_visible(page):
        print("  [captcha] No captcha detected — proceeding")
        return True

    if not SADCAPTCHA_AVAILABLE:
        print("  [captcha] ❌ SadCaptcha not available")
        return False

    # Wait for captcha images to fully load
    print("  [captcha] Waiting for captcha images to load...")
    for _ in range(20):
        imgs = await _extract_captcha_images(page)
        if imgs and imgs[0]["len"] > 1000:
            print(f"  [captcha] Images loaded ({len(imgs)} found, largest={imgs[0]['len']} chars)")
            break
        await asyncio.sleep(1)

    api_client = SadCaptchaClient(SADCAPTCHA_API_KEY)

    # Find the slider element (common to both captcha types)
    # Primary: exact ID used by TikTok's captcha
    slider_el = await page.query_selector("#captcha_slide_button")
    if not slider_el:
        for sel in [
            "button[id*='slide']",
            "div[class*='captcha'] button",
            "div[class*='captcha'] div[class*='slide-btn']",
            "div[class*='captcha'] div[class*='slider-btn']",
            "div[class*='captcha'] div[class*='drag-btn']",
            "div[class*='captcha'] div[role='slider']",
        ]:
            slider_el = await page.query_selector(sel)
            if slider_el and await slider_el.is_visible():
                break

    if slider_el:
        print(f"  [captcha] Slider found: #captcha_slide_button")
    else:
        print(f"  [captcha] ⚠️  Slider not found by DOM, will use coordinate fallback")

    # Find the slider track to know its total width
    # Primary: the full-width rounded container (class contains cap-rounded-full)
    track_el = await page.query_selector("div[class*='cap-rounded-full']")
    if not track_el:
        for sel in [
            "div[class*='captcha'] div[class*='slide-bar']",
            "div[class*='captcha'] div[class*='slider-track']",
            "div[class*='captcha'] div[class*='drag-bar']",
            "div[class*='captcha'] div[class*='bar']",
        ]:
            track_el = await page.query_selector(sel)
            if track_el:
                break

    if track_el:
        tb = await track_el.bounding_box()
        if tb:
            print(f"  [captcha] Track found: {tb['width']:.0f}x{tb['height']:.0f} @({tb['x']:.0f},{tb['y']:.0f})")
    else:
        print(f"  [captcha] ⚠️  Track not found, using default width 348px")

    for attempt in range(3):
        print(f"  [captcha] Attempt {attempt + 1}/3...")
        await asyncio.sleep(1)

        try:
            # Re-query slider fresh on each attempt (element may go stale after drag)
            slider_el = await page.query_selector("#captcha_slide_button")
            if not slider_el:
                for sel in ["button[id*='slide']", "div[class*='captcha'] button"]:
                    slider_el = await page.query_selector(sel)
                    if slider_el and await slider_el.is_visible():
                        break

            # Re-query track too
            track_el = await page.query_selector("div[class*='cap-rounded-full']")
            if track_el:
                tb = await track_el.bounding_box()
                track_width = tb["width"] if tb else 348
            else:
                track_width = 348

            # Detect captcha type
            captcha_type = await _detect_captcha_type(page)
            print(f"  [captcha] Type detected: {captcha_type.upper()}")

            # Wait for images to be large enough (re-load if too small)
            for img_wait in range(10):
                img_data = await _extract_captcha_images(page)
                if img_data and img_data[0]["len"] >= 2000:
                    break
                print(f"  [captcha] Images too small ({img_data[0]['len'] if img_data else 0} chars), waiting...")
                await asyncio.sleep(1)

            if not img_data:
                print("  [captcha] No images found — retrying...")
                await asyncio.sleep(2)
                continue

            print(f"  [captcha] {len(img_data)} image(s): " +
                  ", ".join(f"{d['len']} chars ({d['w']}x{d['h']})" for d in img_data))

            if captcha_type == "rotation":
                # ── Rotation captcha ──────────────────────────────────────────
                # img_data[0] = outer ring (largest), img_data[1] = inner piece
                outer_b64 = img_data[0]["b64"]
                inner_b64 = img_data[1]["b64"] if len(img_data) > 1 else img_data[0]["b64"]
                print(f"  [captcha] Calling SadCaptcha rotate() [outer={img_data[0]['len']} inner={img_data[1]['len'] if len(img_data)>1 else 'same'}]...")
                result = api_client.rotate(outer_b64, inner_b64)
                angle = result.angle
                print(f"  [captcha] SadCaptcha rotation angle = {angle}°")

                # Use track_width already queried above
                # Guard against 360° (means SadCaptcha couldn't determine angle)
                if angle >= 355 or angle <= 5:
                    print(f"  [captcha] Angle {angle}° is invalid (too close to 0/360), retrying...")
                    await asyncio.sleep(2)
                    continue

                distance = track_width * (angle / 360.0)
                print(f"  [captcha] Dragging slider by {distance:.0f}px (track={track_width:.0f}px)")

                if slider_el:
                    await _human_drag_slider(page, slider_el, distance)
                else:
                    # Fallback: drag from known slider position
                    # Slider is at bottom of captcha modal, approximately at y=523
                    await page.mouse.move(470, 523)
                    await asyncio.sleep(0.3)
                    await page.mouse.down()
                    await asyncio.sleep(0.2)
                    steps = 40
                    for i in range(steps + 1):
                        t = i / steps
                        ease = t * t * (3 - 2 * t)
                        await page.mouse.move(470 + distance * ease, 523 + (1 * ((i % 3) - 1)))
                        await asyncio.sleep(0.015)
                    await page.mouse.up()
                    await asyncio.sleep(2)

            elif captcha_type == "puzzle":
                # ── Puzzle-slide captcha ──────────────────────────────────────
                bg_b64 = img_data[0]["b64"]
                piece_b64 = img_data[1]["b64"] if len(img_data) > 1 else bg_b64
                print(f"  [captcha] Calling SadCaptcha puzzle()...")
                result = api_client.puzzle(bg_b64, piece_b64)
                slide_x = result.slide_x_proportion
                print(f"  [captcha] SadCaptcha slide_x_proportion = {slide_x:.3f}")

                if slide_x <= 0:
                    print("  [captcha] slide_x_proportion is 0 — retrying...")
                    await asyncio.sleep(2)
                    continue

                track_width = img_data[0].get("w") or 348
                distance = track_width * slide_x
                print(f"  [captcha] Dragging slider by {distance:.0f}px (track={track_width:.0f}px)")

                if slider_el:
                    await _human_drag_slider(page, slider_el, distance)
                else:
                    await page.mouse.move(500, 523)
                    await asyncio.sleep(0.3)
                    await page.mouse.down()
                    await asyncio.sleep(0.2)
                    steps = 40
                    for i in range(steps + 1):
                        t = i / steps
                        ease = t * t * (3 - 2 * t)
                        await page.mouse.move(500 + distance * ease, 523 + (2 * ((i % 3) - 1)))
                        await asyncio.sleep(0.015)
                    await page.mouse.up()
                    await asyncio.sleep(2)

            else:
                # Unknown type — try puzzle as default
                print("  [captcha] Unknown type — attempting puzzle-slide as default")
                if len(img_data) >= 2:
                    bg_b64 = img_data[0]["b64"]
                    piece_b64 = img_data[1]["b64"]
                    result = api_client.puzzle(bg_b64, piece_b64)
                    slide_x = result.slide_x_proportion
                    track_width = img_data[0].get("w") or 348
                    distance = track_width * slide_x
                    if slider_el:
                        await _human_drag_slider(page, slider_el, distance)
                elif len(img_data) == 1:
                    img_b64 = img_data[0]["b64"]
                    result = api_client.rotate(img_b64, img_b64)
                    angle = result.angle
                    track_width = 340
                    distance = track_width * (angle / 360.0)
                    if slider_el:
                        await _human_drag_slider(page, slider_el, distance)

        except Exception as e:
            print(f"  [captcha] Attempt {attempt + 1} error: {e}")
            await asyncio.sleep(2)

        # Check if captcha is still visible — wait longer for TikTok to process the drag
        await asyncio.sleep(3)
        if not await _captcha_still_visible(page):
            print("  [captcha] ✅ Captcha solved!")
            return True
        # Wait one more second and check again (sometimes there's a brief animation)
        await asyncio.sleep(2)
        if not await _captcha_still_visible(page):
            print("  [captcha] ✅ Captcha solved (delayed)!")
            return True
        print(f"  [captcha] Still visible after attempt {attempt + 1}, retrying...")
        await asyncio.sleep(2)

    print("  [captcha] ❌ Failed to solve captcha after 3 attempts")
    return False


# ── Main engine ───────────────────────────────────────────────────────────────

async def post_comment(
    cookies: Union[str, list],
    comment_text: str,
    video_url: str,
    headless: bool = True,
    screenshot_dir: str = None,
) -> tuple:
    """
    Post a comment on a TikTok video.

    Args:
        cookies:       Path to cookies JSON file, or list of cookie dicts.
        comment_text:  The comment to post.
        video_url:     Full TikTok video URL.
        headless:      Run browser in headless mode (default True).
        screenshot_dir: Optional directory to save debug screenshots.

    Returns:
        (success: bool, message: str)
    """
    if screenshot_dir:
        os.makedirs(screenshot_dir, exist_ok=True)

    async def screenshot(pg, name):
        if screenshot_dir:
            path = os.path.join(screenshot_dir, f"{name}.png")
            await pg.screenshot(path=path)
            print(f"  📸 Screenshot: {path}")

    raw_cookies = load_cookies(cookies)
    playwright_cookies = normalize_cookies(raw_cookies)
    print(f"🍪 Loaded {len(playwright_cookies)} cookies")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-web-security",
            ],
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            locale="en-US",
        )

        # Inject cookies
        await context.add_cookies(playwright_cookies)

        page = await context.new_page()

        # Mask automation signals
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            window.chrome = { runtime: {} };
        """)

        try:
            # ── Step 0: Warm-up — load TikTok homepage to hydrate session ────
            print("🌐 Warming up session on TikTok homepage...")
            await page.goto("https://www.tiktok.com/", wait_until="networkidle", timeout=30000)
            await asyncio.sleep(3)

            # Dismiss any overlays on homepage
            await dismiss_overlays(page)
            await asyncio.sleep(1)

            # Check if session is authenticated
            login_btn = await page.query_selector("button[data-e2e='top-login-button'], a[href*='/login']")
            if login_btn:
                print("  ⚠️  Session may not be authenticated (login button visible)")
            else:
                print("  ✅ Session appears authenticated")

            # ── Step 1: Navigate to the video URL ─────────────────────────────
            print(f"🌐 Navigating to: {video_url}")
            await page.goto(video_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            await screenshot(page, "1_video_page")

            # Dismiss any overlays on video page
            await dismiss_overlays(page)
            await asyncio.sleep(1)

            # Check for login bar (not authenticated)
            for sel in LOGIN_BAR_SELECTORS:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    print("  ⚠️  Login bar detected — session not authenticated for commenting")
                    break

            # ── Step 2: Click the comment icon ────────────────────────────────
            print("💬 Clicking comment icon...")
            clicked = await find_and_click(
                page,
                dom_selectors=COMMENT_ICON_SELECTORS,
                visual_task="the comment bubble / speech bubble icon on the right side of the video",
                fallback_coords=(770, 400),
                label="comment-icon",
            )
            if not clicked:
                return False, "Could not find or click the comment icon"

            await asyncio.sleep(2)
            await screenshot(page, "2_comments_open")

            # ── Step 3: Find the comment text box ─────────────────────────────
            print("🔍 Looking for comment input...")
            comment_input = await find_input(
                page,
                dom_selectors=COMMENT_INPUT_SELECTORS,
                visual_task="the comment text input box at the bottom of the comments panel where users type their comment",
                fallback_coords=(1090, 760),
                label="comment-input",
            )
            if not comment_input:
                await screenshot(page, "error_no_input")
                return False, "Could not find comment input box"

            # ── Step 4: Fill the comment ───────────────────────────────────────
            print(f"✍️  Filling: '{comment_text}'")
            try:
                await comment_input.click(force=True)
                await asyncio.sleep(0.5)
                await comment_input.fill(comment_text)
            except Exception:
                # Fallback: use keyboard typing
                await page.keyboard.type(comment_text, delay=50)
            await asyncio.sleep(1)
            await screenshot(page, "3_comment_filled")

            # ── Step 5: Click Post ─────────────────────────────────────────────
            print("📤 Clicking Post...")
            post_clicked = await find_and_click(
                page,
                dom_selectors=POST_BUTTON_SELECTORS,
                visual_task="the 'Post' button next to the comment input box",
                fallback_coords=(1240, 760),
                label="post-button",
            )
            if not post_clicked:
                # Last resort: press Enter
                await page.keyboard.press("Enter")
                print("  ⚠️  Used Enter key as last resort for Post")

            await asyncio.sleep(2)
            await screenshot(page, "4_after_post")

            # ── Step 6: Detect & solve any captcha ────────────────────────────
            print("🛡️  Checking for captcha...")
            captcha_ok = await solve_captcha(page)
            if not captcha_ok:
                await screenshot(page, "error_captcha_failed")
                return False, "Captcha could not be solved"

            await asyncio.sleep(2)
            await screenshot(page, "5_after_captcha")

            # ── Step 7: Verify the comment was posted ─────────────────────────
            print("🔎 Verifying comment was posted...")

            # Check for success toast
            try:
                toast = await page.wait_for_selector(
                    "div[class*='toast' i], div[class*='Toast' i], div[class*='success' i]",
                    timeout=5000,
                )
                if toast:
                    toast_text = await toast.inner_text()
                    print(f"  ✅ Toast: '{toast_text}'")
                    await screenshot(page, "6_success")
                    return True, f"Comment posted successfully: {toast_text}"
            except Exception:
                pass

            # Check if comment appears in list
            try:
                items = await page.query_selector_all(
                    "div[data-e2e='comment-item'], p[data-e2e='comment-level-1'], div[class*='CommentItem']"
                )
                for item in items:
                    text = await item.inner_text()
                    if comment_text[:20].lower() in text.lower():
                        print(f"  ✅ Comment found in list")
                        await screenshot(page, "6_success")
                        return True, "Comment posted and verified in comments list"
            except Exception:
                pass

            # Check if input is now empty (submitted)
            try:
                input_text = await comment_input.inner_text()
                if not input_text.strip():
                    print("  ✅ Comment input cleared — comment was submitted")
                    await screenshot(page, "6_success")
                    return True, "Comment posted successfully (input cleared)"
            except Exception:
                pass

            await screenshot(page, "6_unverified")
            return True, "Comment posted (no errors detected, could not verify in list)"

        except Exception as e:
            try:
                await screenshot(page, "error_exception")
            except Exception:
                pass
            return False, f"Exception: {e}"

        finally:
            await browser.close()


async def post_comment_for_target(target: dict, cookies: Union[str, list]) -> tuple:
    """
    Convenience wrapper for the AFFILIFY orchestrator.

    Args:
        target: dict with keys 'video_url' and 'comment_text'
        cookies: cookies file path or list

    Returns:
        (success: bool, message: str)
    """
    return await post_comment(
        cookies=cookies,
        comment_text=target["comment_text"],
        video_url=target["video_url"],
    )


# ── Standalone test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 affilify_comment_engine.py <cookies_file> <comment_text> <video_url>")
        print("Example: python3 affilify_comment_engine.py cookies.json 'affilify.eu' 'https://www.tiktok.com/@user/video/123'")
        sys.exit(1)

    cookies_file = sys.argv[1]
    comment = sys.argv[2]
    url = sys.argv[3]

    print("=" * 60)
    print("🚀 AFFILIFY Comment Engine")
    print("=" * 60)
    print(f"📹 Video  : {url}")
    print(f"💬 Comment: '{comment}'")
    print(f"🍪 Cookies: {cookies_file}")
    print("=" * 60)

    success, msg = asyncio.run(
        post_comment(
            cookies=cookies_file,
            comment_text=comment,
            video_url=url,
            headless=True,
            screenshot_dir="/home/ubuntu/diagnostics",
        )
    )

    print("=" * 60)
    if success:
        print(f"✅ SUCCESS: {msg}")
    else:
        print(f"❌ FAILED: {msg}")
    print("=" * 60)
