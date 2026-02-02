# video_filter.py - PRECISION TARGET SELECTION

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
from logger_system import *
import re

class AdvancedVideoFilter:
    """
    Multi-stage filtering system
    Only the BEST targets make it through
    """
    
    def __init__(self):
        self.filter_stats = {
            'total_videos': 0,
            'passed_follower_filter': 0,
            'passed_recency_filter': 0,
            'passed_niche_filter': 0,
            'passed_engagement_filter': 0,
            'final_targets': 0
        }
        
        # Niche keywords for advanced matching
        self.niche_keywords = {
            'high_priority': [
                'affiliate', 'affiliate marketing', 'affiliate program',
                'make money', 'make money online', 'earn money',
                'passive income', 'side hustle', 'online business',
                'digital marketing', 'email marketing'
            ],
            'medium_priority': [
                'entrepreneur', 'business tips', 'marketing strategy',
                'social media', 'content creator', 'monetize',
                'ecommerce', 'dropshipping', 'online sales'
            ],
            'low_priority': [
                'work from home', 'remote work', 'freelance',
                'productivity', 'business growth', 'startup'
            ]
        }
        
        affilify_logger.main_logger.info("🔬 Advanced Video Filter initialized")
    
    async def filter_videos(self, videos: List[Dict], scrape_comments: bool = True) -> pd.DataFrame:
        """
        Multi-stage filtering pipeline
        """
        start = log_start("FilterVideos", total_videos=len(videos))
        
        self.filter_stats['total_videos'] = len(videos)
        
        affilify_logger.main_logger.info("="*70)
        affilify_logger.main_logger.info("🔬 STARTING MULTI-STAGE FILTERING")
        affilify_logger.main_logger.info("="*70)
        
        # Convert to DataFrame for advanced filtering
        df = pd.DataFrame(videos)
        
        if df.empty:
            affilify_logger.main_logger.warning("⚠️ No videos to filter!")
            log_end("FilterVideos", start, False, reason="No videos")
            return df
        
        initial_count = len(df)
        
        # ===== STAGE 1: FOLLOWER COUNT FILTER =====
        affilify_logger.main_logger.info("\n📊 STAGE 1: Follower Count Filter (100K+ only)")
        df = self._filter_by_followers(df)
        self.filter_stats['passed_follower_filter'] = len(df)
        affilify_logger.main_logger.info(
            f"   ✅ Passed: {len(df)}/{initial_count} "
            f"({(len(df)/initial_count*100):.1f}%)"
        )
        
        # ===== STAGE 2: RECENCY FILTER =====
        affilify_logger.main_logger.info("\n⏰ STAGE 2: Recency Filter (< 24 hours)")
        df = self._filter_by_recency(df)
        self.filter_stats['passed_recency_filter'] = len(df)
        affilify_logger.main_logger.info(
            f"   ✅ Passed: {len(df)}/{initial_count} "
            f"({(len(df)/initial_count*100):.1f}%)"
        )
        
        # ===== STAGE 3: NICHE RELEVANCE FILTER =====
        affilify_logger.main_logger.info("\n🎯 STAGE 3: Niche Relevance Filter")
        df = self._filter_by_niche_relevance(df)
        self.filter_stats['passed_niche_filter'] = len(df)
        affilify_logger.main_logger.info(
            f"   ✅ Passed: {len(df)}/{initial_count} "
            f"({(len(df)/initial_count*100):.1f}%)"
        )
        
        # ===== STAGE 4: ENGAGEMENT QUALITY FILTER =====
        affilify_logger.main_logger.info("\n💎 STAGE 4: Engagement Quality Filter")
        df = self._filter_by_engagement(df)
        self.filter_stats['passed_engagement_filter'] = len(df)
        affilify_logger.main_logger.info(
            f"   ✅ Passed: {len(df)}/{initial_count} "
            f"({(len(df)/initial_count*100):.1f}%)"
        )
        
        # ===== STAGE 5: SCRAPE COMMENTS (OPTIONAL) =====
        if scrape_comments and not df.empty:
            affilify_logger.main_logger.info("\n💬 STAGE 5: Comment Analysis")
            df = await self._analyze_comments(df)
        
        # ===== STAGE 6: CALCULATE OPPORTUNITY SCORES =====
        affilify_logger.main_logger.info("\n🎯 STAGE 6: Opportunity Score Calculation")
        df = self._calculate_opportunity_scores(df)
        
        # Sort by opportunity score (highest first)
        df = df.sort_values('opportunity_score', ascending=False)
        
        self.filter_stats['final_targets'] = len(df)
        
        log_end("FilterVideos", start, True, final_targets=len(df))
        
        affilify_logger.main_logger.info("="*70)
        affilify_logger.main_logger.info(f"✅ FILTERING COMPLETE")
        affilify_logger.main_logger.info(f"   Final Targets: {len(df)}")
        affilify_logger.main_logger.info(f"   Success Rate: {(len(df)/initial_count*100):.1f}%")
        affilify_logger.main_logger.info("="*70)
        
        # Log detailed stats
        self._log_filter_statistics(df)
        
        return df
    
    def _filter_by_followers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter: Only creators with 100K+ followers
        """
        filtered = df[df['creator_followers'] >= 100_000].copy()
        
        affilify_logger.main_logger.info(
            f"   Filtered out {len(df) - len(filtered)} videos "
            f"(creators with < 100K followers)"
        )
        
        return filtered
    
    def _filter_by_recency(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter: Only videos < 24 hours old
        """
        filtered = df[df['hours_old'] <= 24].copy()
        
        affilify_logger.main_logger.info(
            f"   Filtered out {len(df) - len(filtered)} videos "
            f"(older than 24 hours)"
        )
        
        return filtered
    
    def _filter_by_niche_relevance(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter: Only videos relevant to target niches
        """
        def calculate_relevance_score(row):
            text = f"{row['description']} {' '.join(row['hashtags'])}".lower()
            
            score = 0
            
            # High priority keywords
            for keyword in self.niche_keywords['high_priority']:
                if keyword in text:
                    score += 10
            
            # Medium priority keywords
            for keyword in self.niche_keywords['medium_priority']:
                if keyword in text:
                    score += 5
            
            # Low priority keywords
            for keyword in self.niche_keywords['low_priority']:
                if keyword in text:
                    score += 2
            
            return score
        
        df['relevance_score'] = df.apply(calculate_relevance_score, axis=1)
        
        # Keep only videos with relevance score > 0
        filtered = df[df['relevance_score'] > 0].copy()
        
        affilify_logger.main_logger.info(
            f"   Filtered out {len(df) - len(filtered)} videos "
            f"(not relevant to target niches)"
        )
        
        # Log top keywords found
        if not filtered.empty:
            avg_score = filtered['relevance_score'].mean()
            affilify_logger.main_logger.info(f"   Average relevance score: {avg_score:.1f}")
        
        return filtered
    
    def _filter_by_engagement(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter: Only videos with good engagement
        """
        # Minimum engagement criteria
        min_engagement_rate = 1.0  # 1% minimum
        min_views = 1000  # At least 1K views
        
        filtered = df[
            (df['engagement_rate'] >= min_engagement_rate) &
            (df['views'] >= min_views)
        ].copy()
        
        affilify_logger.main_logger.info(
            f"   Filtered out {len(df) - len(filtered)} videos "
            f"(low engagement or views)"
        )
        
        return filtered
    
    async def _analyze_comments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze comments on each video
        CRITICAL: Identify low-comment opportunities
        """
        from video_scraper import MilitaryGradeVideoScraper
        
        scraper = MilitaryGradeVideoScraper()
        await scraper.initialize_api()
        
        comment_data = []
        
        for idx, row in df.iterrows():
            video_id = row['video_id']
            current_comment_count = row['comments']
            
            affilify_logger.main_logger.info(
                f"   💬 Analyzing comments for video {idx+1}/{len(df)} "
                f"(Current count: {current_comment_count})"
            )
            
            if current_comment_count <= 20:  # Only scrape if low comment count
                comments = await scraper.scrape_video_comments(video_id, max_comments=50)
                
                comment_data.append({
                    'video_id': video_id,
                    'actual_comment_count': len(comments),
                    'comments': comments,
                    'low_comment_opportunity': len(comments) < 5,
                    'creator_replied': any(c.get('is_creator_reply', False) for c in comments)
                })
            else:
                comment_data.append({
                    'video_id': video_id,
                    'actual_comment_count': current_comment_count,
                    'comments': [],
                    'low_comment_opportunity': False,
                    'creator_replied': False
                })
            
            # Rate limiting
            await asyncio.sleep(random.uniform(2, 4))
        
        # Add comment analysis to DataFrame
        comment_df = pd.DataFrame(comment_data)
        df = df.merge(comment_df, on='video_id', how='left')
        
        # Log golden opportunities
        golden_opps = df[df['low_comment_opportunity'] == True]
        affilify_logger.main_logger.info(
            f"\n   🌟 GOLDEN OPPORTUNITIES FOUND: {len(golden_opps)} videos with <5 comments"
        )
        
        return df
    
    def _calculate_opportunity_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate opportunity score for each video
        Higher score = better target
        """
        def calculate_score(row):
            score = 0
            
            # Base score from engagement rate
            score += row['engagement_rate'] * 10
            
            # Bonus for relevance
            score += row['relevance_score'] * 5
            
            # HUGE BONUS for low comment count (<5 comments)
            if row.get('low_comment_opportunity', False):
                score += 500  # Massive bonus - early engagement opportunity
                affilify_logger.main_logger.info(
                    f"      🌟 GOLDEN TARGET: @{row['creator_username']} "
                    f"({row['creator_followers']:,} followers, {row.get('actual_comment_count', 0)} comments)"
                )
            
            # Bonus for verified creators (more visibility)
            if row.get('creator_verified', False):
                score += 50
            
            # Bonus for high follower count
            follower_bonus = (row['creator_followers'] / 1_000_000) * 20  # Up to 20 points per million
            score += min(follower_bonus, 100)  # Cap at 100
            
            # Bonus for recency (fresher = better)
            if row['hours_old'] < 6:
                score += 50  # Very fresh
            elif row['hours_old'] < 12:
                score += 30
            elif row['hours_old'] < 18:
                score += 15
            
            # Bonus for high views (viral potential)
            if row['views'] > 100_000:
                score += 30
            elif row['views'] > 50_000:
                score += 20
            elif row['views'] > 10_000:
                score += 10
            
            return score
        
        df['opportunity_score'] = df.apply(calculate_score, axis=1)
        
        affilify_logger.main_logger.info(
            f"   📊 Score range: {df['opportunity_score'].min():.0f} - {df['opportunity_score'].max():.0f}"
        )
        affilify_logger.main_logger.info(
            f"   📊 Average score: {df['opportunity_score'].mean():.0f}"
        )
        
        return df
    
    def _log_filter_statistics(self, df: pd.DataFrame):
        """
        Log detailed statistics about filtered videos
        """
        if df.empty:
            return
        
        affilify_logger.main_logger.info("\n📊 DETAILED STATISTICS:")
        affilify_logger.main_logger.info(f"   Total Targets: {len(df)}")
        golden_opps = df[df['low_comment_opportunity'] == True] if 'low_comment_opportunity' in df.columns else pd.DataFrame()
        affilify_logger.main_logger.info(f"   Golden Opportunities (<5 comments): {len(golden_opps)}")
        affilify_logger.main_logger.info(f"   Verified Creators: {len(df[df['creator_verified'] == True])}")
        affilify_logger.main_logger.info(f"   Average Followers: {df['creator_followers'].mean():,.0f}")
        affilify_logger.main_logger.info(f"   Average Views: {df['views'].mean():,.0f}")
        affilify_logger.main_logger.info(f"   Average Engagement Rate: {df['engagement_rate'].mean():.2f}%")
        affilify_logger.main_logger.info(f"   Average Hours Old: {df['hours_old'].mean():.1f}h")
        
        # Top 5 targets
        affilify_logger.main_logger.info("\n🏆 TOP 5 TARGETS:")
        for idx, row in df.head(5).iterrows():
            affilify_logger.main_logger.info(
                f"   {idx+1}. @{row['creator_username']} | "
                f"{row['creator_followers']:,} followers | "
                f"{row['views']:,} views | "
                f"Score: {row['opportunity_score']:.0f} | "
                f"{'🌟 LOW COMMENTS' if row.get('low_comment_opportunity', False) else ''}"
            )
