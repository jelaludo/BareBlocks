#!/usr/bin/env python3
"""
BareBlocks - Local Development Runner
Simple script to test and run BareBlocks locally
"""

import sys
import os
from pathlib import Path

def print_banner():
    """Print a nice banner"""
    import io
    
    # Set UTF-8 encoding for Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("""
    ===============================================================
    
              BareBlocks - Metadata Inspector
    
         Making image files legible beyond their pixels
    
    ===============================================================
    """)

def show_menu():
    """Show interactive menu"""
    print("\n📋 Available Commands:\n")
    print("  1. CLI Tool - Extract metadata from a file")
    print("  2. Web App (Client-Side) - Static server (localhost:8000)")
    print("  3. GUI Tool - Open graphical interface")
    print("  4. Test with sample image")
    print("  5. Show help")
    print("  6. Exit")
    print()

def run_cli():
    """Run CLI tool interactively"""
    file_path = input("Enter path to file: ").strip()
    if not file_path:
        print("❌ No file path provided")
        return
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print("\n" + "="*60)
    print("Extracting metadata...")
    print("="*60 + "\n")
    
    os.system(f'python bareblocks-cli.py "{file_path}"')

def run_web():
    """Run client-side web app (static server)"""
    print("\n🚀 Starting static server on http://localhost:8000")
    print("📝 Open: http://localhost:8000/index.html\n")
    os.system('python -m http.server 8000')

def run_gui():
    """Run GUI tool"""
    print("\n🚀 Launching GUI...\n")
    os.system('python bareblocks-gui.py')

def test_sample():
    """Test with sample image"""
    sample_file = Path("images/screenshot.png")
    if not sample_file.exists():
        print("❌ Sample image not found. Please add a test image to images/")
        return
    
    print("\n" + "="*60)
    print("Testing with sample image...")
    print("="*60 + "\n")
    os.system(f'python bareblocks-cli.py "{sample_file}"')

def show_help():
    """Show help information"""
    print("""
    BareBlocks Usage Guide
    ===============================================================
    
    Command Line Interface (CLI):
    ------------------------------
    python bareblocks-cli.py <file_path>              # Extract metadata
    python bareblocks-cli.py <file_path> --format json # JSON output
    python bareblocks-cli.py <file_path> --save output.json # Save to file
    python bareblocks-cli.py <file_path> --open-maps  # Open GPS in maps
    
    Web Interface:
    --------------
    python run.py web                                 # Start static server
    python -m http.server 8000                        # Direct start
    
    Graphical Interface (GUI):
    ---------------------------
    python bareblocks-gui.py                          # Launch GUI
    
    Other Tools:
    ------------
    python bareblocks-remove.py <image>                # Remove metadata
    python demo_visualizations.py                     # Create visualizations
    
    Examples:
    ---------
    python bareblocks-cli.py images/screenshot.png
    python bareblocks-cli.py photo.jpg --format json --save meta.json
    """)

def main():
    """Main entry point"""
    print_banner()
    
    if len(sys.argv) > 1:
        # Direct command mode
        command = sys.argv[1].lower()
        if command == "cli":
            run_cli()
        elif command == "web" or command == "server" or command == "static":
            run_web()
        elif command == "gui":
            run_gui()
        elif command == "test":
            test_sample()
        elif command == "help":
            show_help()
        else:
            print(f"Unknown command: {command}")
            print("Use: python run.py [cli|web|static|gui|test|help]")
    else:
        # Interactive mode
        while True:
            show_menu()
            choice = input("Select option (1-6): ").strip()
            
            if choice == "1":
                run_cli()
            elif choice == "2":
                run_web()
            elif choice == "3":
                run_gui()
            elif choice == "4":
                test_sample()
            elif choice == "5":
                show_help()
            elif choice == "6":
                print("\n👋 Goodbye!\n")
                break
            else:
                print("❌ Invalid option. Please choose 1-6.")
            
            if choice != "6":
                if choice != "2":  # Don't wait for web server
                    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
