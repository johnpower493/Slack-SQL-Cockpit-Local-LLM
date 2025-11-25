# Changelog

## [1.1.0] - 2024-01-XX

### Added
- **🔍 Insights Feature**: New AI-powered data analysis capability
  - Added "🔍 Insights" button to query results interface
  - LLM generates contextual, data-driven insights based on query results
  - Provides trend analysis, pattern detection, and business recommendations
  - Appears as in-channel response with formatted insights and data context
  - Includes row count footer and professional styling
  - Handles edge cases (empty data, failed generation) gracefully

- **📈 Line Plot Support**: Enhanced visualization capabilities
  - Added "📈 Line Plot" button alongside existing bar plots
  - Intelligent data type detection (datetime, numeric, categorical)
  - Automatic data sorting for proper line continuity
  - Grid lines and markers for better readability
  - Optimized for time series and trend analysis
  - Uses averaging for duplicate X values (vs summing for bar plots)

- **🎨 Professional Plot Styling**: Publication-ready visualizations
  - Modern color schemes using Seaborn palettes
  - High-resolution output (300 DPI) for crisp charts
  - Professional typography with bold labels and titles
  - Value labels on bar charts for easy reading
  - Data point labels on line charts (for ≤10 points)
  - Automatic trend lines for time series data
  - Enhanced grid styling and clean backgrounds
  - Smart number formatting with thousands separators
  - Improved axis labeling with proper title casing
  - Complementary color schemes for better visual appeal

### Enhanced
- **Improved Plot Experience**: Split single "Plot Data" into specific plot types
  - "📊 Bar Plot" for categorical comparisons
  - "📈 Line Plot" for trends and time series
  - Dynamic button text shows selected plot type
  - Session management tracks plot type selection
- **Better Slack Formatting**: Fixed Markdown rendering in insights
  - Converts standard Markdown to Slack's mrkdwn format
  - Proper bold (`**text**` → `*text*`) and italic formatting
  - Clean bullet points and headers
  - Enhanced LLM prompts for better formatted output
- Updated help command to include all new features
- Enhanced LLM service with `generate_insights()` method
- Improved user experience with emoji indicators and clear messaging
- Added comprehensive error handling for insights generation workflow

### Technical Details
- New `create_line_plot()` method in DataExportService
- Enhanced SessionManager with individual selection retrieval
- New endpoint handlers for `plot_bar` and `plot_line` actions
- Background processing for insights to prevent timeout issues
- Sample data limiting (first 10 rows) to optimize token usage
- Schema context inclusion for better LLM understanding
- Reuses existing SQL queries when possible for efficiency
- Markdown-to-Slack formatting converter function

---

All notable changes to CircularQuery will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-19

### 🎉 Release 1 - Major Refactoring

This release represents a complete architectural overhaul of CircularQuery, transforming it from a monolithic application into a secure, modular, production-ready system.

### Added
- **Modular Architecture**: Clean separation into services, routes, models, and utilities
- **Comprehensive Testing**: Unit tests for critical components and security functions
- **Enhanced Security**: Advanced SQL injection protection with pattern detection
- **Configuration Management**: Centralized, validated configuration system
- **Structured Logging**: Professional logging throughout the application
- **Type Safety**: Complete type hints across all modules
- **Documentation**: Comprehensive setup, usage, and migration guides
- **Test Runner**: Easy-to-use test execution script
- **Archive System**: Preserved legacy components for reference

### Security Fixes
- **SQL Injection**: Fixed vulnerable schema introspection using parameterized queries
- **Input Validation**: Enhanced validation for all user inputs and table names
- **Query Patterns**: Advanced detection of suspicious SQL patterns
- **System Protection**: Prevention of access to SQLite system tables
- **Excessive Limits**: Protection against resource exhaustion attacks
- **Comment Injection**: Blocking of comment-based SQL attacks

### Changed
- **File Structure**: Reorganized from single `app.py` into modular architecture
- **Error Handling**: Replaced print statements with structured logging
- **Database Access**: Enhanced safety with parameterized queries throughout
- **Code Quality**: Fixed deprecated `pandas.applymap()` usage
- **Import Organization**: Cleaned up and optimized module imports
- **Main Entry Point**: `app.py` now uses the new modular architecture

### Removed
- **Duplicate Code**: Eliminated redundant variable assignments and exception handlers
- **Deprecated Methods**: Replaced outdated pandas functions
- **Empty Directories**: Removed unused `adapters/` and placeholder directories
- **Monolithic Design**: Broke down 822-line single file into focused modules

### Fixed
- **Code Quality Issues**: Resolved all identified code quality problems
- **Security Vulnerabilities**: Addressed SQL injection and input validation issues
- **Error Messages**: Improved user-facing error messages and debugging information
- **Configuration Validation**: Added startup validation to catch configuration issues early

### Performance
- **Faster Startup**: Modular loading reduces initialization time
- **Better Error Recovery**: Improved resilience to service failures
- **Optimized Imports**: Reduced memory footprint and load times
- **Connection Management**: More efficient database connection handling

### Developer Experience
- **Easy Testing**: Simple `python run_tests.py` command
- **Clear Documentation**: Complete setup and usage instructions
- **Migration Guide**: Step-by-step checklist for upgrading
- **Rollback Support**: Preserved original components for quick reversion
- **Type Hints**: Full IDE support with type checking
- **Modular Development**: Easy to add new features and modify existing ones

### Migration Support
- **Backward Compatibility**: Same Slack commands and user experience
- **Migration Checklist**: Detailed step-by-step upgrade process
- **Rollback Plan**: Quick reversion capability if needed
- **Verification Steps**: Comprehensive testing procedures
- **Legacy Archive**: All original components preserved for reference

### Documentation
- **README.md**: Complete project overview and quick start guide
- **CHANGELOG.md**: This detailed change log
- **Archive Documentation**: Comprehensive refactoring and migration guides
- **Code Documentation**: Inline documentation throughout all modules
- **Test Documentation**: Clear test structure and execution instructions

## [0.1.0] - Previous Version (Archived)

### Legacy Features (Preserved in Archive)
- Original monolithic `app.py` implementation
- Basic SQL guardrails
- Slack integration for natural language queries
- CSV export and basic plotting functionality
- Simple error handling with print statements

---

## Version Numbering

- **Major Version (1.x.x)**: Breaking changes, major refactoring, architectural changes
- **Minor Version (x.1.x)**: New features, enhancements, backward-compatible changes
- **Patch Version (x.x.1)**: Bug fixes, security patches, minor improvements

## Upgrade Guide

When upgrading between versions:

1. **Check this changelog** for breaking changes and new features
2. **Review configuration changes** that might be required
3. **Run tests** to ensure compatibility with your setup
4. **Follow migration guides** provided in the archive documentation
5. **Test thoroughly** before deploying to production

---

**Note**: The archive folder contains complete documentation of the migration from the original version to Release 1, including detailed improvement analysis and step-by-step migration instructions.