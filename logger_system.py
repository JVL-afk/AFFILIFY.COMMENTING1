# logger_system.py - THE BEATING HEART OF THE SYSTEM

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import colorlog
from logging.handlers import RotatingFileHandler
import threading

class AffillifyLogger:
    """
    Military-grade logging system
    Second-by-second precision
    """
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create specialized log files
        self.main_log = self.log_dir / "main.log"
        self.account_log = self.log_dir / "accounts.log"
        self.comment_log = self.log_dir / "comments.log"
        self.error_log = self.log_dir / "errors.log"
        self.performance_log = self.log_dir / "performance.log"
        self.ai_log = self.log_dir / "ai_decisions.log"
        
        self.setup_loggers()
        
        # Real-time metrics
        self.metrics = {
            'comments_posted': 0,
            'errors_encountered': 0,
            'accounts_active': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # Lock for thread-safe logging
        self.lock = threading.Lock()
        
    def setup_loggers(self):
        """
        Setup multiple specialized loggers
        """
        
        # ============================================
        # MAIN LOGGER - Everything goes here
        # ============================================
        self.main_logger = logging.getLogger('MAIN')
        self.main_logger.setLevel(logging.DEBUG)
        
        # Console handler with colors
        console_handler = colorlog.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)s] %(levelname)-8s%(reset)s '
            '%(log_color)s%(name)-10s%(reset)s %(message)s',
            datefmt='%H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )
        console_handler.setFormatter(console_format)
        
        # File handler with rotation (100MB per file, keep 10 backups)
        file_handler = RotatingFileHandler(
            self.main_log,
            maxBytes=100*1024*1024,  # 100MB
            backupCount=10
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '[%(asctime)s.%(msecs)03d] [%(levelname)-8s] [%(name)-10s] '
            '[Thread-%(thread)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        
        self.main_logger.addHandler(console_handler)
        self.main_logger.addHandler(file_handler)
        
        # ============================================
        # ACCOUNT LOGGER - Account-specific events
        # ============================================
        self.account_logger = logging.getLogger('ACCOUNT')
        self.account_logger.setLevel(logging.DEBUG)
        
        account_handler = RotatingFileHandler(
            self.account_log,
            maxBytes=50*1024*1024,
            backupCount=5
        )
        account_handler.setFormatter(file_format)
        self.account_logger.addHandler(account_handler)
        
        # ============================================
        # COMMENT LOGGER - Every comment tracked
        # ============================================
        self.comment_logger = logging.getLogger('COMMENT')
        self.comment_logger.setLevel(logging.DEBUG)
        
        comment_handler = RotatingFileHandler(
            self.comment_log,
            maxBytes=50*1024*1024,
            backupCount=5
        )
        comment_handler.setFormatter(file_format)
        self.comment_logger.addHandler(comment_handler)
        
        # ============================================
        # ERROR LOGGER - All errors in one place
        # ============================================
        self.error_logger = logging.getLogger('ERROR')
        self.error_logger.setLevel(logging.ERROR)
        
        error_handler = RotatingFileHandler(
            self.error_log,
            maxBytes=50*1024*1024,
            backupCount=5
        )
        error_handler.setFormatter(file_format)
        self.error_logger.addHandler(error_handler)
        
        # ============================================
        # PERFORMANCE LOGGER - Timing & metrics
        # ============================================
        self.perf_logger = logging.getLogger('PERFORMANCE')
        self.perf_logger.setLevel(logging.DEBUG)
        
        perf_handler = RotatingFileHandler(
            self.performance_log,
            maxBytes=50*1024*1024,
            backupCount=5
        )
        perf_handler.setFormatter(file_format)
        self.perf_logger.addHandler(perf_handler)
        
        # ============================================
        # AI LOGGER - All AI decisions and outputs
        # ============================================
        self.ai_logger = logging.getLogger('AI')
        self.ai_logger.setLevel(logging.DEBUG)
        
        ai_handler = RotatingFileHandler(
            self.ai_log,
            maxBytes=50*1024*1024,
            backupCount=5
        )
        ai_handler.setFormatter(file_format)
        self.ai_logger.addHandler(ai_handler)
        
        self.main_logger.info("="*70)
        self.main_logger.info("🚀 AFFILIFY TIKTOK DOMINATION SYSTEM - LOGGING INITIALIZED")
        self.main_logger.info("="*70)
    
    def log_operation_start(self, operation: str, context: Dict[str, Any]):
        """
        Log the start of any operation
        """
        with self.lock:
            self.main_logger.info(f"▶️  START: {operation}")
            self.main_logger.debug(f"   Context: {json.dumps(context, indent=2)}")
            return datetime.now()
    
    def log_operation_end(self, operation: str, start_time: datetime, success: bool, details: Dict = None):
        """
        Log the end of any operation with timing
        """
        with self.lock:
            duration = (datetime.now() - start_time).total_seconds()
            
            status = "✅ SUCCESS" if success else "❌ FAILED"
            self.main_logger.info(f"⏹️  END: {operation} | {status} | Duration: {duration:.2f}s")
            
            if details:
                self.main_logger.debug(f"   Details: {json.dumps(details, indent=2)}")
            
            # Performance tracking
            self.perf_logger.info(f"{operation} | {duration:.3f}s | {'SUCCESS' if success else 'FAILED'}")
    
    def log_account_action(self, username: str, action: str, result: str, metadata: Dict = None):
        """
        Log account-specific actions
        """
        with self.lock:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'username': username,
                'action': action,
                'result': result,
                'metadata': metadata or {}
            }
            
            self.account_logger.info(json.dumps(log_entry))
            
            if result.upper() in ['FAILED', 'ERROR']:
                self.error_logger.error(f"Account {username} | {action} | {result}")
    
    def log_comment(self, account: str, video_url: str, comment: str, success: bool, metadata: Dict = None):
        """
        Log every comment attempt
        """
        with self.lock:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'account': account,
                'video_url': video_url,
                'comment': comment,
                'success': success,
                'metadata': metadata or {}
            }
            
            self.comment_logger.info(json.dumps(log_entry))
            
            if success:
                self.metrics['comments_posted'] += 1
                self.main_logger.info(f"💬 COMMENT POSTED | {account} | {comment[:50]}...")
            else:
                self.metrics['errors_encountered'] += 1
                self.error_logger.error(f"Comment failed | {account} | {video_url}")
    
    def log_ai_decision(self, ai_system: str, input_data: Any, output: Any, metadata: Dict = None):
        """
        Log AI decisions for analysis
        """
        with self.lock:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'ai_system': ai_system,
                'input': str(input_data)[:500],  # Truncate for readability
                'output': str(output)[:500],
                'metadata': metadata or {}
            }
            
            self.ai_logger.info(json.dumps(log_entry))
            self.main_logger.debug(f"🤖 AI ({ai_system}): {str(output)[:100]}...")
    
    def log_error(self, error_type: str, error_message: str, stack_trace: str = None, context: Dict = None):
        """
        Log errors with full context
        """
        with self.lock:
            self.metrics['errors_encountered'] += 1
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'error_type': error_type,
                'message': error_message,
                'stack_trace': stack_trace,
                'context': context or {}
            }
            
            self.error_logger.error(json.dumps(log_entry, indent=2))
            self.main_logger.error(f"🔥 ERROR: {error_type} | {error_message}")
    
    def log_metrics_snapshot(self):
        """
        Log current system metrics
        """
        with self.lock:
            uptime = (datetime.now() - datetime.fromisoformat(self.metrics['start_time'])).total_seconds()
            
            self.main_logger.info("="*70)
            self.main_logger.info("📊 SYSTEM METRICS SNAPSHOT")
            self.main_logger.info(f"   Uptime: {uptime/3600:.2f} hours")
            self.main_logger.info(f"   Comments Posted: {self.metrics['comments_posted']}")
            self.main_logger.info(f"   Errors: {self.metrics['errors_encountered']}")
            self.main_logger.info(f"   Active Accounts: {self.metrics['accounts_active']}")
            self.main_logger.info(f"   Success Rate: {self._calculate_success_rate():.1f}%")
            self.main_logger.info("="*70)
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate"""
        total = self.metrics['comments_posted'] + self.metrics['errors_encountered']
        if total == 0:
            return 100.0
        return (self.metrics['comments_posted'] / total) * 100
    
    def create_session_summary(self) -> Dict:
        """
        Create summary of current session
        """
        with self.lock:
            return {
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': (datetime.now() - datetime.fromisoformat(self.metrics['start_time'])).total_seconds(),
                'metrics': self.metrics.copy(),
                'success_rate': self._calculate_success_rate()
            }


# Global logger instance
affilify_logger = AffillifyLogger()

# Convenience functions
def log_start(operation: str, **context):
    return affilify_logger.log_operation_start(operation, context)

def log_end(operation: str, start_time, success: bool, **details):
    affilify_logger.log_operation_end(operation, start_time, success, details)

def log_account(username: str, action: str, result: str, **metadata):
    affilify_logger.log_account_action(username, action, result, metadata)

def log_comment(account: str, video_url: str, comment: str, success: bool, **metadata):
    affilify_logger.log_comment(account, video_url, comment, success, metadata)

def log_ai(ai_system: str, input_data: Any, output: Any, **metadata):
    affilify_logger.log_ai_decision(ai_system, input_data, output, metadata)

def log_error(error_type: str, message: str, stack_trace: str = None, **context):
    affilify_logger.log_error(error_type, message, stack_trace, context)

def log_metrics():
    affilify_logger.log_metrics_snapshot()
