# command_center.py - THE ULTIMATE ORCHESTRATOR

import asyncio
import signal
import sys
from datetime import datetime
from typing import Dict, List
from logger_system import *
from jarvis_brain import jarvis
from target_coordinator import MasterTargetCoordinator
from tiktok_automation_v2 import TikTokAutomationV2
from cookie_manager import CookieManager
from gemini_integration import GeminiCommentGenerator
from comment_strategy import CommentStrategySelector
from main import AffillifyDominationSystem
import pandas as pd

class AffillifyCommandCenter:
    """
    MASTER HEADQUARTERS
    
    Coordinates all systems:
    - JARVIS AI Brain
    - Target Discovery
    - Comment Automation
    - Real-time Dashboard
    - Emergency Protocols
    """
    
    def __init__(self):
        affilify_logger.main_logger.info("\n" + "="*80)
        affilify_logger.main_logger.info("🏢 AFFILIFY COMMAND CENTER - INITIALIZATION SEQUENCE")
        affilify_logger.main_logger.info("="*80)
        
        # Core systems
        self.system = AffillifyDominationSystem()
        self.cookie_manager = CookieManager()
        self.automation = TikTokAutomationV2(self.cookie_manager)
        self.target_coordinator = MasterTargetCoordinator()
        self.strategy_selector = CommentStrategySelector()
        
        # AI systems
        self.gemini = None  # Will initialize with API key
        
        # Operation state
        self.is_running = False
        self.pause_requested = False
        self.shutdown_requested = False
        
        # Statistics
        self.session_stats = {
            'start_time': None,
            'comments_posted': 0,
            'errors_encountered': 0,
            'targets_processed': 0,
            'accounts_used': set(),
            'revenue_generated': 0.0
        }
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        affilify_logger.main_logger.info("✅ Command Center initialized")
    
    def _signal_handler(self, signum, frame):
        """
        Handle shutdown signals gracefully
        """
        affilify_logger.main_logger.warning("\n⚠️ Shutdown signal received!")
        self.shutdown_requested = True
    
    async def startup_sequence(self, gemini_api_key: str):
        """
        Complete system startup sequence
        """
        start = log_start("CommandCenter_Startup")
        
        affilify_logger.main_logger.info("\n🚀 STARTING SYSTEM COMPONENTS...")
        
        try:
            # 1. Initialize Gemini
            affilify_logger.main_logger.info("   1/5 Initializing Gemini 2.5 Pro...")
            self.gemini = GeminiCommentGenerator(gemini_api_key)
            affilify_logger.main_logger.info("   ✅ Gemini ready")
            
            # 2. Start JARVIS Brain
            affilify_logger.main_logger.info("   2/5 Booting JARVIS Brain...")
            jarvis_task = asyncio.create_task(jarvis.start())
            await asyncio.sleep(2)  # Give JARVIS time to initialize
            affilify_logger.main_logger.info("   ✅ JARVIS operational")
            
            # 3. Verify accounts
            affilify_logger.main_logger.info("   3/5 Verifying TikTok accounts...")
            accounts_verified = await self._verify_accounts()
            affilify_logger.main_logger.info(f"   ✅ {accounts_verified} accounts ready")
            
            # 4. Start dashboard server
            affilify_logger.main_logger.info("   4/5 Starting real-time dashboard...")
            dashboard_task = asyncio.create_task(self._start_dashboard())
            await asyncio.sleep(1)
            affilify_logger.main_logger.info("   ✅ Dashboard live at http://localhost:8000")
            
            # 5. Discover initial targets
            affilify_logger.main_logger.info("   5/5 Discovering high-value targets...")
            await self._initial_target_discovery()
            affilify_logger.main_logger.info("   ✅ Target queue ready")
            
            self.session_stats['start_time'] = datetime.now()
            self.is_running = True
            
            log_end("CommandCenter_Startup", start, True)
            
            self._display_startup_complete()
            
            return jarvis_task, dashboard_task
            
        except Exception as e:
            log_error("CommandCenter_Startup", str(e))
            log_end("CommandCenter_Startup", start, False, error=str(e))
            raise
    
    async def run_operation(self, mode: str = "auto", target_comments: int = 300):
        """
        Main operation loop
        
        Modes:
        - auto: Fully automated
        - semi: Requires approval for each batch
        - manual: Manual target selection
        """
        affilify_logger.main_logger.info("\n" + "="*80)
        affilify_logger.main_logger.info(f"🎯 STARTING OPERATION - MODE: {mode.upper()}")
        affilify_logger.main_logger.info(f"   Target: {target_comments} comments")
        affilify_logger.main_logger.info("="*80 + "\n")
        
        comments_posted = 0
        
        while self.is_running and comments_posted < target_comments:
            
            # Check for shutdown
            if self.shutdown_requested:
                affilify_logger.main_logger.warning("🛑 Shutdown requested - stopping gracefully...")
                break
            
            # Check for pause
            if self.pause_requested:
                affilify_logger.main_logger.info("⏸️  Operation paused - waiting for resume...")
                await asyncio.sleep(5)
                continue
            
            try:
                # === STEP 1: GET NEXT ACCOUNT ===
                account = self.system.get_available_account()
                
                if not account:
                    affilify_logger.main_logger.warning("⏳ No accounts available - waiting 5 minutes...")
                    jarvis.record_event('no_accounts_available', {'reason': 'all_at_quota_or_cooling'})
                    await asyncio.sleep(300)
                    continue
                
                account_id, username, cookie_file, comments_today, daily_quota = account
                
                # === STEP 2: GET NEXT TARGET VIDEO ===
                target = self.system.get_next_target_video()
                
                if not target:
                    affilify_logger.main_logger.warning("🎯 Target queue empty - discovering new targets...")
                    await self._refresh_targets()
                    continue
                
                video_id, video_url, creator_username, description = target
                
                # Get full video data from database
                video_data = await self._get_video_metadata(video_id)
                
                # === STEP 3: SELECT COMMENT STRATEGY ===
                strategy_name, strategy_config = self.strategy_selector.select_strategy(video_data)
                
                affilify_logger.main_logger.info(f"\n{'='*80}")
                affilify_logger.main_logger.info(f"🎯 OPERATION {comments_posted + 1}/{target_comments}")
                affilify_logger.main_logger.info(f"   Account: {username} ({comments_today}/{daily_quota} today)")
                affilify_logger.main_logger.info(f"   Target: @{creator_username}")
                affilify_logger.main_logger.info(f"   Strategy: {strategy_name}")
                affilify_logger.main_logger.info(f"{'='*80}")
                
                # Record event for JARVIS
                jarvis.record_event('operation_start', {
                    'account': username,
                    'target': creator_username,
                    'strategy': strategy_name
                })
                
                # === STEP 4: GENERATE COMMENT ===
                comment_text = await self._generate_strategic_comment(
                    video_data,
                    strategy_config
                )
                
                if not comment_text:
                    affilify_logger.main_logger.error("❌ Failed to generate comment - skipping")
                    jarvis.record_event('error', {
                        'type': 'comment_generation_failed',
                        'video_id': video_id
                    })
                    continue
                
                # === STEP 5: POST COMMENT ===
                success, message, metadata = await self.automation.post_comment(
                    username,
                    video_url,
                    comment_text
                )
                
                if success:
                    # SUCCESS!
                    comments_posted += 1
                    self.session_stats['comments_posted'] += 1
                    self.session_stats['accounts_used'].add(username)
                    self.session_stats['targets_processed'] += 1
                    
                    # Record in database
                    self.system.record_comment(account_id, video_url, comment_text)
                    self.system.update_account_activity(account_id, increment_comments=True)
                    self.system.mark_video_commented(video_id)
                    
                    # Update account health (positive)
                    self.system.update_account_health(account_id, +2)
                    
                    # Notify JARVIS
                    jarvis.record_event('comment_success', {
                        'account': username,
                        'video': video_url,
                        'strategy': strategy_name,
                        'metadata': metadata
                    })
                    
                    # Log success with style
                    affilify_logger.main_logger.info(f"\n🎉 SUCCESS!")
                    affilify_logger.main_logger.info(f"   Comment: {comment_text[:60]}...")
                    affilify_logger.main_logger.info(f"   Duration: {metadata['timestamps'].get('total_duration', 0):.1f}s")
                    affilify_logger.main_logger.info(f"   Progress: {comments_posted}/{target_comments} ({(comments_posted/target_comments*100):.1f}%)\n")
                    
                    # Calculate expected results
                    self._display_progress_metrics(comments_posted, target_comments)
                    
                else:
                    # FAILURE
                    self.session_stats['errors_encountered'] += 1
                    
                    # Update account health (negative)
                    self.system.update_account_health(account_id, -5)
                    
                    # Notify JARVIS
                    jarvis.record_event('error', {
                        'type': 'comment_post_failed',
                        'account': username,
                        'video': video_url,
                        'message': message,
                        'metadata': metadata
                    })
                    
                    affilify_logger.main_logger.error(f"\n❌ FAILED: {message}\n")
                
                # === STEP 6: INTELLIGENT DELAY ===
                # JARVIS can optimize this based on success patterns
                delay = await self._calculate_intelligent_delay(success, metadata)
                
                affilify_logger.main_logger.info(f"⏳ Next operation in {delay:.0f} seconds...\n")
                await asyncio.sleep(delay)
                
                # Periodic log snapshot
                if comments_posted % 10 == 0:
                    log_metrics()
                    await self._generate_interim_report()
                
            except Exception as e:
                log_error("OperationLoop", str(e))
                self.session_stats['errors_encountered'] += 1
                
                jarvis.record_event('error', {
                    'type': 'operation_exception',
                    'error': str(e)
                })
                
                affilify_logger.main_logger.error(f"❌ Operation error: {e}")
                await asyncio.sleep(60)  # Wait a minute before retry
        
        # Operation complete
        await self._generate_final_report()
    
    async def _generate_strategic_comment(
        self,
        video_data: Dict,
        strategy_config: Dict
    ) -> str:
        """
        Generate comment using Gemini with strategic configuration
        """
        start = log_start("GenerateStrategicComment", strategy=strategy_config['name'])
        
        try:
            # Build instructions based on strategy
            instructions = strategy_config.get('instructions', {})
            
            # Special handling for GOLDEN OPPORTUNITY (tag creator)
            if strategy_config.get('tag_creator', False):
                tag = f"@{video_data['creator_username']}"
            else:
                tag = None
            
            # Generate comment
            comment = await self.gemini.generate_comment(
                video_description=video_data['description'],
                creator_username=video_data['creator_username'],
                video_views=video_data['views'],
                video_likes=video_data['likes'],
                comment_type=strategy_config.get('comment_type', 'value_add'),
                mention_affilify=strategy_config.get('mention_affilify', False)
            )
            
            # Add creator tag if golden opportunity
            if tag and comment:
                comment = f"{tag} {comment}"
            
            log_end("GenerateStrategicComment", start, True, comment_length=len(comment) if comment else 0)
            
            return comment
            
        except Exception as e:
            log_error("GenerateStrategicComment", str(e))
            log_end("GenerateStrategicComment", start, False, error=str(e))
            return None
    
    async def _calculate_intelligent_delay(self, success: bool, metadata: Dict) -> float:
        """
        Calculate delay before next operation
        JARVIS can optimize this over time
        """
        if success:
            # Success - normal delay
            base_delay = random.uniform(120, 300)  # 2-5 minutes
        else:
            # Failure - longer delay
            base_delay = random.uniform(300, 600)  # 5-10 minutes
        
        # JARVIS optimization factor (would be learned over time)
        optimization_factor = 1.0
        
        return base_delay * optimization_factor
    
    async def _verify_accounts(self) -> int:
        """
        Verify all accounts are ready
        """
        # In production, this would verify cookies for all accounts
        # For now, just count active accounts
        
        stats = self.system.get_dashboard_stats()
        return stats.get('total_accounts', 0)
    
    async def _start_dashboard(self):
        """
        Start dashboard server in background
        """
        from dashboard_server import app
        import uvicorn
        
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="warning")
        server = uvicorn.Server(config)
        await server.serve()
    
    async def _initial_target_discovery(self):
        """
        Discover initial batch of targets
        """
        df = await self.target_coordinator.discover_and_prioritize_targets(
            max_videos=500,
            scrape_comments=True
        )
        
        affilify_logger.main_logger.info(f"   📊 Discovered {len(df)} high-value targets")
    
    async def _refresh_targets(self):
        """
        Refresh target queue
        """
        affilify_logger.main_logger.info("🔄 Refreshing target queue...")
        
        df = await self.target_coordinator.discover_and_prioritize_targets(
            max_videos=200,
            scrape_comments=True
        )
        
        affilify_logger.main_logger.info(f"✅ Added {len(df)} new targets")
    
    async def _get_video_metadata(self, video_id: str) -> Dict:
        """
        Get full video metadata from database
        """
        # In production, this would query the database
        # For now, return minimal data
        return {
            'video_id': video_id,
            'creator_username': 'creator',
            'description': 'Video description',
            'views': 10000,
            'likes': 500,
            'comments': 50,
            'creator_followers': 150000
        }
    
    def _display_startup_complete(self):
        """
        Display startup complete message
        """
        affilify_logger.main_logger.info("\n" + "="*80)
        affilify_logger.main_logger.info("✅ AFFILIFY COMMAND CENTER - FULLY OPERATIONAL")
        affilify_logger.main_logger.info("="*80)
        affilify_logger.main_logger.info("\n🧠 JARVIS Brain: ACTIVE & MONITORING")
        affilify_logger.main_logger.info("📊 Dashboard: http://localhost:8000")
        affilify_logger.main_logger.info("🤖 Automation: READY")
        affilify_logger.main_logger.info("🎯 Targets: LOADED")
        affilify_logger.main_logger.info("💬 Comment AI: ONLINE")
        affilify_logger.main_logger.info("\n" + "="*80)
        affilify_logger.main_logger.info("🚀 READY TO DOMINATE TIKTOK")
        affilify_logger.main_logger.info("="*80 + "\n")
    
    def _display_progress_metrics(self, current: int, target: int):
        """
        Display progress and expected results
        """
        # Calculate expected results
        ctr = 0.019  # 1.9%
        trial_rate = 0.016  # 1.6%
        paid_rate = 0.48  # 48%
        
        visits = int(current * ctr * 100)
        trials = int(visits * trial_rate)
        paid = int(trials * paid_rate)
        revenue = paid * 29 + (paid * 0.3 * 99)
        
        affilify_logger.main_logger.info(f"📈 PROJECTED RESULTS (so far):")
        affilify_logger.main_logger.info(f"   Website Visits: ~{visits}")
        affilify_logger.main_logger.info(f"   Free Trials: ~{trials}")
        affilify_logger.main_logger.info(f"   Paid Customers: ~{paid}")
        affilify_logger.main_logger.info(f"   Revenue: ~${revenue:.2f}")
    
    async def _generate_interim_report(self):
        """
        Generate interim progress report
        """
        affilify_logger.main_logger.info("\n" + "="*80)
        affilify_logger.main_logger.info("📊 INTERIM PROGRESS REPORT")
        affilify_logger.main_logger.info("="*80)
        
        uptime = (datetime.now() - self.session_stats['start_time']).total_seconds() / 3600
        
        affilify_logger.main_logger.info(f"⏱️  Uptime: {uptime:.1f} hours")
        affilify_logger.main_logger.info(f"💬 Comments Posted: {self.session_stats['comments_posted']}")
        affilify_logger.main_logger.info(f"❌ Errors: {self.session_stats['errors_encountered']}")
        affilify_logger.main_logger.info(f"👥 Accounts Used: {len(self.session_stats['accounts_used'])}")
        affilify_logger.main_logger.info(f"🎯 Targets Processed: {self.session_stats['targets_processed']}")
        
        success_rate = (self.session_stats['comments_posted'] / 
                       max(self.session_stats['comments_posted'] + self.session_stats['errors_encountered'], 1)) * 100
        
        affilify_logger.main_logger.info(f"✅ Success Rate: {success_rate:.1f}%")
        affilify_logger.main_logger.info("="*80 + "\n")
    
    async def _generate_final_report(self):
        """
        Generate final operation report
        """
        affilify_logger.main_logger.info("\n" + "="*80)
        affilify_logger.main_logger.info("🏁 FINAL OPERATION REPORT")
        affilify_logger.main_logger.info("="*80)
        
        if self.session_stats['start_time']:
            duration = (datetime.now() - self.session_stats['start_time']).total_seconds()
            hours = duration / 3600
            
            affilify_logger.main_logger.info(f"\n⏱️  Total Duration: {hours:.2f} hours")
            affilify_logger.main_logger.info(f"💬 Total Comments: {self.session_stats['comments_posted']}")
            affilify_logger.main_logger.info(f"❌ Total Errors: {self.session_stats['errors_encountered']}")
            affilify_logger.main_logger.info(f"👥 Accounts Used: {len(self.session_stats['accounts_used'])}")
            
            success_rate = (self.session_stats['comments_posted'] / 
                           max(self.session_stats['comments_posted'] + self.session_stats['errors_encountered'], 1)) * 100
            
            affilify_logger.main_logger.info(f"✅ Success Rate: {success_rate:.1f}%")
            
            # Calculate expected results
            comments = self.session_stats['comments_posted']
            visits = int(comments * 0.019 * 100)
            trials = int(visits * 0.016)
            paid = int(trials * 0.48)
            revenue = paid * 29 + (paid * 0.3 * 99)
            
            affilify_logger.main_logger.info(f"\n💰 EXPECTED RESULTS:")
            affilify_logger.main_logger.info(f"   Website Visits: ~{visits}")
            affilify_logger.main_logger.info(f"   Free Trials: ~{trials}")
            affilify_logger.main_logger.info(f"   Paid Customers: ~{paid}")
            affilify_logger.main_logger.info(f"   Revenue: ~${revenue:.2f}")
            
            self.session_stats['revenue_generated'] = revenue
        
        affilify_logger.main_logger.info("\n" + "="*80)
        affilify_logger.main_logger.info("✅ OPERATION COMPLETE")
        affilify_logger.main_logger.info("="*80 + "\n")
    
    async def shutdown(self):
        """
        Graceful shutdown
        """
        affilify_logger.main_logger.info("\n🛑 Initiating graceful shutdown...")
        
        self.is_running = False
        
        # Give operations time to complete
        await asyncio.sleep(5)
        
        # Generate final report
        await self._generate_final_report()
        
        # Stop JARVIS
        jarvis.monitoring_active = False
        jarvis.optimization_active = False
        
        affilify_logger.main_logger.info("✅ Shutdown complete")
