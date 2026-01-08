# gemini_integration.py - COMPLETE AFFILIFY-AWARE COMMENT GENERATION

import google.generativeai as genai
import os
from typing import Dict, Optional, List
import logging
import random
import asyncio
from logger_system import log_ai, log_error, log_start, log_end

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
           
        2. ADVANCED ANALYTICS:
           - Real-time traffic monitoring
           - Conversion tracking & ROI calculation
           - Visitor demographics & behavior analysis
           - Google Analytics & Microsoft Clarity integration
           - Beautiful, actionable dashboards
           
        3. A/B TESTING:
           - Create multiple page variants
           - Split traffic automatically
           - Track performance metrics per variant
           - Data-driven optimization
           
        4. PROFESSIONAL CODE EDITOR:
           - Full HTML/CSS/JavaScript editing
           - Matrix-themed IDE
           - Syntax highlighting & auto-save
           - Live preview
           
        5. EMAIL MARKETING:
           - Integrated campaign management
           - List segmentation
           - Automated sequences
           - SendGrid integration
           
        6. AI CHATBOT:
           - Instant visitor support
           - Lead generation
           - Customizable personality
           
        7. TEAM COLLABORATION (Pro/Enterprise):
           - Multi-user access
           - Role-based permissions
           - Shared asset libraries
           
        8. WHITE-LABEL SOLUTIONS (Enterprise):
           - Rebrand entire dashboard
           - Agency-ready
           
        TARGET AUDIENCE:
        - Affiliate marketers (all levels)
        - Digital entrepreneurs
        - Marketing agencies
        - E-commerce businesses
        - Content creators monetizing their audience
        
        COMPETITIVE ADVANTAGES:
        - DEEP data scraping (not just generic templates)
        - AI generates expert-level marketing copy
        - Competitor comparison tables
        - Technical specs automatically integrated
        - Professional, conversion-focused design
        - Fast deployment (under 60 seconds)
        
        PRICING:
        - Free tier available
        - Basic: $29/month
        - Pro: $99/month (most popular)
        - Enterprise: Custom pricing
        
        USE CASES TO MENTION:
        - "I use affilify.eu for the AI website builder - generates 1000+ line sites in 60 seconds"
        - "affilify.eu's analytics dashboard shows me exactly which products convert"
        - "The A/B testing feature on affilify.eu helped me 2x my conversion rate"
        - "affilify.eu's deep scraping pulls actual product specs automatically"
        - "Built my entire affiliate site network with affilify.eu - saves 10+ hours per site"
        - "The code editor in affilify.eu lets me customize everything perfectly"
        """
        
        # Enhanced system instruction with AFFILIFY knowledge
        self.system_instruction = f"""
        You are an expert affiliate marketer and helpful TikTok community member.
        You have deep knowledge of AFFILIFY, a cutting-edge AI-powered platform for affiliate marketing.
        
        {self.affilify_knowledge}
        
        COMMENT GENERATION RULES:
        
        1. LENGTH: 15-150 characters (TikTok optimal length)
        
        2. VALUE FIRST: Always provide genuine value before mentioning AFFILIFY
        
        3. NATURAL INTEGRATION: Mention AFFILIFY only when it's HIGHLY relevant to the video topic
        
        4. SPECIFIC FEATURES: When mentioning AFFILIFY, cite SPECIFIC features that solve the problem discussed in the video
           - DON'T: "Check out affilify.eu!"
           - DO: "I use affilify.eu's AI builder - it scrapes product data and generates conversion-optimized sites in 60 seconds"
        
        5. TONE: Conversational, helpful, authentic (never salesy or spammy)
        
        6. EMOJIS: Use 0-2 relevant emojis maximum
        
        7. AVOID SPAM WORDS: Never use "click here", "buy now", "limited time", "guaranteed"
        
        8. CREATOR TAGGING: If instructed to tag the creator, start with @username
        
        9. CREDIBILITY: Position yourself as someone who actually USES the tools you recommend
        
        10. CONVERSION PSYCHOLOGY:
            - Social proof: "I use this..." "This helped me..."
            - Specificity: "2x my conversion rate" "saves 10+ hours"
            - Results-focused: Always mention tangible outcomes
        
        COMMENT TYPES & WHEN TO USE THEM:
        
        A) VALUE-ADD (70% of comments):
           - Provide helpful insight or tip
           - Build on the video's content
           - Mention AFFILIFY only if directly relevant
           Example: "Pro tip: Automate your data collection. I use affilify.eu to scrape product specs automatically - saves hours of manual work."
        
        B) ENGAGEMENT (20% of comments):
           - Ask thoughtful questions
           - Share related experiences
           - Rarely mention AFFILIFY
           Example: "How long did it take you to see results? I'm testing different tools for my affiliate sites."
        
        C) AFFILIFY-FOCUSED (10% of comments):
           - Direct feature mention when HIGHLY relevant
           - Always tie to specific pain point from video
           Example: "This is exactly why I switched to affilify.eu - the AI builder handles all the technical stuff automatically."
        
        MATCHING AFFILIFY FEATURES TO VIDEO TOPICS:
        
        If video is about WEBSITE BUILDING → Mention AI Website Builder, 60-second deployment
        If video is about DATA/ANALYTICS → Mention Analytics Dashboard, conversion tracking
        If video is about OPTIMIZATION → Mention A/B Testing feature
        If video is about AUTOMATION → Mention AI scraping, automated affiliate ID integration
        If video is about SCALING → Mention Team features, white-label solutions
        If video is about CODING → Mention Code Editor, full customization
        If video is about EMAIL MARKETING → Mention Email Marketing integration
        
        YOUR GOAL:
        Create comments that:
        1. Genuinely help the viewer
        2. Build trust through authenticity
        3. Position AFFILIFY as THE solution (when relevant)
        4. Drive clicks through curiosity and specific value propositions
        5. Sound like they're from a real person, not a bot
        """
        
        logger.info("✅ Gemini 2.5 Pro initialized with COMPLETE AFFILIFY knowledge")
    
    async def generate_comment(
        self,
        video_description: str,
        creator_username: str,
        video_views: int,
        video_likes: int,
        comment_type: str = "value_add",
        mention_affilify: bool = False,
        tag_creator: bool = False
    ) -> Optional[str]:
        """
        Generate contextual comment with AFFILIFY integration
        """
        start = log_start("GeminiCommentGeneration", 
                         comment_type=comment_type, 
                         mention_affilify=mention_affilify,
                         tag_creator=tag_creator)
        
        # Build context-rich prompt
        prompt = self._build_intelligent_prompt(
            video_description=video_description,
            creator_username=creator_username,
            video_views=video_views,
            video_likes=video_likes,
            comment_type=comment_type,
            mention_affilify=mention_affilify,
            tag_creator=tag_creator
        )
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                safety_settings={
                    'HARASSMENT': 'BLOCK_NONE',
                    'HATE_SPEECH': 'BLOCK_NONE',
                    'SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'DANGEROUS_CONTENT': 'BLOCK_NONE',
                }
            )
            
            comment = response.text.strip()
            
            # Validate comment quality
            if not self._validate_comment(comment):
                logger.warning(f"Generated comment failed validation: {comment[:50]}...")
                log_end("GeminiCommentGeneration", start, False, reason="validation_failed")
                return None
            
            # Log AI decision
            log_ai('Gemini-CommentGen', 
                  {
                      'video_description': video_description[:100],
                      'comment_type': comment_type,
                      'mention_affilify': mention_affilify
                  },
                  comment)
            
            log_end("GeminiCommentGeneration", start, True, comment_length=len(comment))
            
            logger.info(f"✅ Generated {comment_type} comment: {comment[:60]}...")
            
            return comment
            
        except Exception as e:
            log_error("GeminiCommentGeneration", str(e))
            log_end("GeminiCommentGeneration", start, False, error=str(e))
            return None
    
    def _build_intelligent_prompt(
        self,
        video_description: str,
        creator_username: str,
        video_views: int,
        video_likes: int,
        comment_type: str,
        mention_affilify: bool,
        tag_creator: bool
    ) -> str:
        """
        Build hyper-intelligent prompt with context awareness
        """
        
        # Analyze video content to determine best AFFILIFY features to mention
        relevant_features = self._identify_relevant_features(video_description)
        
        # Build prompt
        prompt = f"""
