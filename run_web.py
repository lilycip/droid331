#!/usr/bin/env python3
"""
Run the web interface for the Droid agent.
"""
import os
import sys
import argparse

def main():
    """Run the web interface."""
    parser = argparse.ArgumentParser(description="Run the Droid agent web interface")
    parser.add_argument("--port", type=int, default=12000, help="Port to run the web interface on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the web interface on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ["PORT"] = str(args.port)
    os.environ["FLASK_ENV"] = "development" if args.debug else "production"
    
    # Run the web interface
    from web.app import app
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()