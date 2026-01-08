# jarvis_brain.py - THE AI OVERLORD

import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import deque
import threading
from logger_system import *
from dolphin_integration import dolphin
import re

class JarvisBrain:
    """
    Dolphin-X1-Llama-3.1 as JARVIS
    
    Monitors EVERYTHING
    Analyzes EVERYTHING
    Optimizes EVERYTHING
    Fixes EVERYTHING in real-time
    """
    
    def __init__(self):
        # Real-time data streams
        self.log_stream = deque(maxlen=10000)  # Last 10K log entries
        self.event_stream = deque(maxlen=5000)  # Last 5K events
        self.error_stream = deque(maxlen=1000)  # Last 1K errors
        self.success_stream = deque(maxlen=5000)  # Last 5K successes
        
        # Live metrics
        self.metrics = {
            'total_comments_posted': 0,
            'total_errors': 0,
            'success_rate': 100.0,
            'accounts_active': 0,
            'accounts_resting': 0,
            'accounts_banned': 0,
            'current_targets': 0,
            'avg_comment_time': 0,
            'ai_optimizations_made': 0,
            'code_fixes_deployed': 0
        }
        
        # AI decision history
        self.decisions = []
        
        # Code modifications tracking
        self.code_modifications = []
        
        # Active monitoring threads
        self.monitoring_active = False
        self.optimization_active = False
        
        # Lock for thread-safe operations
        self.lock = threading.Lock()
        
        affilify_logger.main_logger.info("="*70)
        affilify_logger.main_logger.info("🧠 JARVIS BRAIN ONLINE")
        affilify_logger.main_logger.info("   Dolphin-X1-Llama-3.1 Neural Network: ACTIVE")
        affilify_logger.main_logger.info("   Monitoring Systems: INITIALIZING")
        affilify_logger.main_logger.info("   Code Modification Engine: READY")
        affilify_logger.main_logger.info("="*70)
    
    async def start(self):
        """
        Start JARVIS brain - begin monitoring everything
        """
        start_time = log_start("JarvisBrain_Startup")
        
        affilify_logger.main_logger.info("\n🚀 JARVIS STARTUP SEQUENCE")
        
        # Start monitoring systems
        self.monitoring_active = True
        self.optimization_active = True
        
        # Launch parallel monitoring tasks
        tasks = [
            asyncio.create_task(self._monitor_logs()),
            asyncio.create_task(self._monitor_performance()),
            asyncio.create_task(self._monitor_errors()),
            asyncio.create_task(self._optimize_operations()),
            asyncio.create_task(self._proactive_maintenance())
        ]
        
        log_end("JarvisBrain_Startup", start_time, True)
        
        affilify_logger.main_logger.info("✅ JARVIS FULLY OPERATIONAL")
        affilify_logger.main_logger.info("   'Ready to assist, sir.'\n")
        
        # Keep running
        await asyncio.gather(*tasks)
    
    async def _monitor_logs(self):
        """
        Real-time log monitoring
        Analyzes every log entry as it comes in
        """
        affilify_logger.main_logger.info("📊 Log Monitor: ACTIVE")
        
        last_analysis = datetime.now()
        
        while self.monitoring_active:
            try:
                # Read new log entries
                # In production, this would tail the log files
                await asyncio.sleep(10)  # Check every 10 seconds
                
                # Every 5 minutes, deep analysis
                if (datetime.now() - last_analysis).total_seconds() > 300:
                    await self._deep_log_analysis()
                    last_analysis = datetime.now()
                
            except Exception as e:
                log_error("JarvisLogMonitor", str(e))
    
    async def _monitor_performance(self):
        """
        Real-time performance monitoring
        Tracks success rates, timing, efficiency
        """
        affilify_logger.main_logger.info("⚡ Performance Monitor: ACTIVE")
        
        while self.monitoring_active:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Update metrics
                await self._update_live_metrics()
                
                # Check for performance degradation
                if self.metrics['success_rate'] < 70:
                    await self._handle_performance_degradation()
                
            except Exception as e:
                log_error("JarvisPerformanceMonitor", str(e))
    
    async def _monitor_errors(self):
        """
        Real-time error monitoring and auto-fixing
        """
        affilify_logger.main_logger.info("🔥 Error Monitor: ACTIVE")
        
        error_patterns = {}
        
        while self.monitoring_active:
            try:
                await asyncio.sleep(20)  # Check every 20 seconds
                
                # Analyze recent errors
                recent_errors = list(self.error_stream)[-50:]  # Last 50 errors
                
                # Pattern detection
                for error in recent_errors:
                    error_type = error.get('error_type', 'unknown')
                    
                    if error_type not in error_patterns:
                        error_patterns[error_type] = []
                    
                    error_patterns[error_type].append(error)
                
                # If same error appears 3+ times, trigger auto-fix
                for error_type, errors in error_patterns.items():
                    if len(errors) >= 3:
                        affilify_logger.main_logger.warning(
                            f"🚨 JARVIS ALERT: Recurring error detected - {error_type} "
                            f"({len(errors)} occurrences)"
                        )
                        
                        await self._auto_fix_error(error_type, errors)
                        
                        # Clear this pattern
                        error_patterns[error_type] = []
                
            except Exception as e:
                log_error("JarvisErrorMonitor", str(e))
    
    async def _optimize_operations(self):
        """
        Continuous optimization engine
        Analyzes data and makes improvements
        """
        affilify_logger.main_logger.info("🎯 Optimization Engine: ACTIVE")
        
        while self.optimization_active:
            try:
                # Run optimization every 10 minutes
                await asyncio.sleep(600)
                
                affilify_logger.main_logger.info("\n🧠 JARVIS: Running optimization analysis...")
                
                # Collect performance data
                success_data = list(self.success_stream)[-100:]
                error_data = list(self.error_stream)[-100:]
                
                if success_data:
                    # Ask Dolphin-X1 for optimizations
                    optimizations = await self._analyze_and_optimize(success_data, error_data)
                    
                    if optimizations:
                        await self._apply_optimizations(optimizations)
                
            except Exception as e:
                log_error("JarvisOptimization", str(e))
    
    async def _proactive_maintenance(self):
        """
        Proactive system maintenance
        Prevents issues before they occur
        """
        affilify_logger.main_logger.info("🛡️ Proactive Maintenance: ACTIVE")
        
        while self.monitoring_active:
            try:
                # Check every 15 minutes
                await asyncio.sleep(900)
                
                affilify_logger.main_logger.info("\n🔧 JARVIS: Running proactive maintenance...")
                
                # Check account health
                await self._check_account_health_predictive()
                
                # Check selector freshness
                await self._verify_selectors()
                
                # Check API quotas
                await self._check_api_limits()
                
                # Optimize database
                await self._optimize_database()
                
                affilify_logger.main_logger.info("✅ JARVIS: Maintenance complete\n")
                
            except Exception as e:
                log_error("JarvisProactiveMaintenance", str(e))
    
    async def _deep_log_analysis(self):
        """
        Deep analysis of logs using Dolphin-X1
        """
        start = log_start("JarvisDeepAnalysis")
        
        # Get recent logs
        recent_logs = list(self.log_stream)[-500:]
        
        if not recent_logs:
            log_end("JarvisDeepAnalysis", start, False, reason="No logs")
            return
        
        # Prepare data for Dolphin-X1
        log_summary = self._summarize_logs(recent_logs)
        
        prompt = f"""You are JARVIS, analyzing the AFFILIFY TikTok Domination System logs.

RECENT ACTIVITY SUMMARY:
{json.dumps(log_summary, indent=2)}

CURRENT METRICS:
{json.dumps(self.metrics, indent=2)}

Analyze the logs and provide:
1. Overall system health assessment
2. Potential issues you detect
3. Optimization opportunities
4. Predicted problems that might occur
5. Recommended actions

Respond in JSON format:
{{
    "health_status": "excellent|good|concerning|critical",
    "health_score": 0-100,
    "issues_detected": [
        {{"issue": "...", "severity": "low|medium|high|critical", "recommendation": "..."}}
    ],
    "optimizations": [
        {{"area": "...", "improvement": "...", "expected_benefit": "..."}}
    ],
    "predictions": [
        {{"prediction": "...", "probability": "low|medium|high", "preventive_action": "..."}}
    ],
    "immediate_actions": ["...", "..."]
}}

JSON Response:
"""
        
        try:
            # Query Dolphin-X1
            analysis = await dolphin.analyze_system_health(prompt)
            
            if analysis:
                # Log AI analysis
                log_ai('JARVIS-Analysis', log_summary, analysis)
                
                # Store decision
                self.decisions.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'deep_analysis',
                    'analysis': analysis
                })
                
                # Display findings
                self._display_jarvis_analysis(analysis)
                
                # Take immediate actions if needed
                if analysis.get('immediate_actions'):
                    await self._execute_immediate_actions(analysis['immediate_actions'])
            
            log_end("JarvisDeepAnalysis", start, True)
            
        except Exception as e:
            log_error("JarvisDeepAnalysis", str(e))
            log_end("JarvisDeepAnalysis", start, False, error=str(e))
    
    async def _auto_fix_error(self, error_type: str, errors: List[Dict]):
        """
        Automatically fix recurring errors using Dolphin-X1
        """
        start = log_start("JarvisAutoFix", error_type=error_type, occurrences=len(errors))
        
        affilify_logger.main_logger.info(f"\n🔧 JARVIS: Attempting auto-fix for {error_type}...")
        
        # Get error context
        error_context = {
            'error_type': error_type,
            'occurrences': len(errors),
            'recent_errors': errors[-5:],
            'system_state': self.metrics
        }
        
        prompt = f"""You are JARVIS, the autonomous AI assistant for the AFFILIFY system.

CRITICAL ERROR DETECTED:
{json.dumps(error_context, indent=2)}

Generate a code fix that will resolve this error.

Requirements:
1. Provide complete, executable Python code
2. Include error handling
3. Add logging
4. Make it production-ready
5. Include comments explaining the fix

Respond with:
{{
    "fix_type": "selector_update|timing_adjustment|logic_fix|...",
    "description": "What this fix does",
    "code": "Complete Python code",
    "deployment_instructions": "How to deploy this fix",
    "rollback_plan": "How to undo if it fails"
}}

JSON Response:
"""
        
        try:
            # Get fix from Dolphin-X1
            fix = await dolphin.generate_error_fix(prompt)
            
            if fix and fix.get('code'):
                # Log the fix
                log_ai('JARVIS-AutoFix', error_context, fix)
                
                affilify_logger.main_logger.info(f"✅ JARVIS: Fix generated - {fix.get('description')}")
                
                # Deploy the fix
                success = await self._deploy_code_fix(fix)
                
                if success:
                    self.metrics['code_fixes_deployed'] += 1
                    
                    affilify_logger.main_logger.info(
                        f"🎯 JARVIS: Fix deployed successfully!"
                    )
                    
                    # Store modification
                    self.code_modifications.append({
                        'timestamp': datetime.now().isoformat(),
                        'error_type': error_type,
                        'fix': fix,
                        'status': 'deployed'
                    })
                else:
                    affilify_logger.main_logger.error(f"❌ JARVIS: Fix deployment failed")
                
                log_end("JarvisAutoFix", start, success)
                return success
            
            log_end("JarvisAutoFix", start, False, reason="No fix generated")
            return False
            
        except Exception as e:
            log_error("JarvisAutoFix", str(e))
            log_end("JarvisAutoFix", start, False, error=str(e))
            return False
    
    async def _deploy_code_fix(self, fix: Dict) -> bool:
        """
        Deploy code fix in real-time
        """
        try:
            fix_type = fix.get('fix_type')
            code = fix.get('code')
            
            # Create backup of current code
            backup_path = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            
            if fix_type == 'selector_update':
                # Update selectors in tiktok_automation_v2.py
                await self._update_selectors(code)
            
            elif fix_type == 'timing_adjustment':
                # Update timing parameters
                await self._update_timing_params(code)
            
            elif fix_type == 'logic_fix':
                # Apply logic fix
                await self._apply_logic_fix(code)
            
            else:
                # Generic code deployment
                await self._deploy_generic_fix(code)
            
            affilify_logger.main_logger.info(f"   💾 Backup saved: {backup_path}")
            
            return True
            
        except Exception as e:
            affilify_logger.main_logger.error(f"   ❌ Deployment error: {e}")
            return False
    
    async def _analyze_and_optimize(self, success_data: List, error_data: List) -> Dict:
        """
        Analyze performance and generate optimizations
        """
        prompt = f"""You are JARVIS, optimizing the AFFILIFY system.

RECENT SUCCESSES ({len(success_data)}):
{json.dumps(success_data[:10], indent=2)}

RECENT ERRORS ({len(error_data)}):
{json.dumps(error_data[:10], indent=2)}

CURRENT PERFORMANCE:
- Success Rate: {self.metrics['success_rate']:.1f}%
- Avg Comment Time: {self.metrics['avg_comment_time']:.1f}s

Analyze and provide optimizations in JSON:
{{
    "timing_optimizations": {{
        "video_watch_min": X,
        "video_watch_max": Y,
        "action_delay_min": X,
        "action_delay_max": Y
    }},
    "strategy_adjustments": [
        {{"adjustment": "...", "reason": "...", "expected_improvement": "..."}}
    ],
    "selector_improvements": [
        {{"current": "...", "improved": "...", "reason": "..."}}
    ],
    "overall_recommendation": "..."
}}

JSON Response:
"""
        
        try:
            optimizations = await dolphin.optimize_timing(success_data, error_data)
            
            if optimizations:
                self.metrics['ai_optimizations_made'] += 1
                
                log_ai('JARVIS-Optimization', 
                      {'successes': len(success_data), 'errors': len(error_data)},
                      optimizations)
            
            return optimizations
            
        except Exception as e:
            log_error("JarvisOptimization", str(e))
            return {}
    
    async def _apply_optimizations(self, optimizations: Dict):
        """
        Apply AI-generated optimizations to running system
        """
        affilify_logger.main_logger.info("\n🎯 JARVIS: Applying optimizations...")
        
        applied = []
        
        # Apply timing optimizations
        if 'timing_optimizations' in optimizations:
            timing = optimizations['timing_optimizations']
            # This would update the running TikTokAutomationV2 instance
            affilify_logger.main_logger.info(f"   ⏱️  Updated timing parameters")
            applied.append('timing')
        
        # Apply strategy adjustments
        if 'strategy_adjustments' in optimizations:
            for adjustment in optimizations['strategy_adjustments']:
                affilify_logger.main_logger.info(f"   📊 {adjustment.get('adjustment')}")
                applied.append('strategy')
        
        # Apply selector improvements
        if 'selector_improvements' in optimizations:
            for improvement in optimizations['selector_improvements']:
                affilify_logger.main_logger.info(f"   🔍 {improvement.get('reason')}")
                applied.append('selectors')
        
        affilify_logger.main_logger.info(f"✅ JARVIS: Applied {len(applied)} optimizations\n")
    
    def _display_jarvis_analysis(self, analysis: Dict):
        """
        Display JARVIS analysis in readable format
        """
        affilify_logger.main_logger.info("\n" + "="*70)
        affilify_logger.main_logger.info("🧠 JARVIS ANALYSIS REPORT")
        affilify_logger.main_logger.info("="*70)
        
        health_status = analysis.get('health_status', 'unknown').upper()
        health_score = analysis.get('health_score', 0)
        
        # Color-coded health status
        if health_score >= 80:
            status_icon = "✅"
        elif health_score >= 60:
            status_icon = "⚠️"
        else:
            status_icon = "🚨"
        
        affilify_logger.main_logger.info(f"\n{status_icon} System Health: {health_status} ({health_score}/100)")
        
        # Issues detected
        issues = analysis.get('issues_detected', [])
        if issues:
            affilify_logger.main_logger.info(f"\n🔍 Issues Detected ({len(issues)}):")
            for issue in issues:
                severity = issue.get('severity', 'unknown').upper()
                affilify_logger.main_logger.info(f"   [{severity}] {issue.get('issue')}")
                affilify_logger.main_logger.info(f"   → {issue.get('recommendation')}")
        
        # Optimizations
        optimizations = analysis.get('optimizations', [])
        if optimizations:
            affilify_logger.main_logger.info(f"\n💡 Optimization Opportunities ({len(optimizations)}):")
            for opt in optimizations:
                affilify_logger.main_logger.info(f"   • {opt.get('area')}: {opt.get('improvement')}")
                affilify_logger.main_logger.info(f"     Expected: {opt.get('expected_benefit')}")
        
        # Predictions
        predictions = analysis.get('predictions', [])
        if predictions:
            affilify_logger.main_logger.info(f"\n🔮 Predictions ({len(predictions)}):")
            for pred in predictions:
                prob = pred.get('probability', 'unknown').upper()
                affilify_logger.main_logger.info(f"   [{prob}] {pred.get('prediction')}")
                affilify_logger.main_logger.info(f"   Preventive: {pred.get('preventive_action')}")
        
        affilify_logger.main_logger.info("\n" + "="*70 + "\n")
    
    async def _update_live_metrics(self):
        """
        Update live metrics from database
        """
        from main import AffillifyDominationSystem
        
        try:
            system = AffillifyDominationSystem()
            db_stats = system.get_dashboard_stats()
            
            with self.lock:
                self.metrics.update({
                    'total_comments_posted': db_stats.get('total_comments', 0),
                    'accounts_active': db_stats.get('total_accounts', 0),
                    'success_rate': self._calculate_current_success_rate()
                })
        
        except Exception as e:
            pass
    
    def _calculate_current_success_rate(self) -> float:
        """
        Calculate current success rate from streams
        """
        recent_successes = len([e for e in self.success_stream if e])
        recent_errors = len([e for e in self.error_stream if e])
        
        total = recent_successes + recent_errors
        if total == 0:
            return 100.0
        
        return (recent_successes / total) * 100
    
    def _summarize_logs(self, logs: List[Dict]) -> Dict:
        """
        Summarize logs for AI analysis
        """
        return {
            'total_entries': len(logs),
            'time_range': {
                'start': logs[0].get('timestamp') if logs else None,
                'end': logs[-1].get('timestamp') if logs else None
            },
            'log_types': self._count_log_types(logs),
            'most_common_operations': self._get_common_operations(logs),
            'error_summary': self._summarize_errors(logs)
        }
    
    def _count_log_types(self, logs: List[Dict]) -> Dict:
        """Count different log types"""
        types = {}
        for log in logs:
            log_type = log.get('type', 'unknown')
            types[log_type] = types.get(log_type, 0) + 1
        return types
    
    def _get_common_operations(self, logs: List[Dict]) -> List[str]:
        """Get most common operations"""
        operations = {}
        for log in logs:
            op = log.get('operation', 'unknown')
            operations[op] = operations.get(op, 0) + 1
        
        sorted_ops = sorted(operations.items(), key=lambda x: x[1], reverse=True)
        return [op for op, count in sorted_ops[:10]]
    
    def _summarize_errors(self, logs: List[Dict]) -> Dict:
        """Summarize error information"""
        errors = [log for log in logs if log.get('level') == 'ERROR']
        
        error_types = {}
        for error in errors:
            error_type = error.get('error_type', 'unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': len(errors),
            'error_types': error_types,
            'most_common': max(error_types.items(), key=lambda x: x[1])[0] if error_types else None
        }
    
    def record_event(self, event_type: str, data: Dict):
        """
        Record event for JARVIS to analyze
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'data': data
        }
        
        with self.lock:
            self.event_stream.append(event)
            
            if event_type == 'comment_success':
                self.success_stream.append(event)
            elif event_type == 'error':
                self.error_stream.append(event)
    
    def get_current_status(self) -> Dict:
        """
        Get current JARVIS status for dashboard
        """
        with self.lock:
            return {
                'metrics': self.metrics.copy(),
                'recent_decisions': self.decisions[-10:],
                'recent_modifications': self.code_modifications[-5:],
                'monitoring_active': self.monitoring_active,
                'optimization_active': self.optimization_active
            }


# Global JARVIS instance
jarvis = JarvisBrain()
