#!/usr/bin/env python3
"""
Launcher script for Querypls application.
"""

import sys
import os
import argparse

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def run_streamlit():
    """Run the Streamlit application."""
    import subprocess
    import streamlit.web.cli as stcli
    
    # Set environment variables
    os.environ['STREAMLIT_SERVER_PORT'] = '8501'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = 'localhost'
    
    # Run streamlit
    sys.argv = [
        'streamlit', 'run',
        'src/frontend/app.py',
        '--server.port=8501',
        '--server.address=localhost'
    ]
    sys.exit(stcli.main())


def run_cli():
    """Run the CLI application."""
    from terminal.cli import main as cli_main
    cli_main()


def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(description='Querypls - SQL Generation Tool')
    parser.add_argument(
        'mode',
        choices=['web', 'cli'],
        default='web',
        nargs='?',
        help='Run mode: web (Streamlit) or cli (Command Line)'
    )
    parser.add_argument(
        'cli_args',
        nargs='*',
        help='Arguments to pass to CLI (when mode is cli)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'web':
        print("🚀 Starting Querypls Web Application...")
        run_streamlit()
    elif args.mode == 'cli':
        print("🚀 Starting Querypls CLI...")
        # Pass CLI arguments to the CLI
        if args.cli_args:
            sys.argv = ['cli'] + args.cli_args
        run_cli()


if __name__ == "__main__":
    main() 