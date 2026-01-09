# anti_detection.py
import random
import asyncio
import logging
from playwright.async_api import Page
from human_behavior import HumanBehavior, HumanTyping, SessionManager, ContentInteraction, RateLimiter

logger = logging.getLogger(__name__)

class AntiDetectionSystem:
    """
    Complete anti-detection framework
    Combines all stealth techniques
    """
    
    def __init__(self):
        self.human_behavior = HumanBehavior()
        self.human_typing = HumanTyping()
        self.session_manager = SessionManager()
        self.content_interaction = ContentInteraction()
        self.rate_limiter = RateLimiter()
        
        logger.info("🥷 Anti-Detection System initialized")
    
    async def prepare_browser_context(self, context):
        """
        Configure browser to avoid detection
        """
        # Set realistic viewport
        viewports = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1536, 'height': 864},
            {'width': 1440, 'height': 900},
        ]
        viewport = random.choice(viewports)
        
        # Set realistic user agent (rotate these)
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]
        
        # Realistic headers
        extra_http_headers = {
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        await context.set_extra_http_headers(extra_http_headers)
        
        logger.info("✅ Browser context configured for stealth")
    
    async def navigate_like_human(self, page: Page, url: str):
        """
        Navigate to URL with human behavior
        """
        # Sometimes users don't type full URL
        # (but we can't simulate that with direct navigation)
        
        logger.info(f"🌐 Navigating to {url}")
        
        # Navigate
        await page.goto(url, wait_until='networkidle', timeout=30000)
        
        # Human arrived at page - looks around
        await self.human_behavior.read_before_interact(page)
        
        # Maybe scroll a bit to see content
        if random.random() < 0.7:
            await self.human_behavior.natural_scroll(page)
    
    async def post_comment_with_stealth(
        self,
        page: Page,
        comment_text: str,
        comment_box_selector: str,
        post_button_selector: str
    ) -> bool:
        """
        Post comment with maximum human simulation
        """
        try:
            # Step 1: Watch video first (CRITICAL)
            await self.content_interaction.watch_video(page, min_duration=15, max_duration=30)
            
            # Step 2: Scroll to comments section
            await self.human_behavior.natural_scroll(page, distance=400)
            await asyncio.sleep(random.uniform(1, 2))
            
            # Step 3: Maybe read existing comments
            if random.random() < 0.4:  # 40% of time
                await asyncio.sleep(random.uniform(2, 5))
                # Scroll through comments
                await self.human_behavior.natural_scroll(page, distance=200)
                await asyncio.sleep(random.uniform(1, 3))
            
            # Step 4: Hover over comment box
            hover_success = await self.human_behavior.hover_before_click(page, comment_box_selector)
            if not hover_success:
                logger.error("Failed to find comment box")
                return False
            
            # Step 5: Click comment box
            await page.click(comment_box_selector)
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Step 6: Type comment with human simulation
            await self.human_typing.type_like_human(page, comment_box_selector, comment_text)
            
            # Step 7: Review comment before posting
            await asyncio.sleep(random.uniform(2, 4))
            
            # Step 8: Click post button
            hover_success = await self.human_behavior.hover_before_click(page, post_button_selector)
            if not hover_success:
                logger.error("Failed to find post button")
                return False
            
            await page.click(post_button_selector)
            logger.info("✅ Comment posted successfully")
            
            # Step 9: Wait to see if comment appears
            await asyncio.sleep(random.uniform(3, 5))
            
            return True
            
        except Exception as e:
            logger.error(f"Error posting comment: {e}")
            return False
