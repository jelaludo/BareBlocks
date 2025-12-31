his tool exists to make image files legible beyond their pixels. Its purpose is to transparently inspect, parse, and explain the full range of data that can be embedded in an image—standard metadata, container-level structures, arbitrary payloads, and probabilistic signals—using clear, step-by-step analysis that runs entirely on the user’s device. Rather than promising certainty or forensic authority, it aims to educate users about what information is explicitly stored, what is merely possible, and what cannot be reliably known, fostering file-format literacy, informed skepticism, and a precise understanding of how modern images function as both visual media and data containers.

UI inspiration : 
https://dev.to/wesen/14-great-tips-to-make-amazing-cli-applications-3gp3




From GPT : 
Below is a module-level architecture with explicit step-by-step processing, where each step answers exactly two questions:

WHAT is being processed
WHAT RESULT is produced

No hand-waving, no “magic detection”.

Module-Level Architecture

Image Metadata & Embedded Data Inspector

0. Orchestrator Module

ImageInspectionController

WHAT

Receives a File object from browser input

Coordinates all inspection phases

Enforces order, timeouts, and UI updates

RESULT

Ordered execution

Unified inspection report object

Progress events emitted per phase

Phase 1 — File Intake & Normalization
Module: FileLoader
WHAT

Raw image file from <input> or drag-drop

Browser File API

STEPS

Read file as ArrayBuffer

Store original file size

Store MIME type (browser-declared, not trusted)

RESULT
{
  "buffer": ArrayBuffer,
  "fileSize": 4213982,
  "mimeHint": "image/png",
  "fileName": "image.png"
}

Phase 2 — Container Identification (Sniffing)
Module: ContainerSniffer
WHAT

First ~32 bytes of file

Known magic byte signatures

STEPS

Read magic bytes

Match against known formats

Reject unsupported or unknown formats

RESULT
{
  "containerType": "PNG",
  "confidence": "high"
}


(Example alternatives: JPEG, WEBP, HEIF)

Phase 3 — Structural Enumeration (Critical Phase)
Module: StructureParser
WHAT

Entire file buffer

Format-specific container rules

STEPS (PNG example)

Walk file sequentially

For each chunk:

Read length

Read type

Record offset

Record CRC validity

Classify chunk as:

Pixel data

Declared metadata

Custom / unknown

RESULT
{
  "chunks": [
    { "type": "IHDR", "offset": 8, "size": 13 },
    { "type": "iTXt", "offset": 33, "size": 182412 },
    { "type": "IDAT", "offset": 182461, "size": 1203881 },
    { "type": "IEND", "offset": 1386342, "size": 0 }
  ],
  "pixelDataBytes": 1203881,
  "nonPixelBytes": 182425
}


This phase does not decode anything.
It establishes where data lives.

Phase 4 — Declared Metadata Extraction
Module: DeclaredMetadataExtractor
WHAT

Known metadata regions only

EXIF / IPTC / XMP schemas

STEPS

Pass buffer to exifr

Parse EXIF fields

Parse IPTC fields

Parse XMP XML blocks

Preserve namespace boundaries

RESULT
{
  "exif": { "camera": "Sony A7", "iso": 200 },
  "iptc": { "caption": "Street photo" },
  "xmp": {
    "dc": { "creator": "Jelaludo" },
    "photoshop": { "History": "Edited" }
  }
}


Declared metadata only.
No guessing.

Phase 5 — Opaque Payload Detection
Module: OpaquePayloadScanner
WHAT

All non-pixel, non-declared data regions

STEPS

For each region:

Attempt UTF-8 decode

Attempt JSON parse

Attempt XML parse

Attempt zlib decompression

Calculate entropy

Detect magic bytes (ZIP, PDF, etc.)

RESULT
{
  "payloads": [
    {
      "source": "iTXt",
      "size": 182412,
      "classification": "compressed-json",
      "entropy": 7.9
    }
  ]
}


This is where ComfyUI workflows appear.

Phase 6 — AI / Workflow Pattern Recognition
Module: AIMetadataDetector
WHAT

Textual payloads

Known AI workflow patterns

STEPS

Scan payloads for:

JSON graph structures

Known ComfyUI node keys

Stable Diffusion parameter signatures

Identify:

Graph definition

Prompt templates

Seeds / samplers

Wildcard usage

RESULT
{
  "aiMetadata": {
    "tool": "ComfyUI",
    "graphDetected": true,
    "wildcardsPresent": true,
    "resolvedPromptAvailable": false
  }
}


Important:
This module never invents resolved prompts.

Phase 7 — Size & Anomaly Heuristics
Module: AnomalyAnalyzer
WHAT

Structural + payload statistics

STEPS

Compute:

Non-pixel data ratio

Largest chunk %

Compare against known norms

Flag unusual but valid patterns

RESULT
{
  "flags": [
    "large_non_pixel_data",
    "custom_chunks_present"
  ],
  "nonPixelRatio": 0.42
}


No alarmism.
Just classification.

Phase 8 — Pixel-Domain Steganography (Optional)
Module: SteganographyHeuristics
WHAT

Decoded pixel data only

STEPS

Extract RGB channels

Compute LSB variance

Generate entropy heatmap

Compare channel noise distributions

RESULT
{
  "lsbAnomaly": false,
  "entropyVariance": "normal",
  "confidence": "low"
}


Explicitly heuristic.

Phase 9 — Report Assembly
Module: InspectionReportBuilder
WHAT

Outputs of all previous modules

STEPS

Merge results

Preserve source attribution

Attach uncertainty labels

Format for UI consumption

RESULT
{
  "summary": {...},
  "structure": {...},
  "metadata": {...},
  "payloads": {...},
  "warnings": [...]
}

Phase 10 — UI Rendering & Disclosure
Module: UIRenderer
WHAT

Final inspection report

Progressive disclosure rules

STEPS

Render high-level summary

Gate advanced views behind tabs

Attach educational tooltips

Allow payload export (explicit user action)

RESULT

Transparent, educational UI

No hidden automation

No false certainty

Key Architectural Principles (Non-Negotiable)

Structure before semantics

Declared ≠ embedded ≠ inferred

Large ≠ malicious

Absence ≠ proof

User trust comes from precision

Final Consultant Verdict

This architecture:

Is technically defensible

Scales from casual users to experts

Avoids false claims

Teaches file-format literacy

Fits perfectly in a static, client-only site