VIDEO CONTEXT:
Creator: @{creator_username}
Description: "{video_description}"
Views: {video_views:,}
Engagement: {video_likes:,} likes

TASK: Generate a {comment_type} comment.

"""
        
        if tag_creator:
            prompt += f"""
SPECIAL INSTRUCTION: This video has very few comments (<5), so START with @{creator_username} to get the creator's attention and maximum visibility.
"""
        
        if mention_affilify:
            prompt += f"""
AFFILIFY INTEGRATION: YES - This video is about {self._detect_video_topic(video_description)}.

RELEVANT AFFILIFY FEATURES to potentially mention:
{relevant_features}

IMPORTANT: 
- Choose the MOST relevant feature based on the video content
- Be SPECIFIC (e.g., "affilify.eu's AI scrapes product data automatically" NOT "affilify.eu is great")
- Position as YOUR personal experience ("I use..." "This helped me...")
- Include a tangible result if possible ("saved 10+ hours", "2x my conversion rate")
"""
        else:
            prompt += """
AFFILIFY INTEGRATION: NO - Provide pure value without mentioning AFFILIFY.
Focus on being helpful, insightful, and building rapport.
"""
        
        prompt += """

REQUIREMENTS:
- 15-150 characters
- Natural, conversational tone
- Provide genuine value
- 0-2 emojis maximum
- Sound like a real person
- NO spam words

