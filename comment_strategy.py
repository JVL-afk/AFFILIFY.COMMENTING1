# comment_strategy.py - INTELLIGENT COMMENT SELECTION

from typing import Dict, Tuple
from logger_system import *

class CommentStrategySelector:
    """
    Selects optimal comment strategy based on video characteristics
    """
    
    def __init__(self):
        affilify_logger.main_logger.info("🎯 Comment Strategy Selector initialized")
    
    def select_strategy(self, video_data: Dict) -> Tuple[str, Dict]:
        """
        Select best comment strategy for this video
        
        Returns: (strategy_name, strategy_config)
        """
        
        # GOLDEN OPPORTUNITY: Low comment count (<5)
        if video_data.get('low_comment_opportunity', False):
            return self._golden_opportunity_strategy(video_data)
        
        # HIGH VISIBILITY: Viral video (100K+ views)
        elif video_data.get('views', 0) > 100_000:
            return self._viral_video_strategy(video_data)
        
        # VERIFIED CREATOR: Extra credibility
        elif video_data.get('creator_verified', False):
            return self._verified_creator_strategy(video_data)
        
        # FRESH CONTENT: < 6 hours old
        elif video_data.get('hours_old', 24) < 6:
            return self._fresh_content_strategy(video_data)
        
        # DEFAULT: Standard engagement
        else:
            return self._standard_strategy(video_data)
    
    def _golden_opportunity_strategy(self, video_data: Dict) -> Tuple[str, Dict]:
        """
        Strategy for videos with <5 comments
        TAG THE CREATOR for maximum visibility
        """
        strategy = {
            'name': 'GOLDEN_OPPORTUNITY',
            'tag_creator': True,
            'comment_type': 'value_add_with_tag',
            'mention_affilify': True,  # Yes, mention AFFILIFY
            'urgency': 'CRITICAL',  # Post ASAP
            'priority_score': 1000,
            
            'instructions': {
                'tag_format': f"@{video_data['creator_username']}",
                'tone': 'supportive_and_helpful',
                'length': 'medium',  # 60-100 chars
                'emoji_count': 1,
                'call_to_action': True
            }
        }
        
        affilify_logger.main_logger.info(
            f"   🌟 GOLDEN OPPORTUNITY: @{video_data['creator_username']} "
            f"- Tagging creator in comment for maximum visibility!"
        )
        
        return ('GOLDEN_OPPORTUNITY', strategy)
    
    def _viral_video_strategy(self, video_data: Dict) -> Tuple[str, Dict]:
        """
        Strategy for viral videos (100K+ views)
        """
        strategy = {
            'name': 'VIRAL_VIDEO',
            'tag_creator': False,
            'comment_type': 'engagement',  # Ask question or build on point
            'mention_affilify': random.random() < 0.3,  # 30% chance
            'urgency': 'HIGH',
            'priority_score': 800,
            
            'instructions': {
                'tone': 'conversational',
                'length': 'short',  # 40-60 chars
                'emoji_count': random.randint(0, 1),
                'call_to_action': False
            }
        }
        
        return ('VIRAL_VIDEO', strategy)
    
    def _verified_creator_strategy(self, video_data: Dict) -> Tuple[str, Dict]:
        """
        Strategy for verified creators
        """
        strategy = {
            'name': 'VERIFIED_CREATOR',
            'tag_creator': False,
            'comment_type': 'value_add',
            'mention_affilify': random.random() < 0.25,  # 25% chance
            'urgency': 'MEDIUM',
            'priority_score': 700,
            
            'instructions': {
                'tone': 'professional',
                'length': 'medium',
                'emoji_count': 1,
                'call_to_action': False
            }
        }
        
        return ('VERIFIED_CREATOR', strategy)
    
    def _fresh_content_strategy(self, video_data: Dict) -> Tuple[str, Dict]:
        """
        Strategy for very fresh content (< 6 hours)
        """
        strategy = {
            'name': 'FRESH_CONTENT',
            'tag_creator': False,
            'comment_type': 'early_engagement',
            'mention_affilify': random.random() < 0.2,  # 20% chance
            'urgency': 'HIGH',
            'priority_score': 750,
            
            'instructions': {
                'tone': 'enthusiastic',
                'length': 'short',
                'emoji_count': random.randint(1, 2),
                'call_to_action': False
            }
        }
        
        return ('FRESH_CONTENT', strategy)
    
    def _standard_strategy(self, video_data: Dict) -> Tuple[str, Dict]:
        """
        Standard engagement strategy
        """
        strategy = {
            'name': 'STANDARD',
            'tag_creator': False,
            'comment_type': random.choice(['value_add', 'engagement', 'question']),
            'mention_affilify': random.random() < 0.15,  # 15% chance
            'urgency': 'NORMAL',
            'priority_score': 500,
            
            'instructions': {
                'tone': 'helpful',
                'length': 'medium',
                'emoji_count': random.randint(0, 1),
                'call_to_action': False
            }
        }
        
        return ('STANDARD', strategy)
