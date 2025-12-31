"""
Layered Image Inspector - Phase-by-phase parsing architecture
Implements the step-by-step analysis from CursorInstructions_BareBlocks.md
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from rich.text import Text
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich import box
import exifread
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

class LayeredInspector:
    """
    Implements the layered parsing architecture:
    Phase 0: Orchestration
    Phase 1: File Intake & Normalization
    Phase 2: Container Identification (Sniffing)
    Phase 3: Structural Enumeration
    Phase 4: Declared Metadata Extraction
    Phase 5: Opaque Payload Detection
    Phase 6: AI/Workflow Pattern Recognition
    Phase 7: Size & Anomaly Heuristics
    Phase 8: Report Assembly
    """
    
    def __init__(self, console: Optional[Console] = None, verbose: bool = True):
        self.console = console or Console()
        self.verbose = verbose
        self.results = {}
        
    def _convert_exif_value(self, value):
        """Convert EXIF values to JSON-serializable format"""
        if hasattr(value, 'values'):  # IFDRational
            try:
                if len(value.values) == 1:
                    return float(value.values[0].num) / float(value.values[0].den)
                else:
                    return [float(v.num) / float(v.den) for v in value.values]
            except:
                return str(value)
        elif hasattr(value, 'num') and hasattr(value, 'den'):  # Rational
            try:
                return float(value.num) / float(value.den)
            except:
                return str(value)
        else:
            return str(value)
    
    def phase_0_orchestrate(self, file_path: str) -> Dict[str, Any]:
        """Phase 0: Orchestration - Coordinate all inspection phases"""
        if self.verbose:
            self.console.print("\n[bold cyan]Phase 0: Orchestration[/bold cyan]")
            self.console.print(f"[dim]Coordinating inspection phases for: {os.path.basename(file_path)}[/dim]\n")
        
        results = {
            "phases": {},
            "summary": {},
            "warnings": [],
            "uncertainties": []
        }
        
        # Execute phases in order
        results["phases"]["1_intake"] = self.phase_1_file_intake(file_path)
        results["phases"]["2_container"] = self.phase_2_container_identification(file_path, results["phases"]["1_intake"])
        results["phases"]["3_structure"] = self.phase_3_structural_enumeration(file_path, results["phases"]["2_container"])
        results["phases"]["4_metadata"] = self.phase_4_declared_metadata(file_path, results["phases"]["3_structure"])
        results["phases"]["5_payloads"] = self.phase_5_opaque_payloads(file_path, results["phases"]["3_structure"])
        results["phases"]["6_ai_patterns"] = self.phase_6_ai_patterns(results["phases"]["5_payloads"])
        results["phases"]["7_anomalies"] = self.phase_7_anomaly_heuristics(results)
        results["phases"]["8_report"] = self.phase_8_report_assembly(results)
        
        return results
    
    def phase_1_file_intake(self, file_path: str) -> Dict[str, Any]:
        """Phase 1: File Intake & Normalization"""
        if self.verbose:
            self.console.print("[bold yellow]Phase 1:[/bold yellow] [cyan]File Intake & Normalization[/cyan]")
            self.console.print("[dim]  WHAT: Raw file from input[/dim]")
            self.console.print("[dim]  STEPS: Read file, store size, detect MIME type[/dim]\n")
        
        file_stat = os.stat(file_path)
        file_size = file_stat.st_size
        
        # Read first bytes for MIME detection
        with open(file_path, 'rb') as f:
            first_bytes = f.read(32)
        
        # Detect MIME type from magic bytes
        mime_hint = self._detect_mime_from_bytes(first_bytes, file_path)
        
        result = {
            "fileSize": file_size,
            "fileName": os.path.basename(file_path),
            "filePath": os.path.abspath(file_path),
            "mimeHint": mime_hint,
            "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
        }
        
        if self.verbose:
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_row("[dim]File Size:[/dim]", f"[green]{file_size:,} bytes[/green]")
            table.add_row("[dim]MIME Hint:[/dim]", f"[cyan]{mime_hint}[/cyan]")
            table.add_row("[dim]File Name:[/dim]", f"[white]{result['fileName']}[/white]")
            self.console.print(table)
            self.console.print()
        
        return result
    
    def phase_2_container_identification(self, file_path: str, intake: Dict) -> Dict[str, Any]:
        """Phase 2: Container Identification (Sniffing)"""
        if self.verbose:
            self.console.print("[bold yellow]Phase 2:[/bold yellow] [cyan]Container Identification[/cyan]")
            self.console.print("[dim]  WHAT: First ~32 bytes of file (magic bytes)[/dim]")
            self.console.print("[dim]  STEPS: Read magic bytes, match against known formats[/dim]\n")
        
        with open(file_path, 'rb') as f:
            magic_bytes = f.read(32)
        
        container_type, confidence = self._identify_container(magic_bytes)
        
        result = {
            "containerType": container_type,
            "confidence": confidence,
            "magicBytes": magic_bytes[:16].hex()  # First 16 bytes as hex
        }
        
        if self.verbose:
            status_color = "green" if confidence == "high" else "yellow" if confidence == "medium" else "red"
            self.console.print(f"[dim]Container:[/dim] [bold {status_color}]{container_type}[/bold {status_color}]")
            self.console.print(f"[dim]Confidence:[/dim] [{status_color}]{confidence}[/{status_color}]")
            self.console.print(f"[dim]Magic Bytes:[/dim] [dim]{result['magicBytes']}[/dim]")
            self.console.print()
        
        return result
    
    def phase_3_structural_enumeration(self, file_path: str, container: Dict) -> Dict[str, Any]:
        """Phase 3: Structural Enumeration - Walk file structure"""
        if self.verbose:
            self.console.print("[bold yellow]Phase 3:[/bold yellow] [cyan]Structural Enumeration[/cyan]")
            self.console.print("[dim]  WHAT: Entire file buffer, format-specific container rules[/dim]")
            self.console.print("[dim]  STEPS: Walk file sequentially, identify chunks/segments[/dim]\n")
        
        container_type = container.get("containerType", "").upper()
        structure = {}
        
        if container_type == "PNG":
            structure = self._parse_png_structure(file_path)
        elif container_type in ["JPEG", "JPG"]:
            structure = self._parse_jpeg_structure(file_path)
        else:
            structure = {
                "format": container_type,
                "note": "Structure parsing not yet implemented for this format",
                "fileSize": os.path.getsize(file_path)
            }
        
        if self.verbose:
            if "chunks" in structure:
                self.console.print(f"[dim]Found {len(structure['chunks'])} chunks:[/dim]")
                for chunk in structure.get("chunks", [])[:5]:  # Show first 5
                    chunk_type = chunk.get("type", "UNKNOWN")
                    size = chunk.get("size", 0)
                    offset = chunk.get("offset", 0)
                    self.console.print(f"  [cyan]{chunk_type}[/cyan] - {size:,} bytes at offset {offset:,}")
                if len(structure.get("chunks", [])) > 5:
                    self.console.print(f"  [dim]... and {len(structure['chunks']) - 5} more[/dim]")
            self.console.print()
        
        return structure
    
    def phase_4_declared_metadata(self, file_path: str, structure: Dict) -> Dict[str, Any]:
        """Phase 4: Declared Metadata Extraction - EXIF, IPTC, XMP"""
        if self.verbose:
            self.console.print("[bold yellow]Phase 4:[/bold yellow] [cyan]Declared Metadata Extraction[/cyan]")
            self.console.print("[dim]  WHAT: Known metadata regions only (EXIF/IPTC/XMP schemas)[/dim]")
            self.console.print("[dim]  STEPS: Parse EXIF fields, IPTC fields, XMP XML blocks[/dim]\n")
        
        metadata = {
            "exif": {},
            "iptc": {},
            "xmp": {},
            "image_properties": {}
        }
        
        try:
            # EXIF data using exifread
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                
                for tag, value in tags.items():
                    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                        # Convert to JSON-serializable format
                        metadata["exif"][tag] = self._convert_exif_value(value)
            
            # Image properties using PIL
            with Image.open(file_path) as img:
                metadata["image_properties"] = {
                    "format": img.format,
                    "mode": img.mode,
                    "size": {"width": img.size[0], "height": img.size[1]},
                    "dpi": img.info.get('dpi', None),
                    "has_color_profile": 'icc_profile' in img.info
                }
                
                # GPS coordinates if available
                if hasattr(img, '_getexif') and img._getexif():
                    gps_info = self._extract_gps_from_pil(img)
                    if gps_info:
                        metadata["gps"] = gps_info
                        
        except Exception as e:
            metadata["error"] = str(e)
        
        if self.verbose:
            exif_count = len(metadata.get("exif", {}))
            if exif_count > 0:
                self.console.print(f"[green][OK][/green] Found [cyan]{exif_count}[/cyan] EXIF tags")
            else:
                self.console.print("[yellow][!][/yellow] No EXIF data found")
            
            if metadata.get("image_properties"):
                props = metadata["image_properties"]
                self.console.print(f"[green][OK][/green] Image: [cyan]{props.get('size', {}).get('width')}x{props.get('size', {}).get('height')}[/cyan] {props.get('format', '')}")
            
            if metadata.get("gps"):
                self.console.print(f"[green][OK][/green] GPS coordinates found")
            
            self.console.print()
        
        return metadata
    
    def phase_5_opaque_payloads(self, file_path: str, structure: Dict) -> Dict[str, Any]:
        """Phase 5: Opaque Payload Detection - Scan non-pixel data"""
        if self.verbose:
            self.console.print("[bold yellow]Phase 5:[/bold yellow] [cyan]Opaque Payload Detection[/cyan]")
            self.console.print("[dim]  WHAT: All non-pixel, non-declared data regions[/dim]")
            self.console.print("[dim]  STEPS: Attempt UTF-8 decode, JSON parse, XML parse, calculate entropy[/dim]\n")
        
        payloads = []
        
        # For PNG, check text chunks
        if "chunks" in structure:
            for chunk in structure.get("chunks", []):
                chunk_type = chunk.get("type", "")
                if chunk_type in ["tEXt", "zTXt", "iTXt"]:
                    payload_info = self._analyze_png_text_chunk(file_path, chunk)
                    if payload_info:
                        payloads.append(payload_info)
        
        if self.verbose:
            if payloads:
                self.console.print(f"[green][OK][/green] Found [cyan]{len(payloads)}[/cyan] opaque payload(s)")
                for payload in payloads:
                    self.console.print(f"  [dim]-[/dim] {payload.get('source', 'Unknown')}: {payload.get('classification', 'Unknown')}")
            else:
                self.console.print("[dim]No opaque payloads detected[/dim]")
            self.console.print()
        
        return {"payloads": payloads}
    
    def phase_6_ai_patterns(self, payloads_data: Dict) -> Dict[str, Any]:
        """Phase 6: AI/Workflow Pattern Recognition"""
        if self.verbose:
            self.console.print("[bold yellow]Phase 6:[/bold yellow] [cyan]AI/Workflow Pattern Recognition[/cyan]")
            self.console.print("[dim]  WHAT: Textual payloads, known AI workflow patterns[/dim]")
            self.console.print("[dim]  STEPS: Scan for ComfyUI, Stable Diffusion signatures[/dim]\n")
        
        ai_metadata = {
            "tool": None,
            "graphDetected": False,
            "wildcardsPresent": False,
            "resolvedPromptAvailable": False
        }
        
        # Check payloads for AI patterns
        for payload in payloads_data.get("payloads", []):
            # Check if payload is already marked as ComfyUI
            if payload.get("isComfyUI"):
                ai_metadata["tool"] = "ComfyUI"
                ai_metadata["graphDetected"] = True
                continue
            
            content = payload.get("content", "")
            
            # If content is already a dict (parsed JSON), check it directly
            if isinstance(content, dict):
                if content.get("nodes") or content.get("workflow") or content.get("prompt"):
                    ai_metadata["tool"] = "ComfyUI"
                    ai_metadata["graphDetected"] = True
                    continue
            
            # If content is a string, try to parse and check
            if isinstance(content, str):
                # Check for ComfyUI patterns in text
                if "comfy" in content.lower() or "workflow" in content.lower() or "CLIPTextEncode" in content:
                    ai_metadata["tool"] = "ComfyUI"
                    ai_metadata["graphDetected"] = True
                
                # Check for JSON workflow structures
                try:
                    data = json.loads(content)
                    if isinstance(data, dict):
                        if data.get("nodes") or data.get("workflow") or data.get("prompt"):
                            ai_metadata["tool"] = "ComfyUI"
                            ai_metadata["graphDetected"] = True
                        elif any(key in data for key in ["nodes", "links", "workflow"]):
                            ai_metadata["graphDetected"] = True
                            if not ai_metadata["tool"]:
                                ai_metadata["tool"] = "Unknown Workflow Tool"
                except:
                    pass
        
        if self.verbose:
            if ai_metadata["tool"]:
                self.console.print(f"[green][OK][/green] AI Tool detected: [cyan]{ai_metadata['tool']}[/cyan]")
                if ai_metadata["graphDetected"]:
                    self.console.print(f"[green][OK][/green] Workflow graph detected")
            else:
                self.console.print("[dim]No AI workflow patterns detected[/dim]")
            self.console.print()
        
        return {"aiMetadata": ai_metadata}
    
    def phase_7_anomaly_heuristics(self, all_results: Dict) -> Dict[str, Any]:
        """Phase 7: Size & Anomaly Heuristics"""
        if self.verbose:
            self.console.print("[bold yellow]Phase 7:[/bold yellow] [cyan]Size & Anomaly Heuristics[/cyan]")
            self.console.print("[dim]  WHAT: Structural + payload statistics[/dim]")
            self.console.print("[dim]  STEPS: Compute non-pixel data ratio, flag unusual patterns[/dim]\n")
        
        intake = all_results["phases"]["1_intake"]
        structure = all_results["phases"]["3_structure"]
        payloads = all_results["phases"]["5_payloads"]
        
        file_size = intake.get("fileSize", 0)
        flags = []
        
        # Calculate non-pixel data ratio
        pixel_data_bytes = structure.get("pixelDataBytes", 0)
        non_pixel_bytes = structure.get("nonPixelBytes", 0)
        
        if file_size > 0:
            non_pixel_ratio = non_pixel_bytes / file_size if file_size > 0 else 0
            
            if non_pixel_ratio > 0.3:  # More than 30% non-pixel data
                flags.append("large_non_pixel_data")
            
            if len(payloads.get("payloads", [])) > 0:
                flags.append("custom_chunks_present")
        
        result = {
            "flags": flags,
            "nonPixelRatio": round(non_pixel_ratio, 3) if file_size > 0 else 0,
            "fileSize": file_size,
            "pixelDataBytes": pixel_data_bytes,
            "nonPixelBytes": non_pixel_bytes
        }
        
        if self.verbose:
            if flags:
                self.console.print(f"[yellow][!][/yellow] Anomalies detected: [cyan]{', '.join(flags)}[/cyan]")
            else:
                self.console.print("[green][OK][/green] No significant anomalies")
            self.console.print(f"[dim]Non-pixel ratio:[/dim] [cyan]{result['nonPixelRatio']:.1%}[/cyan]")
            self.console.print()
        
        return result
    
    def phase_8_report_assembly(self, all_results: Dict) -> Dict[str, Any]:
        """Phase 8: Report Assembly - Merge all results"""
        if self.verbose:
            self.console.print("[bold yellow]Phase 8:[/bold yellow] [cyan]Report Assembly[/cyan]")
            self.console.print("[dim]  WHAT: Outputs of all previous modules[/dim]")
            self.console.print("[dim]  STEPS: Merge results, preserve source attribution, attach uncertainty labels[/dim]\n")
        
        report = {
            "summary": {
                "fileName": all_results["phases"]["1_intake"]["fileName"],
                "fileSize": all_results["phases"]["1_intake"]["fileSize"],
                "containerType": all_results["phases"]["2_container"]["containerType"],
                "hasExif": len(all_results["phases"]["4_metadata"].get("exif", {})) > 0,
                "hasPayloads": len(all_results["phases"]["5_payloads"].get("payloads", [])) > 0,
                "hasAiMetadata": all_results["phases"]["6_ai_patterns"]["aiMetadata"]["tool"] is not None
            },
            "structure": all_results["phases"]["3_structure"],
            "metadata": all_results["phases"]["4_metadata"],
            "payloads": all_results["phases"]["5_payloads"],
            "aiMetadata": all_results["phases"]["6_ai_patterns"],
            "anomalies": all_results["phases"]["7_anomalies"],
            "warnings": all_results.get("warnings", []),
            "uncertainties": all_results.get("uncertainties", [])
        }
        
        if self.verbose:
            self.console.print("[bold green][OK][/bold green] [bold]Inspection complete![/bold]")
            self.console.print()
        
        return report
    
    # Helper methods
    
    def _detect_mime_from_bytes(self, first_bytes: bytes, file_path: str) -> str:
        """Detect MIME type from magic bytes"""
        if first_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            return "image/png"
        elif first_bytes.startswith(b'\xff\xd8\xff'):
            return "image/jpeg"
        elif first_bytes.startswith(b'GIF87a') or first_bytes.startswith(b'GIF89a'):
            return "image/gif"
        elif first_bytes.startswith(b'BM'):
            return "image/bmp"
        elif first_bytes.startswith(b'RIFF') and b'WEBP' in first_bytes[:12]:
            return "image/webp"
        else:
            # Fallback to extension
            ext = Path(file_path).suffix.lower()
            ext_map = {
                '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                '.png': 'image/png', '.gif': 'image/gif',
                '.bmp': 'image/bmp', '.tiff': 'image/tiff', '.tif': 'image/tiff'
            }
            return ext_map.get(ext, 'application/octet-stream')
    
    def _identify_container(self, magic_bytes: bytes) -> tuple:
        """Identify container type from magic bytes"""
        if magic_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            return "PNG", "high"
        elif magic_bytes.startswith(b'\xff\xd8\xff'):
            return "JPEG", "high"
        elif magic_bytes.startswith(b'GIF87a') or magic_bytes.startswith(b'GIF89a'):
            return "GIF", "high"
        elif magic_bytes.startswith(b'BM'):
            return "BMP", "high"
        elif magic_bytes.startswith(b'RIFF') and b'WEBP' in magic_bytes[:12]:
            return "WEBP", "high"
        else:
            return "UNKNOWN", "low"
    
    def _parse_png_structure(self, file_path: str) -> Dict:
        """Parse PNG file structure - walk chunks"""
        chunks = []
        pixel_data_bytes = 0
        non_pixel_bytes = 8  # PNG signature
        
        with open(file_path, 'rb') as f:
            # Skip PNG signature (8 bytes)
            f.read(8)
            offset = 8
            
            while True:
                try:
                    # Read chunk length (4 bytes)
                    length_bytes = f.read(4)
                    if len(length_bytes) < 4:
                        break
                    
                    length = int.from_bytes(length_bytes, 'big')
                    
                    # Read chunk type (4 bytes)
                    chunk_type = f.read(4).decode('ascii', errors='ignore')
                    
                    # Read chunk data
                    chunk_data = f.read(length)
                    
                    # Read CRC (4 bytes)
                    crc = f.read(4)
                    
                    chunk_info = {
                        "type": chunk_type,
                        "size": length,
                        "offset": offset,
                        "hasData": len(chunk_data) > 0
                    }
                    
                    chunks.append(chunk_info)
                    
                    if chunk_type == "IDAT":
                        pixel_data_bytes += length
                    else:
                        non_pixel_bytes += length + 12  # +12 for length, type, CRC
                    
                    offset += length + 12
                    
                    if chunk_type == "IEND":
                        break
                        
                except Exception as e:
                    break
        
        return {
            "format": "PNG",
            "chunks": chunks,
            "pixelDataBytes": pixel_data_bytes,
            "nonPixelBytes": non_pixel_bytes,
            "totalChunks": len(chunks)
        }
    
    def _parse_jpeg_structure(self, file_path: str) -> Dict:
        """Parse JPEG file structure - walk segments"""
        segments = []
        non_pixel_bytes = 0
        
        with open(file_path, 'rb') as f:
            # Check SOI marker
            soi = f.read(2)
            if soi != b'\xff\xd8':
                return {"format": "JPEG", "error": "Invalid JPEG file"}
            
            non_pixel_bytes += 2
            offset = 2
            
            while True:
                try:
                    marker = f.read(2)
                    if len(marker) < 2:
                        break
                    
                    if marker[0] != 0xff:
                        break
                    
                    marker_type = marker[1]
                    
                    if marker_type == 0xd8:  # SOI
                        continue
                    elif marker_type == 0xd9:  # EOI
                        break
                    elif marker_type == 0xda:  # SOS (Start of Scan - image data starts)
                        # Skip to end of file or next marker
                        remaining = f.read()
                        pixel_data_size = len(remaining)
                        break
                    else:
                        # Read segment length
                        length_bytes = f.read(2)
                        if len(length_bytes) < 2:
                            break
                        length = int.from_bytes(length_bytes, 'big') - 2
                        
                        segment_data = f.read(length)
                        
                        segment_info = {
                            "marker": f"0xFF{marker_type:02X}",
                            "size": length,
                            "offset": offset
                        }
                        segments.append(segment_info)
                        non_pixel_bytes += length + 4
                        offset += length + 4
                        
                except Exception as e:
                    break
        
        return {
            "format": "JPEG",
            "segments": segments,
            "pixelDataBytes": pixel_data_size if 'pixel_data_size' in locals() else 0,
            "nonPixelBytes": non_pixel_bytes,
            "totalSegments": len(segments)
        }
    
    def _analyze_png_text_chunk(self, file_path: str, chunk: Dict) -> Optional[Dict]:
        """Analyze PNG text chunk for payloads"""
        try:
            with open(file_path, 'rb') as f:
                f.seek(chunk["offset"] + 8)  # Skip length and type
                data = f.read(chunk["size"])
                
                chunk_type = chunk["type"]
                
                # Parse tEXt chunks: keyword\0text
                if chunk_type == "tEXt":
                    try:
                        # Find null separator
                        null_pos = data.find(b'\x00')
                        if null_pos > 0:
                            keyword = data[:null_pos].decode('latin1', errors='ignore')
                            text_data = data[null_pos + 1:]
                            
                            # Try to decode as UTF-8
                            try:
                                text_value = text_data.decode('utf-8', errors='ignore')
                            except:
                                text_value = text_data.decode('latin1', errors='ignore')
                            
                            # Try JSON parse on the value
                            try:
                                json_data = json.loads(text_value)
                                # Check if it's a ComfyUI workflow
                                is_comfyui = (
                                    isinstance(json_data, dict) and 
                                    (json_data.get("nodes") or json_data.get("workflow") or json_data.get("prompt"))
                                )
                                return {
                                    "source": f"{chunk_type}:{keyword}",
                                    "size": chunk["size"],
                                    "classification": "json",
                                    "content": json_data,
                                    "keyword": keyword,
                                    "isComfyUI": is_comfyui
                                }
                            except:
                                # Not JSON, return as text
                                return {
                                    "source": f"{chunk_type}:{keyword}",
                                    "size": chunk["size"],
                                    "classification": "text",
                                    "content": text_value,
                                    "keyword": keyword
                                }
                    except:
                        pass
                
                # For zTXt and iTXt, try direct decode
                if chunk_type in ["zTXt", "iTXt"]:
                    try:
                        # zTXt: keyword\0compression_method\0compressed_text
                        # iTXt: more complex, but try similar approach
                        if chunk_type == "zTXt":
                            null_pos = data.find(b'\x00')
                            if null_pos > 0:
                                keyword = data[:null_pos].decode('latin1', errors='ignore')
                                # Skip compression method (1 byte) and null
                                compressed_data = data[null_pos + 2:]
                                # Try zlib decompression
                                try:
                                    import zlib
                                    decompressed = zlib.decompress(compressed_data)
                                    text_value = decompressed.decode('utf-8', errors='ignore')
                                    # Try JSON parse
                                    try:
                                        json_data = json.loads(text_value)
                                        is_comfyui = (
                                            isinstance(json_data, dict) and 
                                            (json_data.get("nodes") or json_data.get("workflow") or json_data.get("prompt"))
                                        )
                                        return {
                                            "source": f"{chunk_type}:{keyword}",
                                            "size": chunk["size"],
                                            "classification": "json",
                                            "content": json_data,
                                            "keyword": keyword,
                                            "isComfyUI": is_comfyui
                                        }
                                    except:
                                        return {
                                            "source": f"{chunk_type}:{keyword}",
                                            "size": chunk["size"],
                                            "classification": "text",
                                            "content": text_value,
                                            "keyword": keyword
                                        }
                                except:
                                    pass
                    except:
                        pass
                
                # Fallback: try direct decode
                try:
                    text = data.decode('utf-8', errors='ignore')
                    # Try JSON parse
                    try:
                        json_data = json.loads(text)
                        is_comfyui = (
                            isinstance(json_data, dict) and 
                            (json_data.get("nodes") or json_data.get("workflow") or json_data.get("prompt"))
                        )
                        return {
                            "source": chunk_type,
                            "size": chunk["size"],
                            "classification": "json",
                            "content": json_data,
                            "isComfyUI": is_comfyui
                        }
                    except:
                        return {
                            "source": chunk_type,
                            "size": chunk["size"],
                            "classification": "text",
                            "content": text[:500]  # First 500 chars
                        }
                except:
                    return {
                        "source": chunk_type,
                        "size": chunk["size"],
                        "classification": "binary",
                        "entropy": self._calculate_entropy(data)
                    }
        except Exception as e:
            if self.verbose:
                self.console.print(f"[dim]Error analyzing chunk {chunk.get('type')}: {e}[/dim]")
            return None
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy"""
        if not data:
            return 0
        entropy = 0
        for x in range(256):
            p_x = float(data.count(bytes([x]))) / len(data)
            if p_x > 0:
                entropy += - p_x * (p_x.bit_length() - 1)
        return round(entropy, 2)
    
    def _extract_gps_from_pil(self, img: Image.Image) -> Optional[Dict]:
        """Extract GPS coordinates from PIL image"""
        try:
            exif = img._getexif()
            if not exif:
                return None
            
            gps_ifd = exif.get(34853)  # GPS IFD tag
            if not gps_ifd:
                return None
            
            gps_data = {}
            for tag, value in gps_ifd.items():
                tag_name = GPSTAGS.get(tag, tag)
                gps_data[tag_name] = str(value)
            
            # Convert to decimal degrees if we have lat/lon
            if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                return gps_data
            
            return None
        except:
            return None

