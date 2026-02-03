#!/usr/bin/env python3.11
"""
Test Gemini Comment Generation with AFFILIFY Integration
"""

import asyncio
import os
from gemini_integration import GeminiCommentGenerator
from comment_strategy import CommentStrategySelector

async def test_comment_generation():
    print("=" * 80)
    print("🧠 TESTING GEMINI COMMENT GENERATION WITH AFFILIFY")
    print("=" * 80)
    
    # Initialize
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment!")
        return
    
    print(f"\n✅ API Key found: {api_key[:20]}...")
    
    generator = GeminiCommentGenerator(api_key)
    strategy_selector = CommentStrategySelector()
    
    # Test scenarios
    test_videos = [
        {
            'name': 'GOLDEN OPPORTUNITY (Low Comments)',
            'video_id': '7594419148805934367',
            'creator_username': 'rakos.media',
            'description': 'How to make $10K/month with affiliate marketing 💰',
            'views': 143241,
            'comments': 3,  # <5 comments!
            'low_comment_opportunity': True,
            'creator_verified': True,
            'hours_old': 2.5
        },
        {
            'name': 'VIRAL VIDEO (High Views)',
            'video_id': '7487858254840597790',
            'creator_username': 'passiveincome_pro',
            'description': 'My passive income strategy that actually works 🚀',
            'views': 450000,  # Viral!
            'comments': 1234,
            'low_comment_opportunity': False,
            'creator_verified': False,
            'hours_old': 18
        },
        {
            'name': 'FRESH CONTENT (New Video)',
            'video_id': '7600011639911435551',
            'creator_username': 'entrepreneur_tips',
            'description': 'Side hustle ideas for 2026',
            'views': 5432,
            'comments': 45,
            'low_comment_opportunity': False,
            'creator_verified': False,
            'hours_old': 3.2  # Very fresh!
        },
        {
            'name': 'VERIFIED CREATOR',
            'video_id': '7601749983737515277',
            'creator_username': 'business_guru',
            'description': 'How I built a 7-figure online business',
            'views': 89000,
            'comments': 567,
            'low_comment_opportunity': False,
            'creator_verified': True,  # Verified!
            'hours_old': 12
        }
    ]
    
    print(f"\n📊 Testing {len(test_videos)} scenarios...\n")
    
    results = []
    
    for i, video in enumerate(test_videos, 1):
        print(f"{'='*80}")
        print(f"TEST {i}/{len(test_videos)}: {video['name']}")
        print(f"{'='*80}")
        print(f"   Video ID: {video['video_id']}")
        print(f"   Creator: @{video['creator_username']}")
        print(f"   Description: {video['description']}")
        print(f"   Views: {video['views']:,}")
        print(f"   Comments: {video['comments']}")
        print(f"   Hours old: {video['hours_old']}")
        print(f"   Verified: {'✅' if video.get('creator_verified') else '❌'}")
        
        # Select strategy
        strategy_name, strategy_config = strategy_selector.select_strategy(video)
        
        print(f"\n🎯 STRATEGY SELECTED: {strategy_name}")
        print(f"   Priority Score: {strategy_config['priority_score']}")
        print(f"   Urgency: {strategy_config['urgency']}")
        print(f"   Tag Creator: {'✅' if strategy_config['tag_creator'] else '❌'}")
        print(f"   Mention AFFILIFY: {'✅' if strategy_config['mention_affilify'] else '❌'}")
        print(f"   Tone: {strategy_config['instructions']['tone']}")
        print(f"   Length: {strategy_config['instructions']['length']}")
        
        # Generate comment
        print(f"\n💬 GENERATING COMMENT...")
        
        try:
            comment = await generator.generate_comment(video, strategy_name)
            
            print(f"\n✅ COMMENT GENERATED:")
            print(f"   Length: {len(comment)} chars")
            print(f"   Preview: \"{comment}\"")
            
            # Check if AFFILIFY is mentioned
            has_affilify = 'affilify' in comment.lower()
            has_tag = f"@{video['creator_username']}" in comment
            
            print(f"\n📋 ANALYSIS:")
            print(f"   Contains AFFILIFY: {'✅' if has_affilify else '❌'}")
            print(f"   Tags Creator: {'✅' if has_tag else '❌'}")
            print(f"   Within 150 chars: {'✅' if len(comment) <= 150 else '❌'}")
            
            results.append({
                'scenario': video['name'],
                'strategy': strategy_name,
                'comment': comment,
                'length': len(comment),
                'has_affilify': has_affilify,
                'has_tag': has_tag,
                'success': True
            })
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results.append({
                'scenario': video['name'],
                'strategy': strategy_name,
                'error': str(e),
                'success': False
            })
        
        print()
    
    # Final summary
    print(f"{'='*80}")
    print("📊 FINAL SUMMARY")
    print(f"{'='*80}")
    
    successful = sum(1 for r in results if r['success'])
    print(f"\n✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {len(results) - successful}/{len(results)}")
    
    if successful > 0:
        print(f"\n💬 ALL GENERATED COMMENTS:")
        for i, result in enumerate(results, 1):
            if result['success']:
                print(f"\n{i}. {result['scenario']} ({result['strategy']})")
                print(f"   \"{result['comment']}\"")
                print(f"   Length: {result['length']} | AFFILIFY: {'✅' if result['has_affilify'] else '❌'} | Tag: {'✅' if result['has_tag'] else '❌'}")
    
    print(f"\n{'='*80}")
    print("🎉 GEMINI COMMENT GENERATION TEST COMPLETE!")
    print(f"{'='*80}")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_comment_generation())
