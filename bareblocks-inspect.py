#!/usr/bin/env python3
"""
BareBlocks Layered Inspector - CLI tool with Rich formatting
Shows step-by-step inspection process with beautiful terminal output
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.layered_inspector import LayeredInspector
from core.rich_display import RichDisplay

def main():
    parser = argparse.ArgumentParser(
        description='BareBlocks - Layered Image Inspector',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bareblocks-inspect.py image.png
  python bareblocks-inspect.py photo.jpg --json
  python bareblocks-inspect.py file.png --quiet
        """
    )
    parser.add_argument('file_path', help='Path to the image file to inspect')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress progress output')
    
    args = parser.parse_args()
    
    if not Path(args.file_path).exists():
        console = Console()
        console.print(f"[red]Error:[/red] File not found: {args.file_path}")
        sys.exit(1)
    
    console = Console()
    
    # Print banner
    banner = Text()
    banner.append("BareBlocks", style="bold cyan")
    banner.append(" - ", style="dim")
    banner.append("Layered Image Inspector", style="bold")
    banner.append("\n", style="dim")
    banner.append("Making image files legible beyond their pixels", style="dim italic")
    
    console.print(Panel(banner, border_style="cyan", padding=(1, 2)))
    console.print()
    
    # Run inspection
    inspector = LayeredInspector(console=console, verbose=not args.quiet)
    
    try:
        results = inspector.phase_0_orchestrate(args.file_path)
        final_report = results["phases"]["8_report"]
        
        if args.json:
            import json
            print(json.dumps(final_report, indent=2, default=str))
        else:
            # Display with Rich formatting
            display = RichDisplay(console=console)
            display.display_inspection_report(final_report)
            
            # Final summary
            console.print(Panel(
                "[bold green][OK] Inspection Complete[/bold green]\n"
                "[dim]All phases executed successfully. See above for detailed results.[/dim]",
                border_style="green"
            ))
    
    except Exception as e:
        console.print(f"[red]Error during inspection:[/red] {str(e)}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)

if __name__ == "__main__":
    main()

