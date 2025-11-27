"""
Data export and visualization services.
"""
import os
import json
import time
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import matplotlib.style as mplstyle
import seaborn as sns
from typing import Optional, List, Tuple
from config.settings import config

# Set professional plotting style
plt.style.use('default')
sns.set_palette("husl")

def apply_professional_style():
    """Apply professional styling to matplotlib plots."""
    plt.rcParams.update({
        # Figure and DPI
        'figure.figsize': (12, 7),
        'figure.dpi': 100,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.facecolor': 'white',
        
        # Font settings
        'font.family': ['DejaVu Sans', 'Arial', 'sans-serif'],
        'font.size': 11,
        'axes.titlesize': 16,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        
        # Colors and style
        'axes.facecolor': '#f8f9fa',
        'figure.facecolor': 'white',
        'axes.edgecolor': '#dee2e6',
        'axes.linewidth': 0.8,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.spines.left': True,
        'axes.spines.bottom': True,
        
        # Grid
        'axes.grid': True,
        'grid.color': '#e9ecef',
        'grid.linestyle': '-',
        'grid.linewidth': 0.5,
        'axes.axisbelow': True,
        
        # Ticks
        'xtick.color': '#6c757d',
        'ytick.color': '#6c757d',
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        
        # Legend
        'legend.frameon': True,
        'legend.fancybox': True,
        'legend.shadow': True,
        'legend.framealpha': 0.9,
        'legend.facecolor': 'white',
        'legend.edgecolor': '#dee2e6',
    })


