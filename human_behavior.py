# human_behavior.py

import random
import asyncio
from playwright.async_api import Page

class HumanBehavior:
    """
    Simulates authentic human interaction patterns
    """
    
    @staticmethod
    async def natural_scroll(page: Page, distance: int = None):
        """
        Scroll like a human - not robotic
        """
        if distance is None:
            distance = random.randint(300, 800)
        
        # Humans scroll in chunks, not smooth
        chunks = random.randint(3, 7)
        chunk_size = distance // chunks
        
        for i in range(chunks):
            # Varying scroll speeds
            current_chunk = chunk_size + random.randint(-50, 50)
            await page.mouse.wheel(0, current_chunk)
            
            # Pause between scrolls (humans don't scroll constantly)
            pause = random.uniform(0.1, 0.4)
            
            # Occasionally longer pause (reading something)
            if random.random() < 0.2:
                pause = random.uniform(1.0, 2.5)
            
            await asyncio.sleep(pause)
        
        # Sometimes scroll back up a bit (changed mind)
        if random.random() < 0.15:
            await asyncio.sleep(random.uniform(0.5, 1.0))
            await page.mouse.wheel(0, -random.randint(50, 150))
    
    @staticmethod
    async def hover_before_click(page: Page, selector: str):
        """
        Humans hover before clicking
        """
        element = await page.query_selector(selector)
        if not element:
            return False
        
        # Get element position
        box = await element.bounding_box()
        if not box:
            return False
        
        # Move to element with human-like curve
        center_x = box['x'] + box['width'] / 2
        center_y = box['y'] + box['height'] / 2
        
        # Add slight randomness (humans don't click exact center)
        offset_x = random.randint(-10, 10)
        offset_y = random.randint(-10, 10)
        
        # Move mouse gradually (not instant teleport)
        await page.mouse.move(center_x + offset_x, center_y + offset_y)
        
        # Hover pause (0.3-2 seconds)
        await asyncio.sleep(random.uniform(0.3, 2.0))
        
        return True
    
    @staticmethod
    async def read_before_interact(page: Page, content_selector: str = None):
        """
        Simulate reading page content before interacting
        """
        if content_selector:
            element = await page.query_selector(content_selector)
            if element:
                text = await element.inner_text()
                # Reading time based on content length (250 words/minute)
                word_count = len(text.split())
                reading_time = (word_count / 250) * 60  # seconds
                
                # Apply factor (nobody reads everything)
                actual_time = reading_time * random.uniform(0.2, 0.6)
                actual_time = max(2.0, min(actual_time, 10.0))  # 2-10 seconds
                
                await asyncio.sleep(actual_time)
        else:
            # Generic "looking at page" time
            await asyncio.sleep(random.uniform(2.0, 5.0))
    
    @staticmethod
    async def random_mouse_movement(page: Page, duration: float = 5.0):
        """
        Occasional random mouse movements (humans fidget)
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < duration:
            # Random position on screen
            x = random.randint(100, 1200)
            y = random.randint(100, 700)
            
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Only move 30% of the time
            if random.random() > 0.3:
                breakclass HumanTyping:
    """
    Realistic typing simulation
    """
    
    @staticmethod
    async def type_like_human(page: Page, selector: str, text: str):
        """
        Type character-by-character with human variance
        """
        element = await page.query_selector(selector)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        await element.click()
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        words = text.split(' ')
        
        for word_index, word in enumerate(words):
            # Type word
            for char_index, char in enumerate(word):
                await element.type(char)
                
                # Varying typing speed (40-120 WPM)
                # Average: ~80 WPM = ~400 chars/min = ~0.15 sec/char
                base_delay = 0.15
                variation = random.uniform(0.05, 0.25)
                delay = base_delay * variation
                
                # Occasional slow character (thinking)
                if random.random() < 0.05:
                    delay *= random.uniform(2.0, 4.0)
                
                # First character of word slightly slower
                if char_index == 0:
                    delay *= 1.3
                
                await asyncio.sleep(delay)
                
                # Occasional typo + correction
                if random.random() < 0.03:  # 3% typo rate
                    # Type wrong character
                    wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                    await element.type(wrong_char)
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    
                    # Realize mistake
                    await asyncio.sleep(random.uniform(0.2, 0.6))
                    
                    # Backspace
                    await page.keyboard.press('Backspace')
                    await asyncio.sleep(random.uniform(0.1, 0.2))
                    
                    # Type correct character
                    await element.type(char)
                    await asyncio.sleep(random.uniform(0.1, 0.2))
            
            # Space after word (except last word)
            if word_index < len(words) - 1:
                await element.type(' ')
                await asyncio.sleep(random.uniform(0.15, 0.3))
        
        # Pause after typing (reviewing what was written)
        await asyncio.sleep(random.uniform(1.0, 3.0))class SessionManager:
    """
    Manages realistic session patterns
    """
    
    def __init__(self):
        self.session_durations = []
        self.break_durations = []
    
    def calculate_session_duration(self) -> float:
        """
        Humans have varying session lengths
        """
        # Most sessions: 10-45 minutes
        # Occasional long session: 60-120 minutes
        # Quick sessions: 2-5 minutes
        
        rand = random.random()
        if rand < 0.7:  # 70% normal sessions
            return random.uniform(600, 2700)  # 10-45 minutes
        elif rand < 0.9:  # 20% long sessions
            return random.uniform(3600, 7200)  # 60-120 minutes
        else:  # 10% quick sessions
            return random.uniform(120, 300)  # 2-5 minutes
    
    def calculate_break_duration(self) -> float:
        """
        Breaks between sessions
        """
        # Short break: 2-10 minutes (70%)
        # Medium break: 10-30 minutes (20%)
        # Long break: 30-120 minutes (10%)
        
        rand = random.random()
        if rand < 0.7:
            return random.uniform(120, 600)
        elif rand < 0.9:
            return random.uniform(600, 1800)
        else:
            return random.uniform(1800, 7200)
    
    async def take_break(self, duration: float = None):
        """
        Simulate break between sessions
        """
        if duration is None:
            duration = self.calculate_break_duration()
        
        logger.info(f"☕ Taking break for {duration/60:.1f} minutes")
        await asyncio.sleep(duration)
        logger.info(f"✅ Break complete, resuming activity")class ContentInteraction:
    """
    Realistic content engagement patterns
    """
    
    @staticmethod
    async def watch_video(page: Page, min_duration: int = 10, max_duration: int = 30):
        """
        Watch video with human viewing patterns
        """
        # Random watch duration
        duration = random.uniform(min_duration, max_duration)
        logger.info(f"👀 Watching video for {duration:.1f} seconds")
        
        elapsed = 0
        while elapsed < duration:
            # Random chunk of watching
            chunk = random.uniform(3, 8)
            await asyncio.sleep(chunk)
            elapsed += chunk
            
            # Occasional interactions during watching
            action_roll = random.random()
            
            if action_roll < 0.1:  # 10% - scroll to comments
                await HumanBehavior.natural_scroll(page, distance=300)
                await asyncio.sleep(random.uniform(1, 3))
                await HumanBehavior.natural_scroll(page, distance=-300)  # scroll back
            
            elif action_roll < 0.15:  # 5% - pause/resume video
                # Click video to pause
                video = await page.query_selector('video')
                if video:
                    box = await video.bounding_box()
                    if box:
                        await page.mouse.click(
                            box['x'] + box['width']/2,
                            box['y'] + box['height']/2
                        )
                        await asyncio.sleep(random.uniform(2, 5))
                        await page.mouse.click(
                            box['x'] + box['width']/2,
                            box['y'] + box['height']/2
                        )
            
            elif action_roll < 0.2:  # 5% - check profile
                # Could click on creator's profile
                pass
        
        logger.info(f"✅ Finished watching video")
    
    @staticmethod
    def should_interact(interaction_rate: float = 0.3) -> bool:
        """
        Humans don't interact with every piece of content
        """
        return random.random() < interaction_rateclass RateLimiter:
    """
    Enforce human-like rate limiting
    """
    
    def __init__(self):
        self.actions_per_minute_limit = 8  # Max 8 actions/min
        self.actions_per_hour_limit = 100  # Max 100 actions/hour
        self.recent_actions = []
    
    def can_perform_action(self) -> bool:
        """
        Check if we can perform another action without appearing bot-like
        """
        now = time.time()
        
        # Clean old actions
        self.recent_actions = [
            t for t in self.recent_actions 
            if now - t < 3600  # Last hour
        ]
        
        # Check hourly limit
        if len(self.recent_actions) >= self.actions_per_hour_limit:
            return False
        
        # Check per-minute limit
        last_minute = [t for t in self.recent_actions if now - t < 60]
        if len(last_minute) >= self.actions_per_minute_limit:
            return False
        
        return True
    
    async def wait_before_next_action(self):
        """
        Calculate and wait appropriate time before next action
        """
        # Minimum 2 seconds between ANY actions
        base_wait = random.uniform(2.0, 5.0)
        
        # If we're approaching limits, slow down more
        now = time.time()
        last_minute = [t for t in self.recent_actions if now - t < 60]
        
        if len(last_minute) >= 6:
            # Close to per-minute limit, add delay
            base_wait += random.uniform(5.0, 15.0)
        
        await asyncio.sleep(base_wait)
    
    def record_action(self):
        """Record that an action was performed"""
        self.actions_per_minute = time.time()
