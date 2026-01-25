import asyncio
from video_scraper import VideoScraper

async def main():
    print("🚀 STARTING ROLEX DISCOVERY VERIFICATION...")
    scraper = VideoScraper()
    videos = await scraper.discover_targets_comprehensive(max_videos=10)
    
    print(f"\n✅ DISCOVERY COMPLETE: FOUND {len(videos)} VIDEOS")
    for i, v in enumerate(videos, 1):
        print(f"{i}. {v['video_url']} (Niche: {v['niche']})")
    
    if not videos:
        print("❌ No videos found. Check logs for blocks.")

if __name__ == "__main__":
    asyncio.run(main())
