#!/usr/bin/env python
"""
Test chart generation with improved layout and larger fonts.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.chart_service import ChartService


def test_improved_chart():
    """Test improved chart with better layout and larger fonts."""
    print("=" * 80)
    print("Testing Improved Chart Layout v3")
    print("=" * 80)

    chart_service = ChartService()

    # Test data - user's provided data
    test_sectors = [
        {
            "plateName": "Electric Vehicles",
            "changeRatio": "+2.41%",
            "stockName": "Polestar Automotive",
            "priceRiseCount": 8,
            "priceFallCount": 4
        },
        {
            "plateName": "Solid State Battery",
            "changeRatio": "+1.80%",
            "stockName": "Toyota Motor",
            "priceRiseCount": 3,
            "priceFallCount": 5
        },
        {
            "plateName": "EV Charging",
            "changeRatio": "+1.71%",
            "stockName": "Tesla",
            "priceRiseCount": 1,
            "priceFallCount": 8
        },
        {
            "plateName": "Sports Betting",
            "changeRatio": "+0.98%",
            "stockName": "Penn Entertainment",
            "priceRiseCount": 4,
            "priceFallCount": 3
        },
        {
            "plateName": "Weight Loss Drugs",
            "changeRatio": "+0.94%",
            "stockName": "Eli Lilly and Co",
            "priceRiseCount": 4,
            "priceFallCount": 4
        },
        {
            "plateName": "Hydrogen Energy",
            "changeRatio": "+0.90%",
            "stockName": "Linde",
            "priceRiseCount": 2,
            "priceFallCount": 5
        },
        {
            "plateName": "Defense",
            "changeRatio": "+0.65%",
            "stockName": "Boeing",
            "priceRiseCount": 6,
            "priceFallCount": 3
        },
        {
            "plateName": "Renewable Energy",
            "changeRatio": "+0.60%",
            "stockName": "VESTAS WIND SYSTEMS",
            "priceRiseCount": 4,
            "priceFallCount": 2
        },
        {
            "plateName": "Digital Payment",
            "changeRatio": "+0.59%",
            "stockName": "The Western Union",
            "priceRiseCount": 10,
            "priceFallCount": 11
        },
        {
            "plateName": "Credit Card Payment",
            "changeRatio": "+0.48%",
            "stockName": "MasterCard",
            "priceRiseCount": 3,
            "priceFallCount": 6
        }
    ]

    print(f"Generating chart for {len(test_sectors)} sectors...")
    print("\nKey improvements in v3:")
    print("  • Much larger fonts (16-24px)")
    print("  • Leader stock OUTSIDE the bar (no overlap)")
    print("  • Clear spacing between elements")
    print("  • Better layout with more space")
    print("  • Professional formatting")

    try:
        chart_bytes = chart_service.generate_sector_performance_chart(test_sectors)
        print(f"\n✓ Chart generated successfully!")
        print(f"  Size: {len(chart_bytes):,} bytes")

        # Save to file
        output_path = "test_chart_v3.png"
        with open(output_path, 'wb') as f:
            f.write(chart_bytes)
        print(f"  Saved to: {output_path}")

        print("\n" + "=" * 80)
        print("Chart Layout:")
        print("=" * 80)
        print("Left: Sector name + Leader (20 chars max)")
        print("Middle: Bar chart with % change")
        print("Right: ▲X ▼Y counts")
        print("Bottom: Overall statistics")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_improved_chart()
    sys.exit(0 if success else 1)