class DataExportService:
    """Handles CSV generation and chart creation."""
    
    @staticmethod
    def generate_csv_from_data(data: List[dict]) -> str:
        """
        Generate CSV content from query results.
        
        Args:
            data: List of dictionaries representing query results
            
        Returns:
            CSV content as string
        """
        if not data:
            return ""
            
        try:
            df = pd.DataFrame(data)
            return df.to_csv(index=False)
        except Exception as e:
            print(f"Error generating CSV: {e}")
            return ""
    
    @staticmethod
    def save_csv_to_storage(csv_content: str, query_identifier: str) -> str:
        """
        Save CSV content to storage and return file path.
        
        Args:
            csv_content: CSV content as string
            query_identifier: Identifier for the query (used in filename)
            
        Returns:
            Path to saved CSV file
        """
        filename_hash = hashlib.md5(query_identifier.encode()).hexdigest()
        filename = f"{filename_hash}.csv"
        filepath = os.path.join(config.EXPORTS_DIR, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(csv_content)
            return filepath
        except Exception as e:
            print(f"Error saving CSV: {e}")
            raise
    
    @staticmethod
    def get_csv_columns(csv_filepath: str) -> List[str]:
        """
        Extract column names from a CSV file.
        
        Args:
            csv_filepath: Path to CSV file
            
        Returns:
            List of column names
        """
        try:
            df = pd.read_csv(csv_filepath)
            return list(df.columns)
        except Exception as e:
            print(f"Error reading CSV columns from {csv_filepath}: {e}")
            return []
    
    @staticmethod
    def create_bar_plot(csv_filepath: str, x_column: str, y_column: str, 
                       user_id: str) -> Optional[str]:
        """
        Create a bar plot from CSV data and save to file.
        
        Args:
            csv_filepath: Path to CSV file
            x_column: Column name for X-axis
            y_column: Column name for Y-axis
            user_id: User ID for unique filename
            
        Returns:
            Path to saved plot image or None if failed
        """
        try:
            df = pd.read_csv(csv_filepath)
            
            if df.empty or x_column not in df.columns or y_column not in df.columns:
                print(f"Invalid columns or empty data: {x_column}, {y_column}")
                return None
            
            # Aggregate duplicate X values by summing Y values
            if df.duplicated(subset=[x_column]).any():
                df = df.groupby(x_column, dropna=False)[y_column].sum().reset_index()
            
            # Apply professional styling
            apply_professional_style()
            
            # Create plot with enhanced styling
            fig, ax = plt.subplots(figsize=(12, 7))
            
            # Convert data
            x_data = df[x_column].astype(str)
            y_data = pd.to_numeric(df[y_column], errors='coerce')
            
            # Create bars with gradient colors
            colors = sns.color_palette("viridis", len(x_data))
            bars = ax.bar(x_data, y_data, color=colors, alpha=0.8, edgecolor='white', linewidth=0.7)
            
            # Add value labels on top of bars
            for i, (bar, value) in enumerate(zip(bars, y_data)):
                if not pd.isna(value):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{value:,.0f}' if abs(value) >= 1 else f'{value:.2f}',
                           ha='center', va='bottom', fontweight='bold', fontsize=9)
            
            # Styling
            ax.set_xlabel(x_column.replace('_', ' ').title(), fontweight='bold')
            ax.set_ylabel(y_column.replace('_', ' ').title(), fontweight='bold')
            ax.set_title(f"{y_column.replace('_', ' ').title()} by {x_column.replace('_', ' ').title()}", 
                        fontweight='bold', pad=20)
            
            # Format x-axis
            plt.xticks(rotation=45, ha='right')
            
            # Add subtle styling touches
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}' if abs(x) >= 1 else f'{x:.2f}'))
            
            plt.tight_layout()
            
            # Save plot
            plot_filename = f"bar_plot_{user_id}_{int(time.time())}.png"
            plot_filepath = os.path.join(config.EXPORTS_DIR, plot_filename)
            plt.savefig(plot_filepath)
            plt.close()
            
            return plot_filepath
            
        except Exception as e:
            print(f"Error creating bar plot: {e}")
            plt.close()  # Ensure plot is closed even on error
            return None
    
    @staticmethod
    def create_line_plot(csv_filepath: str, x_column: str, y_column: str, 
                        user_id: str) -> Optional[str]:
        """
        Create a line plot from CSV data and save to file.
        
        Args:
            csv_filepath: Path to CSV file
            x_column: Column name for X-axis
            y_column: Column name for Y-axis
            user_id: User ID for unique filename
            
        Returns:
            Path to saved plot image or None if failed
        """
        try:
            df = pd.read_csv(csv_filepath)
            
            if df.empty or x_column not in df.columns or y_column not in df.columns:
                print(f"Invalid columns or empty data: {x_column}, {y_column}")
                return None
            
            # Sort by X column for proper line continuity
            df = df.sort_values(by=x_column)
            
            # Aggregate duplicate X values by averaging Y values (more appropriate for line plots)
            if df.duplicated(subset=[x_column]).any():
                df = df.groupby(x_column, dropna=False)[y_column].mean().reset_index()
            
            # Convert X column to appropriate type for plotting
            x_data = df[x_column]
            y_data = pd.to_numeric(df[y_column], errors='coerce')
            
            # Try to parse X as datetime for better time series plots
            is_categorical = False
            try:
                x_data_parsed = pd.to_datetime(x_data, infer_datetime_format=True)
                x_for_plot = x_data_parsed
                x_labels = None  # Use default datetime labels
            except (ValueError, TypeError):
                # If not datetime, try numeric
                try:
                    x_for_plot = pd.to_numeric(x_data, errors='raise')
                    x_labels = None  # Use numeric values as labels
                except (ValueError, TypeError):
                    # Use categorical data - plot with indices but keep original labels
                    x_for_plot = range(len(x_data))
                    x_labels = x_data.astype(str)  # Keep original string labels
                    is_categorical = True
            
            # Apply professional styling
            apply_professional_style()
            
            # Create plot with enhanced styling
            fig, ax = plt.subplots(figsize=(12, 7))
            
            # Enhanced line styling
            line_color = '#2E86AB'  # Professional blue
            marker_color = '#A23B72'  # Complementary accent color
            
            # Plot line with enhanced styling
            ax.plot(x_for_plot, y_data, 
                   color=line_color, 
                   linewidth=3, 
                   marker='o', 
                   markersize=6, 
                   markerfacecolor=marker_color,
                   markeredgecolor='white',
                   markeredgewidth=1,
                   alpha=0.9)
            
            # Add data point labels (for datasets with <= 10 points)
            if len(y_data) <= 10:
                for i, (x_val, y_val) in enumerate(zip(x_for_plot, y_data)):
                    if not pd.isna(y_val):
                        # Use the correct x position for annotation
                        x_pos = x_val if not is_categorical else i
                        ax.annotate(f'{y_val:,.0f}' if abs(y_val) >= 1 else f'{y_val:.2f}',
                                   (x_pos, y_val),
                                   textcoords="offset points",
                                   xytext=(0,10),
                                   ha='center',
                                   fontsize=9,
                                   fontweight='bold',
                                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
            
            # Format X-axis based on data type
            if isinstance(x_for_plot, pd.DatetimeIndex) or hasattr(x_for_plot, 'dt'):
                plt.xticks(rotation=45, ha='right')
                # Better date formatting
                fig.autofmt_xdate()
            elif is_categorical and x_labels is not None:
                # For categorical data, use original labels with proper positioning
                ax.set_xticks(range(len(x_labels)))
                ax.set_xticklabels(x_labels, rotation=45, ha='right')
            else:
                # For numeric data
                plt.xticks(rotation=45, ha='right')
            
            # Enhanced styling
            ax.set_xlabel(x_column.replace('_', ' ').title(), fontweight='bold')
            ax.set_ylabel(y_column.replace('_', ' ').title(), fontweight='bold')
            ax.set_title(f"{y_column.replace('_', ' ').title()} over {x_column.replace('_', ' ').title()}", 
                        fontweight='bold', pad=20)
            
            # Format y-axis with nice numbers
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}' if abs(x) >= 1 else f'{x:.2f}'))
            
            # Add trend line for time series with more than 5 points
            if len(y_data) > 5:
                try:
                    if isinstance(x_for_plot, range):
                        x_numeric = list(x_for_plot)
                    else:
                        x_numeric = pd.to_numeric(pd.Series(x_for_plot), errors='coerce')
                        if x_numeric.isna().any():
                            x_numeric = range(len(x_for_plot))
                    
                    # Calculate trend line
                    z = pd.Series(y_data).dropna()
                    x_clean = x_numeric[:len(z)]
                    if len(z) > 1:
                        coeffs = pd.Series(x_clean).corr(z)
                        if not pd.isna(coeffs):
                            trend_y = z.mean() + (pd.Series(x_clean) - pd.Series(x_clean).mean()) * coeffs * (z.std() / pd.Series(x_clean).std())
                            ax.plot(x_for_plot[:len(trend_y)], trend_y, '--', color='#F18F01', alpha=0.7, linewidth=2, label='Trend')
                            ax.legend(loc='upper left')
                except:
                    pass  # Skip trend line if calculation fails
            
            plt.tight_layout()
            
            # Save plot
            plot_filename = f"line_plot_{user_id}_{int(time.time())}.png"
            plot_filepath = os.path.join(config.EXPORTS_DIR, plot_filename)
            plt.savefig(plot_filepath)
            plt.close()
            
            return plot_filepath
            
        except Exception as e:
            print(f"Error creating line plot: {e}")
            plt.close()  # Ensure plot is closed even on error
            return None
    
    @staticmethod
    def create_pie_chart(csv_filepath: str, category_column: str, value_column: str, 
                        user_id: str) -> Optional[str]:
        """
        Create a pie chart from CSV data and save to file.
        
        Args:
            csv_filepath: Path to CSV file
            category_column: Column name for category labels (pie slices)
            value_column: Column name for values (slice sizes)
            user_id: User ID for unique filename
            
        Returns:
            Path to saved plot image or None if failed
        """
        try:
            df = pd.read_csv(csv_filepath)
            
            if df.empty or category_column not in df.columns or value_column not in df.columns:
                print(f"Invalid columns or empty data: {category_column}, {value_column}")
                return None
            
            # Aggregate duplicate categories by summing values
            if df.duplicated(subset=[category_column]).any():
                df = df.groupby(category_column, dropna=False)[value_column].sum().reset_index()
            
            # Convert data
            categories = df[category_column].astype(str)
            values = pd.to_numeric(df[value_column], errors='coerce')
            
            # Remove any NaN values
            valid_mask = ~(values.isna() | (values == 0))
            categories = categories[valid_mask]
            values = values[valid_mask]
            
            if len(values) == 0:
                print("No valid data for pie chart")
                return None
            
            # Limit to top 10 categories for readability
            if len(values) > 10:
                # Sort by values and take top 10
                combined = list(zip(categories, values))
                combined.sort(key=lambda x: x[1], reverse=True)
                categories, values = zip(*combined[:10])
                categories = list(categories)
                values = list(values)
            
            # Apply professional styling
            apply_professional_style()
            
            # Create figure with proper sizing for pie chart
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create a beautiful color palette
            colors = sns.color_palette("Set3", len(values))
            if len(values) > 10:
                colors = sns.color_palette("tab20", len(values))
            
            # Create pie chart with enhanced styling
            wedges, texts, autotexts = ax.pie(
                values, 
                labels=categories,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                explode=[0.05 if i == 0 else 0 for i in range(len(values))],  # Explode largest slice
                shadow=True,
                textprops={'fontsize': 10, 'fontweight': 'bold'}
            )
            
            # Enhance text styling
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            # Add value labels alongside percentages for clarity
            for i, (category, value) in enumerate(zip(categories, values)):
                angle = (wedges[i].theta2 + wedges[i].theta1) / 2
                x = 1.1 * plt.np.cos(plt.np.radians(angle))
                y = 1.1 * plt.np.sin(plt.np.radians(angle))
                
                # Add value annotation outside the pie
                ax.annotate(
                    f'{value:,.0f}' if abs(value) >= 1 else f'{value:.2f}',
                    xy=(x, y), 
                    xytext=(x*1.2, y*1.2),
                    ha='center', 
                    va='center',
                    fontsize=8,
                    fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='gray'),
                    arrowprops=dict(arrowstyle='->', color='gray', alpha=0.7)
                )
            
            # Set title with enhanced styling
            ax.set_title(
                f"{value_column.replace('_', ' ').title()} by {category_column.replace('_', ' ').title()}", 
                fontweight='bold', 
                fontsize=16,
                pad=30
            )
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            
            # Add a subtle legend if we have many categories
            if len(categories) > 6:
                ax.legend(
                    wedges, 
                    [f"{cat[:20]}..." if len(str(cat)) > 20 else str(cat) for cat in categories],
                    title=category_column.replace('_', ' ').title(),
                    loc="center left",
                    bbox_to_anchor=(1, 0, 0.5, 1),
                    fontsize=9
                )
            
            plt.tight_layout()
            
            # Save plot
            plot_filename = f"pie_chart_{user_id}_{int(time.time())}.png"
            plot_filepath = os.path.join(config.EXPORTS_DIR, plot_filename)
            plt.savefig(plot_filepath, bbox_inches='tight', dpi=300)
            plt.close()
            
            return plot_filepath
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            plt.close()  # Ensure plot is closed even on error
            return None


class SessionManager:
    """Manages user session data for plotting and exports."""
    
    def __init__(self):
        self._sessions = {}
    
    def store_user_selection(self, user_id: str, selection_type: str, value: str):
        """Store a user's selection (X axis, Y axis, or CSV path)."""
        if user_id not in self._sessions:
            self._sessions[user_id] = {}
        self._sessions[user_id][selection_type] = value
    
    def get_user_selections(self, user_id: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Get user's X axis, Y axis, and CSV path selections."""
        user_data = self._sessions.get(user_id, {})
        return (
            user_data.get("X"),
            user_data.get("Y"),
            user_data.get("CSV")
        )
    
    def get_user_selection(self, user_id: str, selection_type: str) -> Optional[str]:
        """Get a specific user selection."""
        user_data = self._sessions.get(user_id, {})
        return user_data.get(selection_type)
    
    def clear_user_session(self, user_id: str):
        """Clear all session data for a user."""
        self._sessions.pop(user_id, None)


# Global session manager instance
session_manager = SessionManager()