# target_coordinator.py - ORCHESTRATES ENTIRE DISCOVERY PIPELINE

import asyncio
from typing import List, Dict
import pandas as pd
from logger_system import *
from video_scraper import MilitaryGradeVideoScraper
from video_filter import AdvancedVideoFilter
from comment_strategy import CommentStrategySelector

class MasterTargetCoordinator:
    """
    Orchestrates the entire target discovery and selection pipeline
    """
    
    def __init__(self):
        self.scraper = MilitaryGradeVideoScraper()
        self.filter = AdvancedVideoFilter()
        self.strategy_selector = CommentStrategySelector()
        
        affilify_logger.main_logger.info("🎯 Master Target Coordinator initialized")
    
    async def discover_and_prioritize_targets(
        self,
        max_videos: int = 500,
        scrape_comments: bool = True
    ) -> pd.DataFrame:
        """
        Complete pipeline: Discover → Filter → Prioritize → Strategy Selection
        """
        start = log_start("DiscoverAndPrioritizeTargets", max_videos=max_videos)
        
        affilify_logger.main_logger.info("\n" + "="*70)
        affilify_logger.main_logger.info("🚀 MASTER TARGET COORDINATOR - FULL PIPELINE")
        affilify_logger.main_logger.info("="*70)
        
        try:
            # ===== PHASE 1: DISCOVER VIDEOS =====
            affilify_logger.main_logger.info("\n📡 PHASE 1: Video Discovery")
            videos = await self.scraper.discover_targets_comprehensive(max_videos)
            
            if not videos:
                affilify_logger.main_logger.error("❌ No videos discovered!")
                log_end("DiscoverAndPrioritizeTargets", start, False, reason="No videos")
                return pd.DataFrame()
            
            # ===== PHASE 3: FILTER VIDEOS =====
            affilify_logger.main_logger.info("\n🔬 PHASE 2: Advanced Filtering")
            df = await self.filter.filter_videos(videos, scrape_comments=scrape_comments)
            
            if df.empty:
                affilify_logger.main_logger.error("❌ No videos passed filters!")
                log_end("DiscoverAndPrioritizeTargets", start, False, reason="All filtered out")
                return df
            
            # ===== PHASE 4: SELECT STRATEGIES =====
            affilify_logger.main_logger.info("\n🎯 PHASE 3: Strategy Selection")
            strategies = []
            
            for idx, row in df.iterrows():
                strategy_name, strategy_config = self.strategy_selector.select_strategy(row.to_dict())
                strategies.append({
                    'video_id': row['video_id'],
                    'strategy_name': strategy_name,
                    'strategy_config': strategy_config
                })
            
            strategy_df = pd.DataFrame(strategies)
            df = df.merge(strategy_df, on='video_id', how='left')
            
            # ===== PHASE 5: FINAL PRIORITIZATION =====
            affilify_logger.main_logger.info("\n📊 PHASE 4: Final Prioritization")
            df = df.sort_values(['strategy_config'], key=lambda x: x.apply(lambda y: y.get('priority_score', 0)), ascending=False)
            
            # ===== PHASE 6: SAVE TO DATABASE =====
            affilify_logger.main_logger.info("\n💾 PHASE 5: Saving to Database")
            await self._save_targets_to_database(df)
            
            log_end("DiscoverAndPrioritizeTargets", start, True, final_targets=len(df))
            
            # ===== SUCCESS SUMMARY =====
            self._print_success_summary(df)
            
            return df
            
        except Exception as e:
            log_error("TargetCoordinator", str(e))
            log_end("DiscoverAndPrioritizeTargets", start, False, error=str(e))
            return pd.DataFrame()
    
    async def _save_targets_to_database(self, df: pd.DataFrame):
        """
        Save prioritized targets to database
        """
        from main import AffillifyDominationSystem
        
        system = AffillifyDominationSystem()
        
        for idx, row in df.iterrows():
            try:
                system.add_target_video(
                    video_url=row['video_url'],
                    creator_username=row['creator_username'],
                    description=row['description'],
                    views=row['views'],
                    likes=row['likes'],
                    comments=row.get('actual_comment_count', row['comments'])
                )
            except Exception as e:
                affilify_logger.main_logger.debug(f"Video already in database: {row['video_id']}")
        
        affilify_logger.main_logger.info(f"   ✅ Saved {len(df)} targets to database")
    
    def _print_success_summary(self, df: pd.DataFrame):
        """
        Print comprehensive success summary
        """
        affilify_logger.main_logger.info("\n" + "="*70)
        affilify_logger.main_logger.info("✅ TARGETING PIPELINE COMPLETE")
        affilify_logger.main_logger.info("="*70)
        
        total = len(df)
        golden = len(df[df['strategy_name'] == 'GOLDEN_OPPORTUNITY'])
        viral = len(df[df['strategy_name'] == 'VIRAL_VIDEO'])
        verified = len(df[df['strategy_name'] == 'VERIFIED_CREATOR'])
        fresh = len(df[df['strategy_name'] == 'FRESH_CONTENT'])
        standard = len(df[df['strategy_name'] == 'STANDARD'])
        
        affilify_logger.main_logger.info(f"\n📊 FINAL TARGET BREAKDOWN:")
        affilify_logger.main_logger.info(f"   Total Targets: {total}")
        affilify_logger.main_logger.info(f"   🌟 Golden Opportunities: {golden} (<5 comments - TAG CREATOR)")
        affilify_logger.main_logger.info(f"   🔥 Viral Videos: {viral} (100K+ views)")
        affilify_logger.main_logger.info(f"   ✅ Verified Creators: {verified}")
        affilify_logger.main_logger.info(f"   ⚡ Fresh Content: {fresh} (< 6 hours)")
        affilify_logger.main_logger.info(f"   📝 Standard: {standard}")
        
        affilify_logger.main_logger.info(f"\n💰 EXPECTED RESULTS (if we comment on all targets):")
        
        # Calculate expected results
        comments_to_post = total
        ctr = 0.019  # 1.9%
        trial_rate = 0.016  # 1.6%
        paid_rate = 0.48  # 48%
        
        visits = int(comments_to_post * ctr * 100)
        trials = int(visits * trial_rate)
        paid = int(trials * paid_rate)
        revenue_low = paid * 29
        revenue_high = paid * 29 + (paid * 0.3 * 99)
        
        affilify_logger.main_logger.info(f"   Website Visits: ~{visits}")
        affilify_logger.main_logger.info(f"   Free Trials: ~{trials}")
        affilify_logger.main_logger.info(f"   Paid Customers: ~{paid}")
        affilify_logger.main_logger.info(f"   Revenue: ${revenue_low:,} - ${revenue_high:,}")
        
        affilify_logger.main_logger.info("\n" + "="*70)
        affilify_logger.main_logger.info("🎯 READY TO DOMINATE TIKTOK!")
        affilify_logger.main_logger.info("="*70 + "\n")


# Standalone execution
async def main():
    """
    Run target discovery pipeline standalone
    """
    coordinator = MasterTargetCoordinator()
    
    df = await coordinator.discover_and_prioritize_targets(
        max_videos=500,
        scrape_comments=True
    )
    
    # Export to CSV for review
    if not df.empty:
        df.to_csv('prioritized_targets.csv', index=False)
        print(f"\n✅ Results exported to: prioritized_targets.csv")

if __name__ == "__main__":
    asyncio.run(main())
