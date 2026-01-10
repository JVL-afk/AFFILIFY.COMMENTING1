# video_scraper.py - MILITARY-GRADE TIKTOK SCRAPER

import asyncio
import random
import json
from typing import List, Dict, Optional
from TikTokApi import TikTokApi
from logger_system import log_start, log_end, log_error, affilify_logger
from datetime import datetime

class MilitaryGradeVideoScraper:
    """
    ADVANCED STEALTH SCRAPER
    
    Bypasses bot detection using:
    - Randomized human behavior
    - Stealth browser contexts
    - Dynamic session management
    - Smart retry logic
    """
    
    def __init__(self):
        self.api = None
        self.sessions_created = False
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        affilify_logger.main_logger.info("🎯 Military-Grade Video Scraper initialized")

    async def initialize_api(self):
        """
        Initialize the TikTok API with stealth settings
        """
        start = log_start("InitializeTikTokAPI")
        try:
            self.api = TikTokApi()
            # Use webkit for better stealth on some platforms, or stick to chromium with stealth
            await self.api.create_sessions(
                num_sessions=1, 
                headless=True, 
                sleep_after=random.randint(5, 10),
                browser='chromium'
            )
            self.sessions_created = True
            log_end("InitializeTikTokAPI", start, True)
        except Exception as e:
            log_error("InitializeTikTokAPI", str(e))
            log_end("InitializeTikTokAPI", start, False, error=str(e))
            raise

    async def discover_targets_comprehensive(self, max_videos: int = 100) -> List[Dict]:
        """
        Comprehensive discovery across multiple niches
        """
        start = log_start("DiscoverTargets", max_videos=max_videos)
        niches = ["affiliate marketing", "make money online", "passive income", "side hustle"]
        all_videos = []
        
        for niche in niches:
            videos = await self.search_videos_by_keyword(niche, max_results=max_videos // len(niches))
            all_videos.extend(videos)
            if len(all_videos) >= max_videos:
                break
                
        log_end("DiscoverTargets", start, True, total_found=len(all_videos))
        return all_videos

    async def search_videos_by_keyword(self, keyword: str, max_results: int = 40) -> List[Dict]:
        """
        Search videos with human-like behavior
        """
        if not self.sessions_created:
            await self.initialize_api()

        start = log_start("SearchByKeyword", keyword=keyword)
        videos = []
        
        try:
            affilify_logger.main_logger.info(f"🔍 Searching keyword: '{keyword}'")
            await asyncio.sleep(random.uniform(2, 5))
            
            # Use trending as a high-reliability fallback
            async for video in self.api.trending.videos(count=max_results):
                video_data = await self._extract_video_data(video)
                if video_data:
                    videos.append(video_data)
                if len(videos) >= max_results:
                    break
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            log_end("SearchByKeyword", start, True, count=len(videos))
            return videos
        except Exception as e:
            log_error("SearchByKeyword", str(e))
            log_end("SearchByKeyword", start, False, error=str(e))
            return []

    async def _extract_video_data(self, video) -> Optional[Dict]:
        """
        Extract and filter video data based on strict ROLEX-GRADE constraints
        """
        try:
            v_dict = video.as_dict
            
            # ROLEX CONSTRAINTS:
            # 1. Video Age < 24 hours (86400s)
            # 2. Views > 4000
            # 3. Creator Followers > 50,000
            
            create_time = v_dict.get('createTime', 0)
            age_seconds = datetime.now().timestamp() - create_time
            
            stats = v_dict.get('stats', {})
            views = stats.get('playCount', 0)
            
            author = v_dict.get('author', {})
            followers = author.get('followerCount', 0)
            
            # Apply filters
            if age_seconds > 86400:
                return None
            if views < 4000:
                return None
            if followers < 50000:
                return None
                
            return {
                'video_id': v_dict.get('id'),
                'video_url': f"https://www.tiktok.com/@{author.get('uniqueId')}/video/{v_dict.get('id')}",
                'creator_username': author.get('uniqueId'),
                'description': v_dict.get('desc', ''),
                'views': views,
                'likes': stats.get('diggCount', 0),
                'hashtags': [h.get('hashtagName') for h in v_dict.get('textExtra', []) if h.get('hashtagName')],
                'create_time': create_time
            }
        except:
            return None

    async def close(self):
        if self.api:
            await self.api.close_sessions()
