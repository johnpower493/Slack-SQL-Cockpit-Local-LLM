"""
Utilities for formatting data and responses.
"""
import json
import re
import pandas as pd
import io
from typing import List, Dict, Any


def format_data_as_table(data: List[Dict[str, Any]], max_width: int = 30) -> str:
    """
    Format query results as a markdown table for Slack.
    
    Args:
        data: List of dictionaries representing query results
        max_width: Maximum width for each column
        
    Returns:
        Formatted table as string
    """
    if not data:
        return "```\n<no rows>\n```"
    
    try:
        df = pd.DataFrame(data)
        
        # Truncate long values
        def truncate_value(value, max_len=max_width):
            value_str = str(value)
            return value_str if len(value_str) <= max_len else value_str[:max_len-3] + "..."
        
        # Apply truncation using map() instead of deprecated applymap()
        for col in df.columns:
            df[col] = df[col].map(truncate_value)
        
        # Calculate column widths
        max_lengths = {}
        for col in df.columns:
            col_max = max(df[col].astype(str).apply(len).max(), len(col))
            max_lengths[col] = min(col_max, max_width)
        
        # Build table
        result = "```\n"
        
        # Header
        header = " | ".join(f"{col:{max_lengths[col]}}" for col in df.columns)
        result += header + "\n"
        
        # Separator
        separator = "-|-".join("-" * max_lengths[col] for col in df.columns)
        result += separator + "\n"
        
        # Rows
        for _, row in df.iterrows():
            # Clean cell values to prevent table breaking
            clean_cells = [str(cell).replace("\n", " ").replace("|", "/") for cell in row]
            row_str = " | ".join(
                f"{cell:{max_lengths[col]}}" 
                for col, cell in zip(df.columns, clean_cells)
            )
            result += row_str + "\n"
        
        result += "```"
        return result
        
    except Exception as e:
        return f"Failed to format table: {str(e)}"


def paginate_query_results(data: List[Dict[str, Any]], page_number: int, 
                          rows_per_page: int = 12) -> List[Dict[str, Any]]:
    """
    Paginate query results.
    
    Args:
        data: Complete query results
        page_number: Page number (1-based)
        rows_per_page: Number of rows per page
        
    Returns:
        Slice of data for the requested page
    """
    start_idx = max(0, (page_number - 1) * rows_per_page)
    end_idx = start_idx + rows_per_page
    return data[start_idx:end_idx]


def calculate_pagination_info(total_rows: int, page_number: int, 
                            rows_per_page: int = 12) -> Dict[str, int]:
    """
    Calculate pagination information.
    
    Args:
        total_rows: Total number of rows
        page_number: Current page number
        rows_per_page: Rows per page
        
    Returns:
        Dictionary with pagination info
    """
    total_pages = max(1, (total_rows + rows_per_page - 1) // rows_per_page)
    start_row = (page_number - 1) * rows_per_page + 1
    end_row = min(page_number * rows_per_page, total_rows)
    
    return {
        "total_pages": total_pages,
        "current_page": page_number,
        "start_row": start_row,
        "end_row": end_row,
        "total_rows": total_rows,
        "has_previous": page_number > 1,
        "has_next": page_number < total_pages,
        "previous_page": max(1, page_number - 1),
        "next_page": min(total_pages, page_number + 1)
    }


def extract_sql_from_slack_message(payload: Dict[str, Any]) -> str:
    """
    Extract SQL query from original Slack message.
    
    Args:
        payload: Slack interaction payload
        
    Returns:
        SQL query string or empty string if not found
    """
    original_text = (payload.get("original_message") or {}).get("text") or ""
    
    # Look for SQL in code blocks
    match = re.search(r"```(.*?)```", original_text, re.DOTALL)
    if not match:
        return ""
    
    sql = match.group(1).strip()
    # Clean up common prefixes and suffixes
    sql = re.sub(r"^sql\n", "", sql, flags=re.IGNORECASE).strip()
    sql = sql.rstrip(";").strip()
    
    return sql


def parse_page_command(command_text: str) -> tuple[str, int]:
    """
    Parse command text to extract query and page number.
    
    Args:
        command_text: Raw command text from Slack
        
    Returns:
        Tuple of (query_text, page_number)
    """
    # Look for page number pattern like "<2>" at the end
    page_match = re.search(r"<(\d+)>$", command_text.strip())
    
    if page_match:
        page_number = int(page_match.group(1))
        query_text = re.sub(r"\s*<\d+>$", "", command_text).strip()
    else:
        page_number = 1
        query_text = command_text.strip()
    
    return query_text, page_number