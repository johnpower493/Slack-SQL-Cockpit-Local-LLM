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
from typing import Optional, List, Tuple
from config.settings import config


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
            
            # Create plot
            plt.figure(figsize=(10, 6))
            plt.bar(df[x_column].astype(str), pd.to_numeric(df[y_column], errors='coerce'))
            plt.xticks(rotation=45, ha='right')
            plt.xlabel(x_column)
            plt.ylabel(y_column)
            plt.title(f"{y_column} by {x_column}")
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
            try:
                x_data_parsed = pd.to_datetime(x_data, infer_datetime_format=True)
                x_for_plot = x_data_parsed
            except (ValueError, TypeError):
                # If not datetime, try numeric
                try:
                    x_for_plot = pd.to_numeric(x_data, errors='raise')
                except (ValueError, TypeError):
                    # Use as string with numeric indices
                    x_for_plot = range(len(x_data))
            
            # Create plot
            plt.figure(figsize=(10, 6))
            plt.plot(x_for_plot, y_data, marker='o', linewidth=2, markersize=4)
            
            # Format X-axis based on data type
            if isinstance(x_for_plot, pd.DatetimeIndex) or hasattr(x_for_plot, 'dt'):
                plt.xticks(rotation=45, ha='right')
            elif x_for_plot is not range(len(x_data)):
                plt.xticks(rotation=45, ha='right')
            else:
                # For categorical data, use original labels
                plt.xticks(range(len(x_data)), x_data.astype(str), rotation=45, ha='right')
            
            plt.xlabel(x_column)
            plt.ylabel(y_column)
            plt.title(f"{y_column} over {x_column}")
            plt.grid(True, alpha=0.3)
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