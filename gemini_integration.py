import google.generativeai as genai
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
    
    Creates hyper-targeted, feature-specific comments that convert
    """
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-pro',
            generation_config={
                'temperature': 0.9,  # High creativity
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 200,
            }
        )
        
        # AFFILIFY PRODUCT KNOWLEDGE - THE SECRET WEAPON
        self.affilify_knowledge = """
        AFFILIFY - THE ULTIMATE AI-POWERED AFFILIATE MARKETING PLATFORM
        
        CORE VALUE PROPOSITION:
        Generate high-converting, niche-specific affiliate websites in under 60 seconds.
        1000+ lines of professional code from a single product link.
        
        KEY FEATURES (mention these strategically in comments):
        
        1. AI WEBSITE BUILDER:
           - Single-prompt generation from product URLs
           - 60-second deployment to live websites
           - Deep web scraping extracts REAL product data (specs, prices, features)
           - Generates 1000+ lines of conversion-optimized code
           - Automatic affiliate ID integration into all CTAs
        
        2. AUTOMATED DATA EXTRACTION:
           - No manual data entry
           - Extracts product titles, descriptions, prices, and high-res images
           - Real-time data syncing
        
        3. SEO & CONVERSION OPTIMIZATION:
           - Built-in SEO best practices
           - Mobile-responsive designs
           - High-converting landing page layouts
           - Trust-building elements (reviews, specs, comparisons)
        
        4. AFFILIATE INTEGRATION:
           - Works with Amazon, eBay, AliExpress, and custom affiliate programs
           - Automatic link cloaking
           - Centralized affiliate link management
        
        5. SCALABILITY:
           - Build 100s of niche sites in days, not months
           - Low maintenance overhead
           - Cloud-hosted for speed and reliability
        
        URL: affilify.eu
        """
        
        affilify_logger.main_logger.info("🧠 Gemini Comment Generator initialized with AFFILIFY knowledge")
    
    async def generate_comment(self, video_data: Dict, strategy: str = 'STANDARD') -> str:
        """
        Generate a hyper-targeted comment using Gemini 2.5 Pro
        """
        start = log_start("GenerateGeminiComment", video_id=video_data.get('video_id'), strategy=strategy)
        
        try:
            # Construct the prompt
            prompt = self._build_prompt(video_data, strategy)
            
            # Generate content
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            comment = response.text.strip()
            
            # Clean up comment (remove quotes if AI added them)
            if comment.startswith('"') and comment.endswith('"'):
                comment = comment[1:-1]
            
            log_ai("Gemini", prompt, comment)
            log_end("GenerateGeminiComment", start, True)
            
            return comment
            
        except Exception as e:
            log_error("GeminiGeneration", str(e))
            log_end("GenerateGeminiComment", start, False, error=str(e))
            
            # Fallback to a simple template if AI fails
            return self._get_fallback_comment(video_data)
    
    def _build_prompt(self, video_data: Dict, strategy: str) -> str:
        """
        Build a sophisticated prompt for Gemini
        """
        prompt = f"""
        You are an elite affiliate marketing expert and social media strategist.
        Your goal is to write a high-converting TikTok comment for the following video:
        
        VIDEO CONTEXT:
        - Creator: @{video_data.get('creator_username')}
        - Description: {video_data.get('description')}
        - Views: {video_data.get('views')}
        - Likes: {video_data.get('likes')}
        - Hashtags: {', '.join(video_data.get('hashtags', []))}
        
        STRATEGY: {strategy}
        
        PRODUCT KNOWLEDGE (AFFILIFY):
        {self.affilify_knowledge}
        
        INSTRUCTIONS:
        1. Write a comment that feels 100% human, natural, and engaging.
        2. DO NOT use hashtags.
        3. DO NOT use more than 1-2 emojis.
        4. Keep it under 150 characters.
        5. If strategy is 'GOLDEN_OPPORTUNITY', tag the creator (@{video_data.get('creator_username')}) and ask a question.
        6. Strategically mention AFFILIFY (affilify.eu) or its features IF it adds value to the conversation.
        7. Focus on solving a problem mentioned or implied in the video (e.g., "site building is hard", "need more traffic", "automation").
        8. Use a helpful, "pro-tip" tone rather than a salesy tone.
        
        OUTPUT:
        Only the comment text. No explanations.
        """
        return prompt
    
    def _get_fallback_comment(self, video_data: Dict) -> str:
        """
        Simple fallback templates
        """
        fallbacks = [
            f"Great insights @{video_data.get('creator_username')}! Automation is definitely the way to scale this 🚀",
            "The key is definitely in the data collection part. Saves so much time!",
            "Love this strategy. Have you tried using AI to build the landing pages? Game changer.",
            f"Spot on @{video_data.get('creator_username')}. Scaling this manually is a nightmare, AI tools make it so much easier."
        ]
        return random.choice(fallbacks)

async def test_gemini_integration():
    """
    Test the Gemini integration
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return
    
    generator = GeminiCommentGenerator(api_key)
    
    test_video = {
        'video_id': '123456789',
        'creator_username': 'affiliate_king',
        'description': 'How I build 10 affiliate sites a month using manual research',
        'views': 50000,
        'likes': 2500,
        'hashtags': ['affiliatemarketing', 'sidehustle', 'passiveincome']
    }
    
    print("🤖 Generating test comment...")
    comment = await generator.generate_comment(test_video, strategy='GOLDEN_OPPORTUNITY')
    print(f"📝 Generated Comment: {comment}")
    
    print("\n✅ All tests complete!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_gemini_integration())