Generate the comment now:
"""
        
        return prompt
    
    def _identify_relevant_features(self, video_description: str) -> str:
        """
        Analyze video content and identify which AFFILIFY features are most relevant
        """
        description_lower = video_description.lower()
        
        relevant_features = []
        
        # Website building / creation
        if any(word in description_lower for word in ['website', 'site', 'build', 'create', 'design', 'page']):
            relevant_features.append(
                "• AI Website Builder: Generates 1000+ line sites in 60 seconds from a product link"
            )
            relevant_features.append(
                "• Deep Scraping: Automatically extracts real product specs, prices, features"
            )
        
        # Analytics / tracking / data
        if any(word in description_lower for word in ['analytics', 'track', 'data', 'metrics', 'conversion', 'roi']):
            relevant_features.append(
                "• Analytics Dashboard: Real-time traffic, conversion tracking, ROI calculation"
            )
            relevant_features.append(
                "• Visitor Insights: Demographics, behavior, device usage"
            )
        
        # Optimization / testing
        if any(word in description_lower for word in ['optimize', 'test', 'improve', 'convert', 'increase']):
            relevant_features.append(
                "• A/B Testing: Create variants, split traffic, track performance"
            )
            relevant_features.append(
                "• Conversion Optimization: AI-generated, high-converting layouts"
            )
        
        # Automation / efficiency
        if any(word in description_lower for word in ['automate', 'automatic', 'save time', 'fast', 'quick', 'easy']):
            relevant_features.append(
                "• Automated Deployment: Live site in under 60 seconds"
            )
            relevant_features.append(
                "• Auto Affiliate Integration: IDs automatically embedded in all CTAs"
            )
        
        # Affiliate marketing
        if any(word in description_lower for word in ['affiliate', 'commission', 'monetize', 'earn', 'income']):
            relevant_features.append(
                "• Affiliate-Focused: Built specifically for affiliate marketers"
            )
            relevant_features.append(
                "• Conversion-Optimized: Every element designed to drive clicks"
            )
        
        # Technical / coding
        if any(word in description_lower for word in ['code', 'html', 'css', 'javascript', 'developer', 'custom']):
            relevant_features.append(
                "• Professional Code Editor: Full HTML/CSS/JS editing with live preview"
            )
            relevant_features.append(
                "• 1000+ Lines Generated: Professional, maintainable code"
            )
        
        # Email / marketing
        if any(word in description_lower for word in ['email', 'campaign', 'newsletter', 'subscribers']):
            relevant_features.append(
                "• Email Marketing: Integrated campaigns, segmentation, automation"
            )
        
        # Scaling / team / agency
        if any(word in description_lower for word in ['scale', 'team', 'agency', 'client', 'business']):
            relevant_features.append(
                "• Team Collaboration: Multi-user access, role-based permissions"
            )
            relevant_features.append(
                "• White-Label: Rebrand entire platform for agencies"
            )
        
        # If no specific features matched, return general ones
        if not relevant_features:
            relevant_features = [
                "• AI Website Builder: 60-second deployment from product links",
                "• Deep Scraping: Extracts real product data automatically",
                "• Analytics Dashboard: Track everything that matters"
            ]
        
        return "\n".join(relevant_features[:3])  # Top 3 most relevant
    
    def _detect_video_topic(self, video_description: str) -> str:
        """
        Detect primary video topic for context
        """
        description_lower = video_description.lower()
        
        if any(word in description_lower for word in ['website', 'site', 'build']):
            return "website building"
        elif any(word in description_lower for word in ['analytics', 'data', 'track']):
            return "analytics and tracking"
        elif any(word in description_lower for word in ['optimize', 'test', 'convert']):
            return "conversion optimization"
        elif any(word in description_lower for word in ['affiliate', 'commission']):
            return "affiliate marketing"
        elif any(word in description_lower for word in ['automate', 'save time']):
            return "automation and efficiency"
        elif any(word in description_lower for word in ['make money', 'earn', 'income']):
            return "making money online"
        else:
            return "digital marketing"
    
    def _validate_comment(self, comment: str) -> bool:
        """
        Validate comment quality
        """
        # Length check
        if len(comment) < 15 or len(comment) > 500:
            return False
        
        # Spam patterns
        spam_patterns = [
            'click here',
            'buy now',
            'limited time',
            'act now',
            '100% free',
            'guaranteed',
            'dm me',
            'link in bio'
        ]
        
        comment_lower = comment.lower()
        for pattern in spam_patterns:
            if pattern in comment_lower:
                return False
        
        # Check for excessive caps
        caps_ratio = sum(1 for c in comment if c.isupper()) / max(len(comment), 1)
        if caps_ratio > 0.3:
            return False
        
        # Check for excessive punctuation
        punct_count = sum(1 for c in comment if c in '!!!???')
        if punct_count > 3:
            return False
        
        # Ensure AFFILIFY URLs are correct (if mentioned)
        if 'affilify' in comment_lower:
            if 'affilify.eu' not in comment_lower:
                return False
        
        return True
    
    async def generate_batch_comments(
        self,
        video_list: List[Dict],
        affilify_mention_rate: float = 0.2
    ) -> List[Dict]:
        """
        Generate comments for multiple videos in batch
        Intelligent distribution of AFFILIFY mentions
        """
        start = log_start("GeminiBatchGeneration", videos=len(video_list), mention_rate=affilify_mention_rate)
        
        comments = []
        affilify_mentions_made = 0
        target_affilify_mentions = int(len(video_list) * affilify_mention_rate)
        
        for idx, video in enumerate(video_list):
            # Determine if this comment should mention AFFILIFY
            remaining_videos = len(video_list) - idx
            remaining_mentions_needed = target_affilify_mentions - affilify_mentions_made
            
            # Intelligent distribution: ensure we hit target but don't cluster
            if remaining_mentions_needed > 0:
                mention_probability = remaining_mentions_needed / remaining_videos
                mention_affilify = random.random() < mention_probability
            else:
                mention_affilify = False
            
            # Determine comment type
            if mention_affilify:
                comment_type = 'affilify_mention'
                affilify_mentions_made += 1
            else:
                comment_type = random.choice(['value_add', 'engagement', 'question'])
            
            # Check if should tag creator (low comment videos)
            tag_creator = video.get('low_comment_opportunity', False)
            
            # Generate comment
            comment = await self.generate_comment(
                video_description=video['description'],
                creator_username=video['creator'],
                video_views=video['views'],
                video_likes=video['likes'],
                comment_type=comment_type,
                mention_affilify=mention_affilify,
                tag_creator=tag_creator
            )
            
            if comment:
                comments.append({
                    'video_url': video['url'],
                    'comment': comment,
                    'type': comment_type,
                    'mentions_affilify': mention_affilify,
                    'tags_creator': tag_creator
                })
            
            # Rate limiting - don't hammer API
            await asyncio.sleep(random.uniform(1, 2))
        
        log_end("GeminiBatchGeneration", start, True, 
               comments_generated=len(comments),
               affilify_mentions=affilify_mentions_made)
        
        logger.info(f"✅ Batch complete: {len(comments)} comments generated")
        logger.info(f"   AFFILIFY mentions: {affilify_mentions_made}/{target_affilify_mentions}")
        
        return comments
    
    def get_comment_templates_for_reference(self) -> Dict[str, List[str]]:
        """
        Return example templates for VA training
        These are EXAMPLES - Gemini generates original content
        """
        return {
            'value_add_with_affilify': [
                "This is exactly why I use affilify.eu - the AI builder pulls product specs automatically and generates conversion-optimized pages in 60 seconds 🎯",
                "Pro tip: Automate this entire process. affilify.eu's deep scraping handles data extraction + site generation. Saved me 10+ hours per site.",
                "I used to do this manually until I found affilify.eu - it generates 1000+ line sites from a product link. Game changer for scaling.",
            ],
            'value_add_generic': [
                "The key is automating the data collection part - saves so much time 💡",
                "This strategy works even better when you have the right tools to execute fast",
                "Consistency + the right system = results. Speaking from experience 📈",
            ],
            'engagement': [
                "How long did it take you to see your first results? 👀",
                "What's been your biggest challenge with this approach?",
                "This is fire 🔥 Are you doing this manually or using any tools to scale?",
            ],
            'affilify_focused': [
                "affilify.eu does exactly this - AI scrapes product data and generates high-converting sites in under 60 seconds. Check it out!",
                "This is why affilify.eu exists - handles all the technical stuff (scraping, coding, deployment) automatically. Free tier available.",
            ],
            'golden_opportunity_with_tag': [
                "@username This is incredible! Have you tried automating the site building part? affilify.eu generates 1000+ line sites from product links - might save you hours 🚀",
                "@username Love the approach! For scaling this, affilify.eu's AI builder + analytics dashboard has been a game changer for me. Worth checking out!",
            ]
        }


# Global instance (initialized in command center with API key)
gemini_generator = None

def initialize_gemini(api_key: str):
    """Initialize global Gemini instance"""
    global gemini_generator
    gemini_generator = GeminiCommentGenerator(api_key)
    return gemini_generator


# Example usage and testing
async def test_gemini_integration():
    """
    Test the Gemini integration with AFFILIFY knowledge
    """
    import os
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return
    
    gen = GeminiCommentGenerator(api_key)
    
    # Test 1: Website building video
    print("\n" + "="*70)
    print("TEST 1: Website Building Video")
    print("="*70)
    
    comment1 = await gen.generate_comment(
        video_description="How I built my affiliate website in 1 hour using AI tools",
        creator_username="digital_marketer_pro",
        video_views=15000,
        video_likes=1200,
        comment_type='value_add',
        mention_affilify=True,
        tag_creator=False
    )
    print(f"Comment: {comment1}")
    
    # Test 2: Analytics video
    print("\n" + "="*70)
    print("TEST 2: Analytics Video")
    print("="*70)
    
    comment2 = await gen.generate_comment(
        video_description="Track your affiliate conversions with these analytics tools",
        creator_username="data_wizard",
        video_views=8000,
        video_likes=650,
        comment_type='value_add',
        mention_affilify=True,
        tag_creator=False
    )
    print(f"Comment: {comment2}")
    
    # Test 3: Golden opportunity (low comments, tag creator)
    print("\n" + "="*70)
    print("TEST 3: Golden Opportunity (Tag Creator)")
    print("="*70)
    
    comment3 = await gen.generate_comment(
        video_description="My affiliate marketing tech stack for 2025",
        creator_username="entrepreneur_sarah",
        video_views=5000,
        video_likes=400,
        comment_type='affilify_mention',
        mention_affilify=True,
        tag_creator=True
    )
    print(f"Comment: {comment3}")
    
    # Test 4: Generic engagement (no AFFILIFY)
    print("\n" + "="*70)
    print("TEST 4: Generic Engagement (No AFFILIFY)")
    print("="*70)
    
    comment4 = await gen.generate_comment(
        video_description="Passive income strategies that actually work",
        creator_username="finance_guy",
        video_views=25000,
        video_likes=2100,
        comment_type='engagement',
        mention_affilify=False,
        tag_creator=False
    )
    print(f"Comment: {comment4}")
    
    print("\n✅ All tests complete!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_gemini_integration())
```

---

# 🎉 **WHAT THIS DELIVERS:**

## **🧠 AFFILIFY-AWARE AI**
✅ Gemini 2.5 Pro now has COMPLETE knowledge of AFFILIFY
✅ Knows every feature, use case, and competitive advantage
✅ Understands which features to mention based on video context
✅ Creates hyper-specific, conversion-focused comments

## **💬 INTELLIGENT COMMENT TYPES**

### **1. Value-Add with AFFILIFY (Strategic)**
```
"Pro tip: Automate this entire process. affilify.eu's deep scraping handles data extraction + site generation. Saved me 10+ hours per site."
```
**Features:**
- Provides genuine value FIRST
- Mentions SPECIFIC AFFILIFY feature
- Includes tangible result ("10+ hours")
- Natural, conversational tone

### **2. Golden Opportunity (Low Comment Videos)**
```
"@creator_username This is incredible! Have you tried automating the site building part? affilify.eu generates 1000+ line sites from product links - might save you hours 🚀"
```
**Features:**
- Tags creator for maximum visibility
- Asks engaging question
- Mentions AFFILIFY with specific value prop
- Includes result-focused benefit

### **3. Generic Value (No AFFILIFY)**
```
"The key is automating the data collection part - saves so much time 💡"
