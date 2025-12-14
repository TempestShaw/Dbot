#!/usr/bin/env python
"""Test script to verify Polymarket earnings integration."""

import asyncio
import json
from config import load_config
from services.web_crawler_service import WebCrawlerService


async def test_polymarket_scraper():
    """Test the Polymarket earnings scraper."""
    print("=" * 60)
    print("Testing Polymarket Earnings Scraper")
    print("=" * 60)

    config = load_config()
    web_crawler = WebCrawlerService(config)

    print("\n1. Testing get_polymarket_earnings_async()...")
    try:
        earnings = await web_crawler.get_polymarket_earnings_async()
        print(f"   ✓ Successfully scraped {len(earnings)} earnings records")

        if earnings:
            print("\n2. Sample data:")
            for i, item in enumerate(earnings[:3], 1):
                print(f"   {i}. {item}")

        print("\n3. Full JSON output:")
        print(json.dumps(earnings, indent=2, ensure_ascii=False))

        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_daily_summary_with_polymarket():
    """Test the complete daily summary including Polymarket data."""
    print("\n" + "=" * 60)
    print("Testing Daily Summary with Polymarket Data")
    print("=" * 60)

    from services.message_service import MessageService

    config = load_config()
    message_service = MessageService(config)

    print("\n1. Generating daily summary with Polymarket earnings...")
    try:
        summary = await message_service.generate_daily_summary_json_async()
        print(f"   ✓ Successfully generated summary")
        print(f"   - Top sectors: {len(summary.get('top_sectors_details', []))}")
        print(f"   - Earnings: {len(summary.get('earnings', []))}")
        print(f"   - Polymarket earnings: {len(summary.get('polymarket_earnings', []))}")
        print(f"   - IPOs: {len(summary.get('ipos', []))}")

        print("\n2. Polymarket earnings in summary:")
        poly_earnings = summary.get('polymarket_earnings', [])
        if poly_earnings:
            for item in poly_earnings[:3]:
                print(f"   - {item}")

        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n🚀 Polymarket Integration Test Suite\n")

    test1 = await test_polymarket_scraper()
    test2 = await test_daily_summary_with_polymarket()

    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    print(f"Polymarket Scraper: {'✓ PASS' if test1 else '✗ FAIL'}")
    print(f"Daily Summary:      {'✓ PASS' if test2 else '✗ FAIL'}")
    print("=" * 60)

    if test1 and test2:
        print("\n✅ All tests passed! Polymarket integration is working.\n")
    else:
        print("\n❌ Some tests failed. Check the errors above.\n")


if __name__ == "__main__":
    asyncio.run(main())
