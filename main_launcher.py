# main_launcher.py - START HERE!

import asyncio
import os
from command_center import AffillifyCommandCenter
from logger_system import affilify_logger

async def main():
    """
    AFFILIFY TIKTOK DOMINATION SYSTEM
    Main entry point
    """
    
    # ASCII Art Banner
    banner = """
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║     █████╗ ███████╗███████╗██╗██╗     ██╗███████╗██╗   ██╗          ║
    ║    ██╔══██╗██╔════╝██╔════╝██║██║     ██║██╔════╝╚██╗ ██╔╝          ║
    ║    ███████║█████╗  █████╗  ██║██║     ██║█████╗   ╚████╔╝           ║
    ║    ██╔══██║██╔══╝  ██╔══╝  ██║██║     ██║██╔══╝    ╚██╔╝            ║
    ║    ██║  ██║██║     ██║     ██║███████╗██║██║        ██║             ║
    ║    ╚═╝  ╚═╝╚═╝     ╚═╝     ╚═╝╚══════╝╚═╝╚═╝        ╚═╝             ║
    ║                                                                       ║
    ║              TIKTOK DOMINATION SYSTEM v2.0                            ║
    ║                  Powered by JARVIS AI                                 ║
    ║                                                                       ║
    ║              "Building Your $150K MRR Empire"                         ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """
    
    print(banner)
    print("\n🚀 Starting AFFILIFY Command Center...\n")
    
    # Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    if not GEMINI_API_KEY:
        print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
        print("   Please set: export GEMINI_API_KEY='your-api-key'")
        return
    
    # Initialize Command Center
    hq = AffillifyCommandCenter()
    
    try:
        # Startup sequence
        jarvis_task, dashboard_task = await hq.startup_sequence(GEMINI_API_KEY)
        
        # Interactive menu
        while True:
            print("\n" + "="*70)
            print("🎯 AFFILIFY COMMAND CENTER - MAIN MENU")
            print("="*70)
            print("\n1. 🚀 Start Automated Campaign (300 comments)")
            print("2. 🎯 Custom Campaign (specify target)")
            print("3. 📊 View System Status")
            print("4. 🔍 Discover New Targets")
            print("5. 🧠 JARVIS Report")
            print("6. 📈 Generate Report")
            print("7. ⏸️  Pause Operations")
            print("8. ▶️  Resume Operations")
            print("9. 🛑 Shutdown System")
            print("\n" + "="*70)
            
            choice = input("\n👉 Select option (1-9): ").strip()
            
            if choice == '1':
                print("\n🚀 Starting automated campaign (300 comments)...")
                await hq.run_operation(mode='auto', target_comments=300)
            
            elif choice == '2':
                target = input("Enter target comment count: ").strip()
                if target.isdigit():
                    print(f"\n🚀 Starting custom campaign ({target} comments)...")
                    await hq.run_operation(mode='auto', target_comments=int(target))
                else:
                    print("❌ Invalid number")
            
            elif choice == '3':
                print("\n📊 SYSTEM STATUS:")
                stats = hq.system.get_dashboard_stats()
                print(f"   Active Accounts: {stats['total_accounts']}")
                print(f"   Comments Today: {stats['comments_today']}")
                print(f"   Total Comments: {stats['total_comments']}")
                print(f"   Avg Health: {stats['avg_health_score']}/100")
                input("\nPress ENTER to continue...")
            
            elif choice == '4':
                print("\n🔍 Discovering new targets...")
                await hq._refresh_targets()
                input("\nPress ENTER to continue...")
            
            elif choice == '5':
                print("\n🧠 JARVIS STATUS:")
                status = jarvis.get_current_status()
                print(f"   Monitoring: {'ACTIVE' if status['monitoring_active'] else 'INACTIVE'}")
                print(f"   Optimization: {'ACTIVE' if status['optimization_active'] else 'INACTIVE'}")
                print(f"   AI Fixes Deployed: {status['metrics']['code_fixes_deployed']}")
                print(f"   Optimizations Made: {status['metrics']['ai_optimizations_made']}")
                input("\nPress ENTER to continue...")
            
            elif choice == '6':
                print("\n📈 Generating report...")
                await hq._generate_interim_report()
                input("\nPress ENTER to continue...")
            
            elif choice == '7':
                hq.pause_requested = True
                print("\n⏸️  Operations paused")
                input("\nPress ENTER to continue...")
            
            elif choice == '8':
                hq.pause_requested = False
                print("\n▶️  Operations resumed")
                input("\nPress ENTER to continue...")
            
            elif choice == '9':
                confirm = input("\n⚠️  Are you sure you want to shutdown? (yes/no): ")
                if confirm.lower() == 'yes':
                    await hq.shutdown()
                    break
            
            else:
                print("❌ Invalid option")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Keyboard interrupt detected")
        await hq.shutdown()
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        await hq.shutdown()
        raise
    
    finally:
        print("\n👋 Thank you for using AFFILIFY Command Center")
        print("   Go build that $150K MRR empire! 🚀\n")


if __name__ == "__main__":
    asyncio.run(main())
