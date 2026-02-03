from google import genai
from google.genai import types
import os
from typing import Dict, Optional, List
import logging
import random
import asyncio
from logger_system import log_ai, log_error, log_start, log_end, affilify_logger

logger = logging.getLogger(__name__)

class GeminiCommentGenerator:
    """
    Gemini 2.5 Pro powered comment generation
    WITH COMPLETE AFFILIFY PRODUCT KNOWLEDGE
    """
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash'  # Using Flash for higher rate limits
        
        # AFFILIFY PRODUCT KNOWLEDGE
        self.affilify_knowledge = """
        AFFILIFY - THE ULTIMATE AI-POWERED AFFILIATE MARKETING PLATFORM
        URL: affilify.eu
        Generate high-converting affiliate websites in under 60 seconds.
        """
        
        affilify_logger.main_logger.info("🧠 Gemini Comment Generator initialized with AFFILIFY knowledge (Modern SDK)")
    
    async def generate_comment(self, video_data: Dict, strategy: str = 'STANDARD') -> str:
        """
        Generate a hyper-targeted comment using Gemini 2.5 Pro
        """
        start = log_start("GenerateGeminiComment", video_id=video_data.get('video_id'), strategy=strategy)
        
        try:
            prompt = self._build_prompt(video_data, strategy)
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.9,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=200,
                )
            )
            
            comment = response.text.strip()
            
            if comment.startswith('"') and comment.endswith('"'):
                comment = comment[1:-1]
            
            log_ai("Gemini", prompt, comment)
            log_end("GenerateGeminiComment", start, True)
            
            return comment
            
        except Exception as e:
            log_error("GeminiGeneration", str(e))
            log_end("GenerateGeminiComment", start, False, error=str(e))
            return self._get_fallback_comment(video_data)
    
    def _build_prompt(self, video_data: Dict, strategy: str) -> str:
        prompt = f"""
        You are an elite affiliate marketing expert.
        Write a high-converting TikTok comment for:
        Creator: @{video_data.get('creator_username')}
        Description: {video_data.get('description')}
        Strategy: {strategy}
        Product: {self.affilify_knowledge}
        Instructions: Natural, human, no hashtags, <150 chars.
        """
        return prompt
    
    def _get_fallback_comment(self, video_data: Dict) -> str:
        fallbacks = [
            f"Great insights @{video_data.get('creator_username')}! Automation is definitely the way to scale this 🚀",
            "Love this strategy. Have you tried using AI to build the landing pages? Game changer."
        ]
        return random.choice(fallbacks)
