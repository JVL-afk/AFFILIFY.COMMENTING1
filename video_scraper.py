# video_scraper.py - SURGICAL PRECISION TARGETING

from TikTokApi import TikTokApi
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time
import random
from logger_system import *
import pandas as pd

class MilitaryGradeVideoScraper:
    """
    Elite video discovery system
    Only the highest-value targets
    """
    
    def __init__(self):
        self.api = None
        self.session_cookies = []
        
        # TARGET PARAMETERS
        self.target_criteria = {
            'min_followers': 100_000,  # 100K+ creators only
            'max_video_age_hours': 24,  # Fresh content only
            'target_niches': [
                'affiliate marketing',
                'make money online',
                'passive income',
                'side hustle',
                'online business',
                'digital marketing',
                'entrepreneur',
                'work from home',
                'financial freedom',
                'email marketing',
                'social media marketing',
                'ecommerce',
                'dropshipping',
                'content creation',
                'monetization'
            ]
        }
        
        # HIGH-VALUE OPPORTUNITY: Low comment count
        self.low_comment_threshold = 5  # Videos with <5 comments = golden opportunity
        
        affilify_logger.main_logger.info("🎯 Military-Grade Video Scraper initialized")
    
    async def initialize_api(self):
        """
        Initialize TikTok API with stealth
        """
        start = log_start("InitializeTikTokAPI")
        
        try:
            # Initialize API
            self.api = TikTokApi()
            
            # Add your own cookies here for better results
            # You can export these from your browser after logging into TikTok
            # This makes scraping more reliable
            
            log_end("InitializeTikTokAPI", start, True)
            affilify_logger.main_logger.info("✅ TikTok API ready")
            
        except Exception as e:
            log_error("TikTokAPIInit", str(e))
            log_end("InitializeTikTokAPI", start, False, error=str(e))
            raise
    
    async def search_videos_by_hashtag(self, hashtag: str, max_results: int = 100) -> List[Dict]:
        """
        Search videos by hashtag with full metadata extraction
        """
        start = log_start("SearchByHashtag", hashtag=hashtag, max_results=max_results)
        
        videos = []
        
        try:
            affilify_logger.main_logger.info(f"🔍 Searching hashtag: #{hashtag}")
            
            # Search using TikTok API
            async for video in self.api.hashtag(name=hashtag).videos(count=max_results):
                try:
                    video_data = await self._extract_video_data(video)
                    
                    if video_data:
                        videos.append(video_data)
                        
                        # Log each video found
                        affilify_logger.main_logger.debug(
                            f"   📹 Found: @{video_data['creator_username']} | "
                            f"{video_data['views']:,} views | "
                            f"{video_data['creator_followers']:,} followers"
                        )
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    affilify_logger.main_logger.debug(f"   ⚠️ Error extracting video: {e}")
                    continue
            
            log_end("SearchByHashtag", start, True, videos_found=len(videos))
            affilify_logger.main_logger.info(f"✅ Found {len(videos)} videos for #{hashtag}")
            
            return videos
            
        except Exception as e:
            log_error("SearchByHashtag", str(e), context={'hashtag': hashtag})
            log_end("SearchByHashtag", start, False, error=str(e))
            return []
    
    async def search_videos_by_keyword(self, keyword: str, max_results: int = 100) -> List[Dict]:
        """
        Search videos by keyword
        """
        start = log_start("SearchByKeyword", keyword=keyword, max_results=max_results)
        
        videos = []
        
        try:
            affilify_logger.main_logger.info(f"🔍 Searching keyword: '{keyword}'")
            
            async for video in self.api.search.videos(keyword, count=max_results):
                try:
                    video_data = await self._extract_video_data(video)
                    
                    if video_data:
                        videos.append(video_data)
                    
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    continue
            
            log_end("SearchByKeyword", start, True, videos_found=len(videos))
            return videos
            
        except Exception as e:
            log_error("SearchByKeyword", str(e), context={'keyword': keyword})
            log_end("SearchByKeyword", start, False, error=str(e))
            return []
    
    async def scrape_creator_recent_videos(self, username: str, max_videos: int = 30) -> List[Dict]:
        """
        Scrape recent videos from a specific high-value creator
        """
        start = log_start("ScrapeCreatorVideos", username=username)
        
        videos = []
        
        try:
            affilify_logger.main_logger.info(f"👤 Scraping creator: @{username}")
            
            user = self.api.user(username=username)
            
            async for video in user.videos(count=max_videos):
                try:
                    video_data = await self._extract_video_data(video)
                    
                    if video_data:
                        videos.append(video_data)
                    
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    continue
            
            log_end("ScrapeCreatorVideos", start, True, videos_found=len(videos))
            return videos
            
        except Exception as e:
            log_error("ScrapeCreatorVideos", str(e), context={'username': username})
            log_end("ScrapeCreatorVideos", start, False, error=str(e))
            return []
    
    async def _extract_video_data(self, video) -> Optional[Dict]:
        """
        Extract complete video metadata
        """
        try:
            # Get video info
            video_dict = video.as_dict
            
            # Extract creator info
            author = video_dict.get('author', {})
            stats = video_dict.get('stats', {})
            
            # Parse timestamp
            create_time = video_dict.get('createTime', 0)
            video_datetime = datetime.fromtimestamp(create_time)
            hours_old = (datetime.now() - video_datetime).total_seconds() / 3600
            
            video_data = {
                # Video identifiers
                'video_id': video_dict.get('id'),
                'video_url': f"https://www.tiktok.com/@{author.get('uniqueId')}/video/{video_dict.get('id')}",
                
                # Creator info
                'creator_username': author.get('uniqueId'),
                'creator_nickname': author.get('nickname'),
                'creator_followers': author.get('followerCount', 0),
                'creator_verified': author.get('verified', False),
                
                # Video metadata
                'description': video_dict.get('desc', ''),
                'hashtags': [tag.get('name') for tag in video_dict.get('challenges', [])],
                'music_title': video_dict.get('music', {}).get('title', ''),
                
                # Engagement stats
                'views': stats.get('playCount', 0),
                'likes': stats.get('diggCount', 0),
                'comments': stats.get('commentCount', 0),
                'shares': stats.get('shareCount', 0),
                
                # Timing
                'created_at': video_datetime.isoformat(),
                'hours_old': hours_old,
                
                # Calculated metrics
                'engagement_rate': self._calculate_engagement_rate(stats),
                'comments_per_1k_views': (stats.get('commentCount', 0) / max(stats.get('playCount', 1), 1)) * 1000,
                
                # Discovery metadata
                'discovered_at': datetime.now().isoformat(),
                'scraper_version': '2.0'
            }
            
            return video_data
            
        except Exception as e:
            affilify_logger.main_logger.debug(f"Error extracting video data: {e}")
            return None
    
    def _calculate_engagement_rate(self, stats: Dict) -> float:
        """
        Calculate engagement rate
        """
        views = stats.get('playCount', 0)
        if views == 0:
            return 0.0
        
        likes = stats.get('diggCount', 0)
        comments = stats.get('commentCount', 0)
        shares = stats.get('shareCount', 0)
        
        engagement = likes + (comments * 3) + (shares * 5)  # Weighted
        
        return (engagement / views) * 100
    
    async def scrape_video_comments(self, video_id: str, max_comments: int = 50) -> List[Dict]:
        """
        Scrape comments from a video
        CRITICAL for identifying low-comment opportunities
        """
        start = log_start("ScrapeVideoComments", video_id=video_id)
        
        comments = []
        
        try:
            video = self.api.video(id=video_id)
            
            async for comment in video.comments(count=max_comments):
                try:
                    comment_dict = comment.as_dict
                    
                    comment_data = {
                        'comment_id': comment_dict.get('cid'),
                        'text': comment_dict.get('text'),
                        'likes': comment_dict.get('digg_count', 0),
                        'author_username': comment_dict.get('user', {}).get('unique_id'),
                        'author_nickname': comment_dict.get('user', {}).get('nickname'),
                        'created_at': datetime.fromtimestamp(comment_dict.get('create_time', 0)).isoformat(),
                        'is_creator_reply': comment_dict.get('user', {}).get('unique_id') == comment_dict.get('author_unique_id')
                    }
                    
                    comments.append(comment_data)
                    
                except Exception as e:
                    continue
            
            log_end("ScrapeVideoComments", start, True, comments_found=len(comments))
            
            affilify_logger.main_logger.info(
                f"💬 Scraped {len(comments)} comments from video {video_id}"
            )
            
            return comments
            
        except Exception as e:
            log_error("ScrapeVideoComments", str(e), context={'video_id': video_id})
            log_end("ScrapeVideoComments", start, False, error=str(e))
            return []
    
    async def discover_targets_comprehensive(self, max_videos: int = 500) -> List[Dict]:
        """
        Comprehensive target discovery across all niches
        """
        start = log_start("DiscoverTargets", max_videos=max_videos)
        
        all_videos = []
        
        affilify_logger.main_logger.info("="*70)
        affilify_logger.main_logger.info("🎯 STARTING COMPREHENSIVE TARGET DISCOVERY")
        affilify_logger.main_logger.info("="*70)
        
        # Search each niche keyword
        for keyword in self.target_criteria['target_niches']:
            affilify_logger.main_logger.info(f"\n🔍 Searching niche: {keyword}")
            
            # Search by keyword
            videos = await self.search_videos_by_keyword(keyword, max_results=50)
            all_videos.extend(videos)
            
            # Also search as hashtag
            hashtag_videos = await self.search_videos_by_hashtag(keyword.replace(' ', ''), max_results=50)
            all_videos.extend(hashtag_videos)
            
            # Rate limiting between searches
            await asyncio.sleep(random.uniform(5, 10))
            
            affilify_logger.main_logger.info(f"   📊 Total videos so far: {len(all_videos)}")
        
        # Remove duplicates
        unique_videos = self._deduplicate_videos(all_videos)
        
        log_end("DiscoverTargets", start, True, videos_discovered=len(unique_videos))
        
        affilify_logger.main_logger.info("="*70)
        affilify_logger.main_logger.info(f"✅ DISCOVERY COMPLETE: {len(unique_videos)} unique videos")
        affilify_logger.main_logger.info("="*70)
        
        return unique_videos
    
    def _deduplicate_videos(self, videos: List[Dict]) -> List[Dict]:
        """
        Remove duplicate videos
        """
        seen = set()
        unique = []
        
        for video in videos:
            video_id = video.get('video_id')
            if video_id and video_id not in seen:
                seen.add(video_id)
                unique.append(video)
        
        return unique
