"""
Rich Display Module - Beautiful terminal output for layered inspection
Creates Rich-formatted output matching the style of the Rich library demo
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text
from rich.columns import Columns
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich import box
from typing import Dict, Any, List

class RichDisplay:
    """Create beautiful Rich-formatted output for inspection results"""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
    
    def display_inspection_report(self, report: Dict[str, Any]):
        """Display complete inspection report with Rich formatting"""
        self.console.print()
        
        # Summary Panel
        summary = report.get("summary", {})
        self._display_summary(summary)
        
        # Structure Section
        structure = report.get("structure", {})
        self._display_structure(structure)
        
        # Metadata Section
        metadata = report.get("metadata", {})
        self._display_metadata(metadata)
        
        # Payloads Section
        payloads = report.get("payloads", {})
        self._display_payloads(payloads)
        
        # AI Metadata Section
        ai_metadata = report.get("aiMetadata", {})
        self._display_ai_metadata(ai_metadata)
        
        # Anomalies Section
        anomalies = report.get("anomalies", {})
        self._display_anomalies(anomalies)
    
    def _display_summary(self, summary: Dict[str, Any]):
        """Display summary information"""
        table = Table(show_header=False, box=box.ROUNDED, padding=(0, 2))
        table.add_column(style="cyan", width=20)
        table.add_column(style="green")
        
        table.add_row("[bold]File Name:[/bold]", summary.get("fileName", "Unknown"))
        table.add_row("[bold]File Size:[/bold]", f"{summary.get('fileSize', 0):,} bytes")
        table.add_row("[bold]Container:[/bold]", f"[bold cyan]{summary.get('containerType', 'Unknown')}[/bold cyan]")
        table.add_row("[bold]Has EXIF:[/bold]", "[green]Yes[/green]" if summary.get("hasExif") else "[red]No[/red]")
        table.add_row("[bold]Has Payloads:[/bold]", "[green]Yes[/green]" if summary.get("hasPayloads") else "[red]No[/red]")
        table.add_row("[bold]AI Metadata:[/bold]", "[green]Yes[/green]" if summary.get("hasAiMetadata") else "[red]No[/red]")
        
        self.console.print(Panel(table, title="[bold cyan]Inspection Summary[/bold cyan]", border_style="cyan"))
        self.console.print()
    
    def _display_structure(self, structure: Dict[str, Any]):
        """Display file structure information"""
        if not structure:
            return
        
        if "chunks" in structure:
            # PNG structure
            table = Table(title="[bold yellow]File Structure (PNG Chunks)[/bold yellow]", 
                        box=box.ROUNDED, show_header=True)
            table.add_column("Chunk Type", style="cyan", width=12)
            table.add_column("Size", style="green", justify="right")
            table.add_column("Offset", style="dim", justify="right")
            table.add_column("Purpose", style="yellow")
            
            chunk_purposes = {
                "IHDR": "Image Header",
                "PLTE": "Palette",
                "IDAT": "Image Data",
                "IEND": "Image End",
                "tEXt": "Text Metadata",
                "zTXt": "Compressed Text",
                "iTXt": "International Text",
                "tIME": "Last Modified",
                "pHYs": "Pixel Dimensions"
            }
            
            for chunk in structure.get("chunks", [])[:20]:  # Show first 20
                chunk_type = chunk.get("type", "UNKNOWN")
                size = chunk.get("size", 0)
                offset = chunk.get("offset", 0)
                purpose = chunk_purposes.get(chunk_type, "Data")
                
                table.add_row(
                    f"[bold]{chunk_type}[/bold]",
                    f"{size:,} bytes",
                    f"{offset:,}",
                    purpose
                )
            
            if len(structure.get("chunks", [])) > 20:
                table.add_row("...", "...", "...", f"[dim]+ {len(structure['chunks']) - 20} more[/dim]")
            
            self.console.print(table)
            
            # Statistics
            stats_table = Table(show_header=False, box=None, padding=(1, 2))
            stats_table.add_column(style="dim")
            stats_table.add_column(style="cyan")
            stats_table.add_row("Pixel Data:", f"{structure.get('pixelDataBytes', 0):,} bytes")
            stats_table.add_row("Non-Pixel Data:", f"{structure.get('nonPixelBytes', 0):,} bytes")
            stats_table.add_row("Total Chunks:", str(structure.get("totalChunks", 0)))
            self.console.print(stats_table)
        
        elif "segments" in structure:
            # JPEG structure
            table = Table(title="[bold yellow]File Structure (JPEG Segments)[/bold yellow]",
                        box=box.ROUNDED, show_header=True)
            table.add_column("Marker", style="cyan", width=12)
            table.add_column("Size", style="green", justify="right")
            table.add_column("Offset", style="dim", justify="right")
            
            for segment in structure.get("segments", [])[:20]:
                marker = segment.get("marker", "UNKNOWN")
                size = segment.get("size", 0)
                offset = segment.get("offset", 0)
                table.add_row(marker, f"{size:,} bytes", f"{offset:,}")
            
            self.console.print(table)
        
        self.console.print()
    
    def _display_metadata(self, metadata: Dict[str, Any]):
        """Display declared metadata"""
        exif = metadata.get("exif", {})
        image_props = metadata.get("image_properties", {})
        gps = metadata.get("gps", {})
        
        if not exif and not image_props:
            return
        
        # EXIF Table
        if exif:
            table = Table(title="[bold green]Declared Metadata (EXIF)[/bold green]",
                        box=box.ROUNDED, show_header=True)
            table.add_column("Tag", style="cyan", width=30)
            table.add_column("Value", style="green")
            
            # Show important tags first
            important_tags = ["Image Make", "Image Model", "EXIF DateTimeOriginal", 
                            "EXIF ISOSpeedRatings", "EXIF FNumber", "EXIF ExposureTime"]
            
            for tag in important_tags:
                if tag in exif:
                    value = exif[tag]
                    if isinstance(value, (list, dict)):
                        value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    table.add_row(tag, str(value))
            
            # Show other tags
            other_tags = [t for t in exif.keys() if t not in important_tags]
            for tag in other_tags[:15]:  # Limit to 15 more
                value = exif[tag]
                if isinstance(value, (list, dict)):
                    value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                table.add_row(tag, str(value))
            
            if len(other_tags) > 15:
                table.add_row("[dim]...[/dim]", f"[dim]+ {len(other_tags) - 15} more tags[/dim]")
            
            self.console.print(table)
        
        # Image Properties
        if image_props:
            props_table = Table(show_header=False, box=box.ROUNDED, padding=(1, 2))
            props_table.add_column(style="cyan", width=20)
            props_table.add_column(style="green")
            
            if "size" in image_props:
                size = image_props["size"]
                props_table.add_row("Dimensions:", f"{size.get('width')} × {size.get('height')}")
            props_table.add_row("Format:", image_props.get("format", "Unknown"))
            props_table.add_row("Color Mode:", image_props.get("mode", "Unknown"))
            if image_props.get("dpi"):
                props_table.add_row("DPI:", str(image_props["dpi"]))
            props_table.add_row("Color Profile:", "[green]Yes[/green]" if image_props.get("has_color_profile") else "[red]No[/red]")
            
            self.console.print(Panel(props_table, title="[bold green]Image Properties[/bold green]", 
                                    border_style="green"))
        
        # GPS
        if gps:
            gps_table = Table(show_header=False, box=box.ROUNDED, padding=(1, 2))
            gps_table.add_column(style="cyan")
            gps_table.add_column(style="green")
            for key, value in gps.items():
                gps_table.add_row(key, str(value))
            self.console.print(Panel(gps_table, title="[bold magenta]GPS Coordinates[/bold magenta]",
                                    border_style="magenta"))
        
        self.console.print()
    
    def _display_payloads(self, payloads_data: Dict[str, Any]):
        """Display opaque payloads"""
        payloads = payloads_data.get("payloads", [])
        if not payloads:
            return
        
        table = Table(title="[bold yellow]Opaque Payloads[/bold yellow]",
                     box=box.ROUNDED, show_header=True)
        table.add_column("Source", style="cyan", width=15)
        table.add_column("Size", style="green", justify="right")
        table.add_column("Classification", style="yellow")
        table.add_column("Preview", style="dim", width=40)
        
        for payload in payloads:
            source = payload.get("source", "Unknown")
            size = payload.get("size", 0)
            classification = payload.get("classification", "Unknown")
            content = payload.get("content", "")
            
            if isinstance(content, dict):
                preview = str(content)[:40] + "..." if len(str(content)) > 40 else str(content)
            elif isinstance(content, str):
                preview = content[:40] + "..." if len(content) > 40 else content
            else:
                preview = str(content)[:40]
            
            table.add_row(source, f"{size:,} bytes", classification, preview)
        
        self.console.print(table)
        self.console.print()
    
    def _display_ai_metadata(self, ai_data: Dict[str, Any]):
        """Display AI/workflow metadata"""
        ai_meta = ai_data.get("aiMetadata", {})
        if not ai_meta.get("tool"):
            return
        
        table = Table(show_header=False, box=box.ROUNDED, padding=(1, 2))
        table.add_column(style="cyan", width=25)
        table.add_column(style="green")
        
        table.add_row("[bold]AI Tool:[/bold]", ai_meta.get("tool", "Unknown"))
        table.add_row("[bold]Graph Detected:[/bold]", "[green]Yes[/green]" if ai_meta.get("graphDetected") else "[red]No[/red]")
        table.add_row("[bold]Wildcards Present:[/bold]", "[green]Yes[/green]" if ai_meta.get("wildcardsPresent") else "[red]No[/red]")
        table.add_row("[bold]Resolved Prompt:[/bold]", "[green]Available[/green]" if ai_meta.get("resolvedPromptAvailable") else "[red]Not Available[/red]")
        
        self.console.print(Panel(table, title="[bold magenta]AI/Workflow Metadata[/bold magenta]",
                                border_style="magenta"))
        self.console.print()
    
    def _display_anomalies(self, anomalies: Dict[str, Any]):
        """Display anomaly heuristics"""
        flags = anomalies.get("flags", [])
        ratio = anomalies.get("nonPixelRatio", 0)
        
        if flags:
            flags_text = ", ".join(flags)
            self.console.print(Panel(
                f"[yellow][!] Anomalies Detected:[/yellow] [cyan]{flags_text}[/cyan]\n"
                f"[dim]Non-pixel data ratio: {ratio:.1%}[/dim]",
                title="[bold yellow][!] Anomaly Analysis[/bold yellow]",
                border_style="yellow"
            ))
        else:
            self.console.print(Panel(
                f"[green][OK] No significant anomalies detected[/green]\n"
                f"[dim]Non-pixel data ratio: {ratio:.1%}[/dim]",
                title="[bold green][OK] Anomaly Analysis[/bold green]",
                border_style="green"
            ))
        
        self.console.print()

