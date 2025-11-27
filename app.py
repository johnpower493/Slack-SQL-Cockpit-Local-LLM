"""
CircularQuery - Self-service analytics made easy.

A Flask application that converts natural language questions into SQL queries
using local LLM (Ollama), executes them against SQLite, and provides interactive
results with CSV export and plotting capabilities through Slack.
"""
import logging
import os
from flask import Flask

from config.settings import config
from routes.slack_routes import slack_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Validate configuration
        config.validate()
        logger.info("Configuration validated successfully")
        
        # Register blueprints
        app.register_blueprint(slack_bp)
        
        # Log startup information
        logger.info(f"Using SQLite database: {config.SQLITE_PATH}")
        if config.LLM_BACKEND == "groq":
            logger.info(f"Using Groq LLM backend with model: {config.GROQ_MODEL}")
        else:
            logger.info(f"Using Ollama LLM backend with model: {config.OLLAMA_MODEL} at {config.OLLAMA_BASE_URL}")
        
        # Display schema summary
        from services.database import DatabaseService
        schema_summary = DatabaseService.get_database_schema()
        logger.info(f"Database schema loaded: {len(schema_summary)} characters")
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        raise


def main():
    """Main entry point."""
    try:
        app = create_app()
        
        # Run the application
        app.run(
            host="0.0.0.0", 
            port=5000, 
            debug=config.DEBUG if hasattr(config, 'DEBUG') else True
        )
        
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Failed to start application: {e}")
        raise


if __name__ == '__main__':
    main()