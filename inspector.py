import asyncio
from TikTokApi import TikTokApi

async def main():
    async with TikTokApi() as api:
        await api.create_sessions(num_sessions=1, headless=True, sleep_after=3)
        print(dir(api.search))

if __name__ == "__main__":
    asyncio.run(main())
