"""
Sector Chart Service - Generates matplotlib sector performance charts.

Single responsibility: Create sector performance visualizations for Discord embeds.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Dict, Tuple
import io
from utils.logger import get_logger


class SectorChartService:
    """Service for generating sector performance charts."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def generate_sector_performance_chart(self, sectors_data: List[Dict]) -> bytes:
        """
        Generate a sector performance chart from sector data.

        Args:
            sectors_data: List of sector dictionaries with:
                - plateName: sector name
                - changeRatio: percentage change
                - stockName: leading stock
                - priceRiseCount: number of rising stocks
                - priceFallCount: number of falling stocks

        Returns:
            PNG image as bytes
        """
        if not sectors_data:
            self.logger.warning("No sector data provided for chart generation")
            return self._generate_empty_chart()

        # Prepare data
        sectors = sectors_data[:10]  # Top 10 sectors

        # Create figure - simple, clean layout
        fig, ax = plt.subplots(figsize=(18, 12))
        fig.patch.set_facecolor('#2C2F33')
        ax.set_facecolor('#23272A')

        # Prepare data
        y_pos = range(len(sectors))
        sector_names = [s.get('plateName', 'Unknown')[:25] for s in sectors]
        changes = [float(s.get('changeRatio', '0%').replace('%', '')) for s in sectors]
        leaders = [s.get('stockName', 'N/A')[:20] for s in sectors]
        up_counts = [s.get('priceRiseCount', 0) for s in sectors]
        down_counts = [s.get('priceFallCount', 0) for s in sectors]

        # Create color map
        colors = ['#57F287' if c > 0 else '#ED4245' if c < 0 else '#808080' for c in changes]

        # Plot horizontal bar chart
        bars = ax.barh(y_pos, changes, color=colors, alpha=0.9, edgecolor='#1a1a1a', height=0.8)

        # Customize chart - MUCH larger fonts
        ax.set_yticks(y_pos)
        ax.set_yticklabels(sector_names, color='white', fontsize=22, fontweight='bold')
        ax.invert_yaxis()
        ax.set_xlabel('Performance (%)', color='white', fontsize=24, fontweight='bold')
        ax.set_title('Top 10 Market Sectors Performance', color='white',
                     fontsize=28, fontweight='bold', pad=30)

        # Add grid
        ax.grid(True, alpha=0.3, color='#4f4f4f', linestyle='--', linewidth=1.5)
        ax.set_axisbelow(True)

        # Add labels - MUCH larger fonts
        max_change = max(abs(max(changes)), abs(min(changes)))
        for i, (bar, change, leader, up, down) in enumerate(zip(bars, changes, leaders, up_counts, down_counts)):
            # Up/Down counts (LEFT of bar, between y-axis and bar)
            # Increased padding: moved further right to avoid y-axis label overlap
            x_pos_counts = -0.01  # Was -0.3, now -0.1 (closer to bar, further from y-axis)
            ax.text(x_pos_counts, bar.get_y() + bar.get_height()/2,
                    f'▲{up} / ▼{down}',
                    ha='center', va='center', color='white', fontweight='bold',
                    fontsize=20, bbox=dict(boxstyle='round,pad=0.4', facecolor='#1a1a1a', alpha=0.9))

            # Percentage change (RIGHT of bar)
            x_pos = bar.get_width() if bar.get_width() >= 0 else bar.get_width() - 0.08
            ha = 'left' if bar.get_width() >= 0 else 'right'
            ax.text(x_pos, bar.get_y() + bar.get_height()/2 + 0.2,
                    f'{change:+.2f}%',
                    ha=ha, va='center', color='white', fontweight='bold', fontsize=22)

            # Leader stock (outside bar, same area as percentage)
            ax.text(x_pos, bar.get_y() + bar.get_height()/2 - 0.2,
                    f'{leader}',
                    ha=ha, va='center', color='#99aab5', fontweight='bold', fontsize=18)

        # Style axes
        ax.tick_params(colors='white', labelsize=18)
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_xlim(min(changes) - 0.8, max_change + 2.0)

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#57F287', label='Positive Performance'),
            Patch(facecolor='#ED4245', label='Negative Performance')
        ]
        ax.legend(handles=legend_elements, loc='lower right', facecolor='#2C2F33',
                  edgecolor='white', labelcolor='white', fontsize=18)

        plt.tight_layout()

        # Save to bytes
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='#2C2F33', edgecolor='none')
        buffer.seek(0)

        # Clean up
        plt.close(fig)

        self.logger.info(f"Generated sector performance chart for {len(sectors_data)} sectors")
        return buffer.getvalue()

    def _generate_empty_chart(self) -> bytes:
        """Generate an empty chart when no data is available."""
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#2C2F33')
        ax.set_facecolor('#23272A')

        ax.text(0.5, 0.5, 'No Sector Data Available', ha='center', va='center',
               transform=ax.transAxes, color='white', fontsize=16)

        ax.set_xticks([])
        ax.set_yticks([])

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', facecolor='#2C2F33')
        buffer.seek(0)
        plt.close(fig)

        return buffer.getvalue()
