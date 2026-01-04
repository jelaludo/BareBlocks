#!/usr/bin/env python3
"""
BareBlocks Web Interface - Browser-based CLI-style metadata inspector
Runs on localhost with a terminal-like interface
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory
import os
import json
import base64
from pathlib import Path
import sys

# Import our metadata extractor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bareblocks_cli_web import MetadataExtractor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# HTML Template with terminal styling
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BareBlocks - Terminal Interface</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
            background: #0d1117;
            color: #c9d1d9;
            overflow: hidden;
            height: 100vh;
        }
        
        .terminal-container {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            background: #0d1117;
        }
        
        .terminal-header {
            background: #161b22;
            padding: 10px 20px;
            border-bottom: 1px solid #30363d;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .terminal-title-area {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .terminal-title {
            color: #6FC3DF;
            font-weight: bold;
            font-size: 14px;
        }
        
        .terminal-tabs {
            display: flex;
            gap: 10px;
        }
        
        .tab-button {
            background: transparent;
            border: 1px solid #30363d;
            color: #8b949e;
            padding: 5px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
            font-size: 11px;
            transition: all 0.2s;
        }
        
        .tab-button:hover {
            background: #21262d;
            color: #c9d1d9;
            border-color: #6FC3DF;
        }
        
        .tab-button.active {
            background: #0d1117;
            color: #6FC3DF;
            border-color: #6FC3DF;
        }
        
        .parsing-flow-content {
            display: none;
            padding: 15px 20px;
            font-size: 11px;
            line-height: 1.6;
            color: #c9d1d9;
        }
        
        .parsing-flow-content.active {
            display: block;
        }
        
        .parsing-flow-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 10px 0;
        }
        
        @media (max-width: 768px) {
            .parsing-flow-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .parsing-flow-phase {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 12px;
        }
        
        .parsing-flow-content h3 {
            color: #89D185;
            font-size: 13px;
            margin: 0 0 8px 0;
            font-weight: bold;
        }
        
        .parsing-flow-content .phase-desc {
            color: #8b949e;
            margin-left: 0;
            margin-bottom: 0;
            white-space: pre-line;
            font-size: 10px;
            line-height: 1.5;
        }
        
        .parsing-flow-content .phase-title {
            color: #6FC3DF;
            font-weight: bold;
        }
        
        .chunks-content {
            display: none;
            padding: 15px 20px;
            font-size: 11px;
            color: #c9d1d9;
            overflow-y: auto;
            height: calc(100vh - 120px);
        }
        
        .chunks-content.active {
            display: block;
        }
        
        .chunks-header {
            margin-bottom: 20px;
        }
        
        .chunks-header h2 {
            color: #89D185;
            font-size: 16px;
            margin-bottom: 10px;
        }
        
        .chunks-stats {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            font-size: 11px;
            color: #8b949e;
        }
        
        .chunks-stat {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .chunks-stat-value {
            color: #6FC3DF;
            font-weight: bold;
        }
        
        .heatmap-container {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 20px;
        }
        
        .heatmap-title {
            color: #6FC3DF;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .heatmap-bar {
            width: 100%;
            height: 40px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 2px;
            position: relative;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .heatmap-segment {
            position: absolute;
            height: 100%;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            cursor: pointer;
            transition: opacity 0.2s, transform 0.1s;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 9px;
            color: rgba(255, 255, 255, 0.7);
            font-weight: bold;
        }
        
        .heatmap-segment:hover {
            opacity: 0.8;
            transform: scaleY(1.1);
            z-index: 10;
        }
        
        .heatmap-segment.tooltip-active {
            opacity: 0.9;
            z-index: 20;
        }
        
        .chunk-tooltip {
            position: absolute;
            background: #0d1117;
            border: 1px solid #6FC3DF;
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 10px;
            color: #c9d1d9;
            pointer-events: none;
            z-index: 100;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
            max-width: 300px;
        }
        
        .chunk-tooltip-title {
            color: #6FC3DF;
            font-weight: bold;
            margin-bottom: 4px;
        }
        
        .chunk-tooltip-detail {
            color: #8b949e;
            margin: 2px 0;
        }
        
        .chunks-legend {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #30363d;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 10px;
        }
        
        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 2px;
            border: 1px solid #30363d;
        }
        
        .chunks-list {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 15px;
        }
        
        .chunks-list-title {
            color: #6FC3DF;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .chunk-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px;
            border-bottom: 1px solid #30363d;
            font-size: 10px;
        }
        
        .chunk-item:last-child {
            border-bottom: none;
        }
        
        .chunk-item-number {
            color: #8b949e;
            font-weight: normal;
            min-width: 35px;
            text-align: right;
        }
        
        .chunk-item-type {
            color: #6FC3DF;
            font-weight: bold;
            min-width: 60px;
        }
        
        .chunk-item-size {
            color: #98C379;
            min-width: 80px;
        }
        
        .chunk-item-offset {
            color: #8b949e;
            min-width: 100px;
        }
        
        .chunk-item-purpose {
            color: #D19A66;
            flex: 1;
        }
        
        .chunk-item-type {
            cursor: pointer;
            text-decoration: underline;
            text-decoration-color: rgba(111, 195, 223, 0.5);
        }
        
        .chunk-item-type:hover {
            color: #89D185;
            text-decoration-color: #89D185;
        }
        
        .chunk-modal {
            position: fixed;
            background: #0d1117;
            border: 2px solid #6FC3DF;
            border-radius: 6px;
            padding: 15px;
            max-width: 600px;
            max-height: 70vh;
            overflow-y: auto;
            z-index: 1000;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.7);
            font-size: 11px;
            color: #c9d1d9;
        }
        
        .chunk-modal-header {
            color: #6FC3DF;
            font-weight: bold;
            font-size: 13px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid #30363d;
        }
        
        .chunk-modal-content {
            line-height: 1.6;
        }
        
        .chunk-modal-section {
            margin-bottom: 12px;
        }
        
        .chunk-modal-section-title {
            color: #89D185;
            font-weight: bold;
            font-size: 11px;
            margin-bottom: 6px;
        }
        
        .chunk-modal-text {
            color: #c9d1d9;
            white-space: pre-wrap;
            word-break: break-word;
            background: #161b22;
            padding: 8px;
            border-radius: 3px;
            border: 1px solid #30363d;
            font-family: 'Courier New', monospace;
            font-size: 10px;
        }
        
        .chunk-modal-hex {
            color: #98C379;
            font-family: 'Courier New', monospace;
            font-size: 10px;
            background: #161b22;
            padding: 8px;
            border-radius: 3px;
            border: 1px solid #30363d;
            white-space: pre;
            overflow-x: auto;
        }
        
        .chunk-modal-hex-line {
            margin-bottom: 2px;
        }
        
        .chunk-modal-hex-offset {
            color: #8b949e;
            margin-right: 8px;
        }
        
        .chunk-modal-hex-bytes {
            color: #6FC3DF;
            margin-right: 8px;
        }
        
        .chunk-modal-hex-ascii {
            color: #D19A66;
        }
        
        .chunk-modal-loading {
            color: #8b949e;
            font-style: italic;
        }
        
        .terminal-controls {
            display: flex;
            gap: 8px;
        }
        
        .control-btn {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            border: none;
            cursor: pointer;
        }
        
        .close { background: #ff5f56; }
        .minimize { background: #ffbd2e; }
        .maximize { background: #27c93f; }
        
        .terminal-body {
            flex: 1;
            padding: 10px 20px;
            overflow-y: auto;
            font-size: 13px;
            line-height: 1;
            display: flex;
            flex-direction: column;
        }
        
        .terminal-line {
            margin: 0;
            padding: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1;
            font-size: 13px;
            display: block;
        }
        
        .prompt {
            color: #6FC3DF;
        }
        
        .title {
            color: #89D185;
            font-weight: bold;
        }
        
        .subtitle {
            color: #9CDCFE;
            font-style: italic;
        }
        
        .command {
            color: #c9d1d9;
        }
        
        .output {
            color: #B294BB;
        }
        
        .error {
            color: #E06C75;
        }
        
        .success {
            color: #98C379;
        }
        
        .warning {
            color: #E5C07B;
        }
        
        .info {
            color: #61AFEF;
        }
        
        .phase {
            color: #56B6C2;
        }
        
        .summary {
            color: #9CDCFE;
        }
        
        .structure {
            color: #C678DD;
        }
        
        .metadata {
            color: #D19A66;
        }
        
        .payload {
            color: #B294BB;
        }
        
        .ai {
            color: #56B6C2;
        }
        
        .anomaly {
            color: #E06C75;
        }
        
        .comfyui {
            color: #D19A66;
        }
        
        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 10px 0;
        }
        
        @media (max-width: 1200px) {
            .metadata-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            .metadata-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .metadata-section {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 10px;
        }
        
        .metadata-section-title {
            font-weight: bold;
            font-size: 12px;
            margin-bottom: 8px;
            padding-bottom: 5px;
            border-bottom: 1px solid #30363d;
        }
        
        .metadata-section-title.summary {
            color: #9CDCFE;
        }
        
        .metadata-section-title.structure {
            color: #C678DD;
        }
        
        .metadata-section-title.metadata {
            color: #D19A66;
        }
        
        .metadata-section-title.comfyui {
            color: #D19A66;
        }
        
        .metadata-section-title.ai {
            color: #56B6C2;
        }
        
        .metadata-section-title.anomaly {
            color: #E06C75;
        }
        
        .metadata-section-title.payload {
            color: #B294BB;
        }
        
        .metadata-table {
            margin: 0;
            border-collapse: collapse;
            width: 100%;
            font-size: 11px;
            table-layout: fixed;
            border-spacing: 0;
        }
        
        .metadata-table th,
        .metadata-table td {
            padding: 3px 5px;
            text-align: left;
            border-bottom: 1px solid #30363d;
        }
        
        .metadata-table th:first-child,
        .metadata-table td:first-child {
            width: 35%;
            max-width: 220px;
            padding-right: 3px;
        }
        
        .metadata-table th:last-child,
        .metadata-table td:last-child {
            width: 72%;
            word-break: break-word;
            padding-left: 3px;
        }
        
        .metadata-table .expandable {
            cursor: pointer;
        }
        
        .metadata-table .expandable:hover {
            background: #161b22;
        }
        
        .metadata-table .toggle {
            color: #6FC3DF;
            font-weight: bold;
            margin-left: 5px;
        }
        
        .metadata-table .nested {
            font-size: 10px;
        }
        
        .metadata-table th {
            background: #161b22;
            color: #6FC3DF;
            font-weight: bold;
        }
        
        .metadata-table tr:hover {
            background: #161b22;
        }
        
        .metadata-table.table-summary th {
            color: #9CDCFE;
            border-bottom: 2px solid #9CDCFE;
        }
        
        .metadata-table.table-structure th {
            color: #C678DD;
            border-bottom: 2px solid #C678DD;
        }
        
        .metadata-table.table-metadata th {
            color: #D19A66;
            border-bottom: 2px solid #D19A66;
        }
        
        .metadata-table.table-payload th {
            color: #B294BB;
            border-bottom: 2px solid #B294BB;
        }
        
        .metadata-table.table-ai th {
            color: #56B6C2;
            border-bottom: 2px solid #56B6C2;
        }
        
        .metadata-table.table-anomaly th {
            color: #E06C75;
            border-bottom: 2px solid #E06C75;
        }
        
        .metadata-table.table-comfyui th {
            color: #D19A66;
            border-bottom: 2px solid #D19A66;
        }
        
        .data-recap {
            margin: 5px 0;
            font-size: 11px;
            line-height: 1.3;
        }
        
        .recap-item {
            display: inline-block;
            margin-right: 15px;
            margin-bottom: 2px;
        }
        
        .found {
            color: #98C379;
            font-weight: bold;
            cursor: pointer;
            text-decoration: underline;
            text-decoration-style: dotted;
        }
        
        .found:hover {
            color: #7fb069;
            text-decoration-style: solid;
        }
        
        .not-found {
            color: #6e7681;
        }
        
        .section-highlight {
            animation: highlightPulse 2s ease-in-out;
            outline: 3px solid #98C379;
            outline-offset: 4px;
            border-radius: 4px;
        }
        
        @keyframes highlightPulse {
            0% {
                outline-color: #98C379;
                outline-width: 3px;
            }
            50% {
                outline-color: #7fb069;
                outline-width: 5px;
            }
            100% {
                outline-color: #98C379;
                outline-width: 3px;
            }
        }
        
        .copy-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 16px;
            height: 16px;
            cursor: pointer;
            opacity: 0.7;
            transition: opacity 0.2s;
            vertical-align: middle;
            position: relative;
        }
        
        .copy-icon:hover {
            opacity: 1;
        }
        
        .copy-icon::before,
        .copy-icon::after {
            content: '';
            position: absolute;
            border: 1.5px solid #6FC3DF;
            background: transparent;
        }
        
        .copy-icon::before {
            width: 10px;
            height: 10px;
            top: 2px;
            left: 2px;
        }
        
        .copy-icon::after {
            width: 10px;
            height: 10px;
            top: 4px;
            left: 4px;
            border-color: #8b949e;
        }
        
        .copy-icon:hover::before,
        .copy-icon:hover::after {
            border-color: #6FC3DF;
        }
        
        .copy-icon.copied::before,
        .copy-icon.copied::after {
            display: none;
        }
        
        .copy-icon.copied::before {
            content: '✓';
            display: block;
            border: none;
            color: #98C379;
            font-size: 14px;
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
        
        .provenance-summary {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 12px;
        }
        
        .provenance-summary-title {
            color: #89D185;
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 13px;
        }
        
        .provenance-line {
            margin: 8px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .provenance-label {
            color: #8b949e;
            min-width: 80px;
            font-weight: bold;
        }
        
        .provenance-value {
            color: #6FC3DF;
            flex: 1;
        }
        
        .provenance-gps {
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        
        .geo-data-clickable {
            cursor: pointer;
            color: #6FC3DF;
            text-decoration: underline;
            text-decoration-style: dotted;
        }
        
        .geo-data-clickable:hover {
            color: #89D185;
        }
        
        .input-area {
            display: flex;
            align-items: center;
            padding: 10px 20px;
            background: #161b22;
            border-top: 1px solid #30363d;
        }
        
        .input-prompt {
            color: #6FC3DF;
            margin-right: 10px;
        }
        
        .input-field {
            flex: 1;
            background: transparent;
            border: none;
            color: #c9d1d9;
            font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            outline: none;
        }
        
        .input-field::placeholder {
            color: #6e7681;
        }
        
        .upload-area {
            margin: 20px 0;
            padding: 20px;
            border: 2px dashed #30363d;
            border-radius: 4px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .upload-area:hover {
            border-color: #6FC3DF;
            background: #161b22;
        }
        
        .upload-area.dragover {
            border-color: #6FC3DF;
            background: #0c1116;
        }
        
        .file-input {
            display: none;
        }
        
        .btn {
            padding: 8px 16px;
            background: #238636;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            margin-left: 10px;
        }
        
        .btn:hover {
            background: #2ea043;
        }
        
        .json-output {
            background: #161b22;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
            overflow-x: auto;
            font-size: 12px;
        }
        
        .json-key { color: #79c0ff; }
        .json-string { color: #a5d6ff; }
        .json-number { color: #79c0ff; }
        .json-boolean { color: #ff7b72; }
        
        ::-webkit-scrollbar {
            width: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #0d1117;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #30363d;
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #484f58;
        }
    </style>
</head>
<body>
    <div class="terminal-container">
        <div class="terminal-header">
            <div class="terminal-title-area">
                <div class="terminal-title">BareBlocks Terminal</div>
                <div class="terminal-tabs">
                    <button class="tab-button active" id="mainTab" onclick="switchTab('main')">Terminal</button>
                    <button class="tab-button" id="flowTab" onclick="switchTab('flow')">Parsing Flow</button>
                    <button class="tab-button" id="chunksTab" onclick="switchTab('chunks')">Chunks</button>
                </div>
            </div>
            <div class="terminal-controls">
                <button class="control-btn close" onclick="window.close()" title="Close window"></button>
            </div>
        </div>
        
        <div class="terminal-body" id="terminal"><div class="terminal-line"><span class="prompt">$</span> <span class="title">BareBlocks - Metadata Inspector</span></div><div class="terminal-line"><span class="prompt">$</span> <span class="subtitle">Making image files legible beyond their pixels</span></div><div class="terminal-line"><span class="prompt">$</span> <span class="command">bareblocks --help</span></div><div class="terminal-line output">Usage: bareblocks &lt;file_path&gt; [options]</div><div class="terminal-line output">Options:</div><div class="terminal-line output">&nbsp;&nbsp;--format json    Output as JSON <span class="copy-icon" onclick="exportJSON()" title="Click to download JSON file" style="margin-left: 8px; cursor: pointer;"></span></div><div class="terminal-line output">&nbsp;&nbsp;--save FILE      Save metadata to file</div><div class="terminal-line"><span class="prompt">$</span> <span class="command">bareblocks &lt;file&gt;</span></div></div>
        
        <div class="parsing-flow-content" id="parsingFlow">
            <div class="parsing-flow-grid">
                <div class="parsing-flow-phase"><h3><span class="phase-title">Phase 0: Orchestration</span></h3><div class="phase-desc">Entry point: phase_0_orchestrate(file_path)
Calls phases 1–8 sequentially
Aggregates results into final report</div></div>
                <div class="parsing-flow-phase"><h3><span class="phase-title">Phase 1: File Intake</span></h3><div class="phase-desc">Reads file into memory
Validates file exists and is readable
Records file size, path, name
Returns basic file info</div></div>
                <div class="parsing-flow-phase"><h3><span class="phase-title">Phase 2: Container Identification</span></h3><div class="phase-desc">Reads first 8–16 bytes (magic bytes)
Matches against known signatures:
  PNG: 89 50 4E 47 0D 0A 1A 0A
  JPEG: FF D8 FF
  WEBP: RIFF...WEBP
Returns container type and confidence</div></div>
                <div class="parsing-flow-phase"><h3><span class="phase-title">Phase 3: Structural Enumeration (PNG example)</span></h3><div class="phase-desc">Skips signature (8 bytes)
Iterates chunks:
  Read 4-byte length (big-endian)
  Read 4-byte chunk type (ASCII)
  Read chunk data (length bytes)
  Read 4-byte CRC
  Record: type, offset, size, hasData flag
Classifies: pixel data (IDAT) vs metadata (tEXt, zTXt, iTXt, etc.)
Stops at IEND
Returns: chunk list, pixel bytes, non-pixel bytes</div></div>
                <div class="parsing-flow-phase"><h3><span class="phase-title">Phase 4: Declared Metadata</span></h3><div class="phase-desc">Uses exifread for EXIF/IPTC/XMP
Uses PIL for image properties (dimensions, mode, format)
Extracts GPS if present
Returns structured metadata dict</div></div>
                <div class="parsing-flow-phase"><h3><span class="phase-title">Phase 5: Opaque Payload Detection</span></h3><div class="phase-desc">For each non-pixel chunk (tEXt, zTXt, iTXt):
  Read chunk data from file at recorded offset
  Parse tEXt: keyword\0value (split on null byte)
  Parse zTXt: decompress with zlib after keyword/compression byte
  Attempt UTF-8 decode
  Attempt JSON parse
  Classify: json, text, or binary
  Calculate entropy if binary
Returns: payload array with source, size, classification, content</div></div>
                <div class="parsing-flow-phase"><h3><span class="phase-title">Phase 6: AI Pattern Recognition</span></h3><div class="phase-desc">Scans payloads for:
  JSON with nodes, workflow, or prompt keys
  String content containing "comfy", "workflow", "CLIPTextEncode"
Sets tool: "ComfyUI" if detected
Returns: AI metadata dict</div></div>
                <div class="parsing-flow-phase"><h3><span class="phase-title">Phase 7: Anomaly Heuristics</span></h3><div class="phase-desc">Computes: non-pixel ratio = non-pixel bytes / total bytes
Flags if ratio > threshold (e.g., >0.1)
Returns: anomaly flags and statistics</div></div>
                <div class="parsing-flow-phase"><h3><span class="phase-title">Phase 8: Report Assembly</span></h3><div class="phase-desc">Merges all phase outputs
Structures as: summary, structure, metadata, payloads, aiMetadata, anomalies
Returns: complete inspection report</div></div>
                <div class="parsing-flow-phase"><h3><span class="phase-title">Web Interface Processing</span></h3><div class="phase-desc">Receives report JSON
Extracts ComfyUI data:
  Finds payload with keyword: "prompt" → node structure
  Finds payload with keyword: "workflow" → workflow structure
  Iterates nodes, extracts inputs.text (string values only)
  Extracts model from UNETLoader node
  Extracts LoRA from LoraLoader node
  Extracts sampler/steps from KSampler node
Displays: workflow params → prompt (green) → workflow info
Data flow: File → Chunks → Payloads → JSON Parse → Node Traversal → Field Extraction → Display</div></div>
            </div>
        </div>
        
        <div class="chunks-content" id="chunksContent">
            <div class="chunks-header">
                <h2>File Structure Heatmap</h2>
                <div class="chunks-stats" id="chunksStats">
                    <div class="chunks-stat"><span>Total Chunks:</span><span class="chunks-stat-value" id="totalChunks">-</span></div>
                    <div class="chunks-stat"><span>File Size:</span><span class="chunks-stat-value" id="fileSize">-</span></div>
                    <div class="chunks-stat"><span>Pixel Data:</span><span class="chunks-stat-value" id="pixelData">-</span></div>
                    <div class="chunks-stat"><span>Non-Pixel Data:</span><span class="chunks-stat-value" id="nonPixelData">-</span></div>
                </div>
            </div>
            <div class="heatmap-container">
                <div class="heatmap-title">File Layout (proportional)</div>
                <div class="heatmap-bar" id="heatmapBar"></div>
                <div class="chunks-legend" id="chunksLegend"></div>
            </div>
            <div class="chunks-list">
                <div class="chunks-list-title">Chunk Details</div>
                <div id="chunksList"></div>
            </div>
        </div>
        
        <div class="input-area">
            <span class="input-prompt">$</span>
            <input type="file" id="fileInput" class="file-input" accept="image/*,video/*,audio/*,.pdf,.docx">
            <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
                <span class="info">🗀 Click or drag file here to analyze</span>
            </div>
        </div>
    </div>
    
    <script>
        // Global variables - will be initialized after DOM loads
        let terminal, fileInput, uploadArea, parsingFlow, chunksContent;
        
        function switchTab(tab) {
            const mainTab = document.getElementById('mainTab');
            const flowTab = document.getElementById('flowTab');
            const chunksTab = document.getElementById('chunksTab');
            
            // Reset all tabs
            terminal.style.display = 'none';
            parsingFlow.classList.remove('active');
            chunksContent.classList.remove('active');
            mainTab.classList.remove('active');
            flowTab.classList.remove('active');
            chunksTab.classList.remove('active');
            
            if (tab === 'main') {
                terminal.style.display = 'flex';
                mainTab.classList.add('active');
            } else if (tab === 'flow') {
                parsingFlow.classList.add('active');
                flowTab.classList.add('active');
            } else if (tab === 'chunks') {
                chunksContent.classList.add('active');
                chunksTab.classList.add('active');
            }
        }
        
        // Make switchTab globally accessible
        window.switchTab = switchTab;
        
        // Chunk color mapping (Rich pastel palette)
        const chunkColors = {
            'IHDR': '#6FC3DF',  // Header - cyan
            'PLTE': '#B294BB',  // Palette - purple
            'IDAT': '#98C379',  // Image data - green
            'IEND': '#E06C75',  // End - red
            'tEXt': '#D19A66',  // Text - orange
            'zTXt': '#56B6C2',  // Compressed text - cyan
            'iTXt': '#C678DD',  // International text - magenta
            'tIME': '#E5C07B',  // Time - yellow
            'pHYs': '#9CDCFE',  // Physical - light blue
            'gAMA': '#61AFEF',  // Gamma - blue
            'cHRM': '#89D185',  // Chromaticity - green
            'DEFAULT': '#8b949e' // Default - gray
        };
        
        const chunkPurposes = {
            'IHDR': 'Image Header',
            'PLTE': 'Color Palette',
            'IDAT': 'Image Data (Pixel)',
            'IEND': 'Image End Marker',
            'tEXt': 'Text Metadata',
            'zTXt': 'Compressed Text',
            'iTXt': 'International Text',
            'tIME': 'Last Modified Time',
            'pHYs': 'Pixel Dimensions',
            'gAMA': 'Gamma Correction',
            'cHRM': 'Chromaticity',
            'DEFAULT': 'Data Chunk'
        };
        
        function updateChunksVisualization(structure) {
            const chunks = structure.chunks || [];
            if (chunks.length === 0) {
                console.log('No chunks to visualize');
                return;
            }
            
            console.log('Updating chunks visualization with', chunks.length, 'chunks');
            
            // Update stats
            const totalChunks = chunks.length;
            const fileSize = (structure.pixelDataBytes || 0) + (structure.nonPixelBytes || 0);
            const pixelData = structure.pixelDataBytes || 0;
            const nonPixelData = structure.nonPixelBytes || 0;
            
            document.getElementById('totalChunks').textContent = totalChunks;
            document.getElementById('fileSize').textContent = formatBytes(fileSize);
            document.getElementById('pixelData').textContent = formatBytes(pixelData);
            document.getElementById('nonPixelData').textContent = formatBytes(nonPixelData);
            
            // Calculate total size for proportional display
            let totalSize = 0;
            chunks.forEach(chunk => {
                totalSize += (chunk.size || 0) + 12; // size + 4 (length) + 4 (type) + 4 (CRC)
            });
            totalSize += 8; // PNG signature
            
            // Create heatmap
            const heatmapBar = document.getElementById('heatmapBar');
            if (!heatmapBar) {
                console.error('Heatmap bar element not found');
                return;
            }
            heatmapBar.innerHTML = '';
            
            let currentOffset = 0;
            const barWidth = heatmapBar.offsetWidth || 800; // Fallback width
            
            chunks.forEach((chunk, index) => {
                const chunkType = chunk.type || 'UNKNOWN';
                const chunkSize = (chunk.size || 0) + 12; // Include overhead
                const percentage = (chunkSize / totalSize) * 100;
                const width = (percentage / 100) * barWidth;
                
                if (width < 1) return; // Skip chunks too small to display
                
                const segment = document.createElement('div');
                segment.className = 'heatmap-segment';
                segment.style.left = `${(currentOffset / totalSize) * 100}%`;
                segment.style.width = `${percentage}%`;
                segment.style.background = chunkColors[chunkType] || chunkColors.DEFAULT;
                segment.textContent = chunkType;
                segment.title = `${chunkType}: ${formatBytes(chunk.size || 0)} at offset ${chunk.offset || 0}`;
                
                // Tooltip on hover
                let tooltip = null;
                segment.addEventListener('mouseenter', (e) => {
                    tooltip = document.createElement('div');
                    tooltip.className = 'chunk-tooltip';
                    tooltip.innerHTML = `
                        <div class="chunk-tooltip-title">${chunkType}</div>
                        <div class="chunk-tooltip-detail">Size: ${formatBytes(chunk.size || 0)}</div>
                        <div class="chunk-tooltip-detail">Offset: ${(chunk.offset || 0).toLocaleString()}</div>
                        <div class="chunk-tooltip-detail">Purpose: ${chunkPurposes[chunkType] || chunkPurposes.DEFAULT}</div>
                    `;
                    document.body.appendChild(tooltip);
                    segment.classList.add('tooltip-active');
                    
                    const rect = segment.getBoundingClientRect();
                    tooltip.style.left = `${rect.left + rect.width / 2 - 150}px`;
                    tooltip.style.top = `${rect.bottom + 5}px`;
                });
                
                segment.addEventListener('mouseleave', () => {
                    if (tooltip) {
                        tooltip.remove();
                        tooltip = null;
                    }
                    segment.classList.remove('tooltip-active');
                });
                
                heatmapBar.appendChild(segment);
                currentOffset += chunkSize;
            });
            
            // Create legend
            const legend = document.getElementById('chunksLegend');
            if (legend) {
                legend.innerHTML = '';
                const uniqueTypes = [...new Set(chunks.map(c => c.type))];
                uniqueTypes.forEach(type => {
                    const item = document.createElement('div');
                    item.className = 'legend-item';
                    const colorBox = document.createElement('div');
                    colorBox.className = 'legend-color';
                    colorBox.style.background = chunkColors[type] || chunkColors.DEFAULT;
                    item.appendChild(colorBox);
                    const label = document.createElement('span');
                    label.textContent = `${type} (${chunkPurposes[type] || chunkPurposes.DEFAULT})`;
                    item.appendChild(label);
                    legend.appendChild(item);
                });
            }
            
            // Create chunks list
            const chunksList = document.getElementById('chunksList');
            if (chunksList) {
                chunksList.innerHTML = '';
                chunks.forEach((chunk, index) => {
                    const item = document.createElement('div');
                    item.className = 'chunk-item';
                    const number = document.createElement('div');
                    number.className = 'chunk-item-number';
                    number.textContent = `${index + 1}.`;
                    const type = document.createElement('div');
                    type.className = 'chunk-item-type';
                    type.textContent = chunk.type || 'UNKNOWN';
                    type.dataset.chunkIndex = index;
                    type.dataset.chunkType = chunk.type;
                    type.dataset.chunkOffset = chunk.offset || 0;
                    type.dataset.chunkSize = chunk.size || 0;
                    
                    // Add hover handler for modal
                    let modal = null;
                    let hoverTimeout = null;
                    
                    type.addEventListener('mouseenter', (e) => {
                        hoverTimeout = setTimeout(() => {
                            showChunkModal(chunk, index, e);
                        }, 300); // Small delay to avoid accidental triggers
                    });
                    
                    type.addEventListener('mouseleave', () => {
                        if (hoverTimeout) {
                            clearTimeout(hoverTimeout);
                            hoverTimeout = null;
                        }
                        // Remove modal if it exists
                        const existingModal = document.querySelector('.chunk-modal');
                        if (existingModal) {
                            existingModal.remove();
                        }
                    });
                    
                    const size = document.createElement('div');
                    size.className = 'chunk-item-size';
                    size.textContent = formatBytes(chunk.size || 0);
                    const offset = document.createElement('div');
                    offset.className = 'chunk-item-offset';
                    offset.textContent = `@ ${(chunk.offset || 0).toLocaleString()}`;
                    const purpose = document.createElement('div');
                    purpose.className = 'chunk-item-purpose';
                    purpose.textContent = chunkPurposes[chunk.type] || chunkPurposes.DEFAULT;
                    
                    item.appendChild(number);
                    item.appendChild(type);
                    item.appendChild(size);
                    item.appendChild(offset);
                    item.appendChild(purpose);
                    chunksList.appendChild(item);
                });
            }
        }
        
        function formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
        }
        
        function showChunkModal(chunk, index, event) {
            // Remove any existing modal
            const existingModal = document.querySelector('.chunk-modal');
            if (existingModal) {
                existingModal.remove();
            }
            
            const modal = document.createElement('div');
            modal.className = 'chunk-modal';
            modal.innerHTML = '<div class="chunk-modal-loading">Loading chunk content...</div>';
            document.body.appendChild(modal);
            
            // Position modal near cursor
            const rect = event.target.getBoundingClientRect();
            modal.style.left = `${rect.right + 10}px`;
            modal.style.top = `${rect.top}px`;
            
            // Adjust if modal goes off screen
            setTimeout(() => {
                const modalRect = modal.getBoundingClientRect();
                if (modalRect.right > window.innerWidth) {
                    modal.style.left = `${rect.left - modalRect.width - 10}px`;
                }
                if (modalRect.bottom > window.innerHeight) {
                    modal.style.top = `${window.innerHeight - modalRect.height - 10}px`;
                }
            }, 0);
            
            // Store modal reference for cleanup
            event.target._modal = modal;
            
            // Close modal when mouse leaves modal or type element
            const closeModal = () => {
                if (modal && modal.parentNode) {
                    modal.remove();
                    event.target._modal = null;
                }
            };
            
            modal.addEventListener('mouseleave', closeModal);
            event.target.addEventListener('mouseleave', closeModal);
            
            // Load and display content based on chunk type
            loadChunkContent(chunk, index, modal);
        }
        
        function loadChunkContent(chunk, chunkIndex, modal) {
            const chunkType = chunk.type;
            
            if (chunkType === 'IHDR') {
                // Parse IHDR header
                fetchChunkBytes(chunk.offset + 8, 13).then(bytes => {
                    if (bytes && bytes.length >= 13) {
                        const width = (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3];
                        const height = (bytes[4] << 24) | (bytes[5] << 16) | (bytes[6] << 8) | bytes[7];
                        const bitDepth = bytes[8];
                        const colorType = bytes[9];
                        const compression = bytes[10];
                        const filter = bytes[11];
                        const interlace = bytes[12];
                        
                        const colorTypes = {
                            0: 'Grayscale',
                            2: 'RGB',
                            3: 'Palette',
                            4: 'Grayscale with Alpha',
                            6: 'RGB with Alpha'
                        };
                        
                        modal.innerHTML = `
                            <div class="chunk-modal-header">IHDR - Image Header</div>
                            <div class="chunk-modal-content">
                                <div class="chunk-modal-section">
                                    <div class="chunk-modal-section-title">Dimensions</div>
                                    <div class="chunk-modal-text">Width: ${width} px\nHeight: ${height} px</div>
                                </div>
                                <div class="chunk-modal-section">
                                    <div class="chunk-modal-section-title">Color Settings</div>
                                    <div class="chunk-modal-text">Bit Depth: ${bitDepth}\nColor Type: ${colorTypes[colorType] || 'Unknown'} (${colorType})\nCompression: ${compression === 0 ? 'Deflate' : 'Unknown'}\nFilter: ${filter === 0 ? 'Adaptive' : 'Unknown'}\nInterlace: ${interlace === 0 ? 'None' : 'Adam7'}</div>
                                </div>
                            </div>
                        `;
                    } else {
                        modal.innerHTML = '<div class="chunk-modal-header">IHDR</div><div class="chunk-modal-content">Could not parse header data</div>';
                    }
                }).catch(err => {
                    modal.innerHTML = `<div class="chunk-modal-header">IHDR</div><div class="chunk-modal-content">Error loading header: ${err.message}</div>`;
                });
            } else if (['tEXt', 'zTXt', 'iTXt'].includes(chunkType)) {
                // Get from payloads if available
                const payloads = window.currentPayloads || [];
                const payload = payloads.find(p => {
                    const source = p.source || '';
                    return source.includes(chunkType) && (p.keyword || '').length > 0;
                });
                
                if (payload && payload.content) {
                    let content = '';
                    if (typeof payload.content === 'string') {
                        content = payload.content;
                    } else if (typeof payload.content === 'object') {
                        content = JSON.stringify(payload.content, null, 2);
                    }
                    
                    modal.innerHTML = `
                        <div class="chunk-modal-header">${chunkType} - ${payload.keyword || 'Text Metadata'}</div>
                        <div class="chunk-modal-content">
                            <div class="chunk-modal-section">
                                <div class="chunk-modal-section-title">Keyword</div>
                                <div class="chunk-modal-text">${escapeHtml(payload.keyword || 'Unknown')}</div>
                            </div>
                            <div class="chunk-modal-section">
                                <div class="chunk-modal-section-title">Content</div>
                                <div class="chunk-modal-text">${escapeHtml(content)}</div>
                            </div>
                        </div>
                    `;
                } else {
                    // Fallback: try to fetch and parse
                    fetchChunkBytes(chunk.offset + 8, Math.min(chunk.size, 1024)).then(bytes => {
                        if (bytes) {
                            const text = new TextDecoder('utf-8', {fatal: false}).decode(bytes);
                            const nullIndex = text.indexOf('\0');
                            if (nullIndex > 0) {
                                const keyword = text.substring(0, nullIndex);
                                const value = text.substring(nullIndex + 1);
                                modal.innerHTML = `
                                    <div class="chunk-modal-header">${chunkType} - ${keyword}</div>
                                    <div class="chunk-modal-content">
                                        <div class="chunk-modal-section">
                                            <div class="chunk-modal-section-title">Keyword</div>
                                            <div class="chunk-modal-text">${escapeHtml(keyword)}</div>
                                        </div>
                                        <div class="chunk-modal-section">
                                            <div class="chunk-modal-section-title">Value</div>
                                            <div class="chunk-modal-text">${escapeHtml(value)}</div>
                                        </div>
                                    </div>
                                `;
                            } else {
                                modal.innerHTML = `<div class="chunk-modal-header">${chunkType}</div><div class="chunk-modal-content"><div class="chunk-modal-text">${escapeHtml(text)}</div></div>`;
                            }
                        }
                    }).catch(err => {
                        modal.innerHTML = `<div class="chunk-modal-header">${chunkType}</div><div class="chunk-modal-content">Error loading content: ${err.message}</div>`;
                    });
                }
            } else if (chunkType === 'IDAT') {
                // Show hex dump of first 64 bytes
                fetchChunkBytes(chunk.offset + 8, 64).then(bytes => {
                    if (bytes) {
                        const hexDump = formatHexDump(bytes, chunk.offset + 8);
                        modal.innerHTML = `
                            <div class="chunk-modal-header">IDAT - Image Data (Pixel)</div>
                            <div class="chunk-modal-content">
                                <div class="chunk-modal-section">
                                    <div class="chunk-modal-section-title">First 64 bytes (of ${chunk.size.toLocaleString()})</div>
                                    <div class="chunk-modal-hex">${hexDump}</div>
                                </div>
                                <div class="chunk-modal-section">
                                    <div style="color: #8b949e; font-size: 10px; margin-top: 8px;">Note: This is compressed PNG image data. The actual pixel data requires decompression.</div>
                                </div>
                            </div>
                        `;
                    } else {
                        modal.innerHTML = `<div class="chunk-modal-header">IDAT</div><div class="chunk-modal-content">Could not load chunk data</div>`;
                    }
                }).catch(err => {
                    modal.innerHTML = `<div class="chunk-modal-header">IDAT</div><div class="chunk-modal-content">Error loading data: ${err.message}</div>`;
                });
            } else {
                // Generic chunk - show hex dump
                fetchChunkBytes(chunk.offset + 8, Math.min(chunk.size, 128)).then(bytes => {
                    if (bytes) {
                        const hexDump = formatHexDump(bytes, chunk.offset + 8);
                        modal.innerHTML = `
                            <div class="chunk-modal-header">${chunkType}</div>
                            <div class="chunk-modal-content">
                                <div class="chunk-modal-section">
                                    <div class="chunk-modal-section-title">First ${bytes.length} bytes (of ${chunk.size.toLocaleString()})</div>
                                    <div class="chunk-modal-hex">${hexDump}</div>
                                </div>
                            </div>
                        `;
                    } else {
                        modal.innerHTML = `<div class="chunk-modal-header">${chunkType}</div><div class="chunk-modal-content">Could not load chunk data</div>`;
                    }
                }).catch(err => {
                    modal.innerHTML = `<div class="chunk-modal-header">${chunkType}</div><div class="chunk-modal-content">Error loading data: ${err.message}</div>`;
                });
            }
        }
        
        function fetchChunkBytes(offset, length) {
            // Get file path from stored data
            const filePath = window.currentFilePath;
            if (!filePath) {
                return Promise.reject(new Error('File path not available'));
            }
            
            return fetch('/chunk-content', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    file_path: filePath,
                    offset: offset,
                    length: length
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                // Decode base64
                const binaryString = atob(data.data);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }
                return bytes;
            });
        }
        
        function formatHexDump(bytes, startOffset) {
            let output = '';
            const bytesPerLine = 16;
            for (let i = 0; i < bytes.length; i += bytesPerLine) {
                const offset = startOffset + i;
                const lineBytes = bytes.slice(i, i + bytesPerLine);
                const hex = Array.from(lineBytes).map(b => {
                    const hex = b.toString(16).padStart(2, '0');
                    return hex;
                }).join(' ');
                const ascii = Array.from(lineBytes).map(b => {
                    return (b >= 32 && b < 127) ? String.fromCharCode(b) : '.';
                }).join('');
                output += `<div class="chunk-modal-hex-line"><span class="chunk-modal-hex-offset">${offset.toString(16).padStart(8, '0')}:</span><span class="chunk-modal-hex-bytes">${hex.padEnd(48)}</span><span class="chunk-modal-hex-ascii">${ascii}</span></div>`;
            }
            return output;
        }
        
        function addLine(content, className = '') {
            const line = document.createElement('div');
            line.className = 'terminal-line ' + className;
            line.innerHTML = content;
            terminal.appendChild(line);
            terminal.scrollTop = terminal.scrollHeight;
        }
        
        function addCommand(cmd) {
            addLine(`<span class="prompt">$</span> <span class="command">bareblocks ${cmd}</span>`, 'command');
        }
        
        function addOutput(content, type = 'output') {
            // If content already has HTML tags, don't wrap it again
            if (content.includes('<span')) {
                addLine(content, type);
            } else {
                addLine(`<span class="${type}">${content}</span>`, type);
            }
        }
        
        function formatValue(value, depth = 0) {
            if (depth > 10) return '[Max depth reached]'; // Increased from 3 to 10
            if (value === null) return '[null]';
            if (value === undefined) return '[undefined]';
            if (typeof value === 'object') {
                if (Array.isArray(value)) {
                    if (value.length === 0) return '[]';
                    if (value.length > 5) {
                        return `[Array: ${value.length} items] ${JSON.stringify(value.slice(0, 3), null, 0)}...`;
                    }
                    return `[${value.map(v => formatValue(v, depth + 1)).join(', ')}]`;
                }
                const keys = Object.keys(value);
                if (keys.length === 0) return '{}';
                if (keys.length > 10) {
                    return `{${keys.slice(0, 5).map(k => `${k}: ${formatValue(value[k], depth + 1)}`).join(', ')}... (+${keys.length - 5} more)}`;
                }
                return `{${keys.map(k => `${k}: ${formatValue(value[k], depth + 1)}`).join(', ')}}`;
            }
            // Don't truncate strings - preserve full text for display
            return String(value);
        }
        
        function highlightBracketedText(text) {
            // Highlight text in brackets like [text], __text__, (text), etc.
            // Also handle wildcards like __mklinkwildcards/catbreed__
            return escapeHtml(text)
                .replace(/(\[[^\]]+\])/g, '<span style="color: #98C379;">$1</span>')
                .replace(/(\([^)]+\))/g, '<span style="color: #98C379;">$1</span>')
                .replace(/(__[^_]+__)/g, '<span style="color: #98C379;">$1</span>')
                .replace(/(\{[^}]+\})/g, '<span style="color: #98C379;">$1</span>');
        }
        
        function createMetadataTableHTML(metadata, sectionType = '') {
            const sectionClass = sectionType ? `table-${sectionType}` : '';
            let html = `<table class="metadata-table ${sectionClass}"><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>`;
            
            // Get accent color for this section type
            const accentColors = {
                'summary': '#9CDCFE',
                'structure': '#C678DD',
                'metadata': '#D19A66',
                'comfyui': '#D19A66',
                'ai': '#56B6C2',
                'anomaly': '#E06C75',
                'payload': '#B294BB'
            };
            const accentColor = accentColors[sectionType] || '#6FC3DF';
            
            // Keys to highlight for each section type (only the value, not the key name)
            const highlightKeys = {
                'summary': ['containerType', 'fileSize (MB)', 'Dimensions'],
                'metadata': ['gps', 'dpi'],
                'comfyui': ['Sampler', 'Steps']
            };
            const keysToHighlight = highlightKeys[sectionType] || [];
            
            function shouldHighlight(key) {
                // Check exact match or case-insensitive match
                // Also check if key ends with the highlight key (for nested keys like "image_properties.dpi")
                return keysToHighlight.some(k => {
                    const keyLower = key.toLowerCase();
                    const kLower = k.toLowerCase();
                    return key === k || keyLower === kLower || keyLower.endsWith('.' + kLower) || keyLower.endsWith('_' + kLower);
                });
            }
            
            function shortenFieldName(key) {
                // Remove redundant prefixes
                if (key.startsWith('GPS ')) {
                    key = key.substring(4); // Remove "GPS " prefix
                }
                // Remove "Interoperability " prefix - handles "Interoperability InteroperabilityIndex" -> "InteroperabilityIndex"
                // Use regex to match "Interoperability " at the start (case-insensitive, flexible whitespace)
                key = key.replace(/^Interoperability\s+/i, '');
                
                // Shorten specific long field names for better display
                const shortenings = {
                    'Thumbnail JPEGInterchangeFormat': 'Thumbnail JFIF',
                    'Thumbnail JPEGInterchangeFormatLength': 'Thumbnail JFIFLength'
                };
                return shortenings[key] || key;
            }
            
            function formatValueWithHighlight(value, key) {
                const formatted = formatValue(value);
                if (shouldHighlight(key)) {
                    return `<span style="color: ${accentColor};">${formatted}</span>`;
                }
                return formatted;
            }
            
            function addRows(obj, prefix = '', depth = 0) {
                if (depth > 2) return; // Limit nesting depth
                for (const [key, value] of Object.entries(obj)) {
                    const fullKey = prefix ? `${prefix}.${key}` : key;
                    if (value && typeof value === 'object' && !Array.isArray(value)) {
                        // Check if this is GPS data with formatted coordinates
                        if (key === 'gps' && value.formatted) {
                            const gpsCoords = value.formatted;
                            const uniqueId = `gps-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                            const gpsColor = shouldHighlight(key) ? accentColor : '#6FC3DF';
                            html += `<tr><td>${escapeHtml(fullKey)}</td><td><div class="gps-coords"><span class="gps-coords-text" style="color: ${gpsColor};">${escapeHtml(gpsCoords)}</span><span class="copy-icon" onclick="copyGPSCoords('${escapeHtml(gpsCoords)}', this)" id="${uniqueId}" title="Click to copy coordinates"></span></div></td></tr>`;
                            continue;
                        }
                        
                        // Check if this is the exif object - expand by default
                        const isExif = key === 'exif' || key.toLowerCase() === 'exif';
                        const itemCount = Object.keys(value).length;
                        
                        // For EXIF, show expanded by default; for others, show collapsed
                        if (isExif) {
                            // EXIF: show expanded immediately
                            html += `<tr class="expandable" onclick="toggleRow(this)" style="cursor: pointer;"><td>${escapeHtml(fullKey)}</td><td>[Object: ${itemCount} properties] <span class="toggle">-</span></td></tr>`;
                            html += `<tr class="nested" style="display:table-row;"><td colspan="2" style="padding-left:20px; padding-top:0; padding-bottom:0;">`;
                        } else {
                            // Other objects: show collapsed by default
                            html += `<tr class="expandable" onclick="toggleRow(this)" style="cursor: pointer;"><td>${escapeHtml(fullKey)}</td><td>[Object: ${itemCount} properties] <span class="toggle">+</span></td></tr>`;
                            html += `<tr class="nested" style="display:none;"><td colspan="2" style="padding-left:20px; padding-top:0; padding-bottom:0;">`;
                        }
                        
                        // Create nested table for proper structure
                        html += `<table style="width:100%; margin:0; border-collapse:collapse; font-size:10px;">`;
                        for (const [nestedKey, nestedValue] of Object.entries(value)) {
                            // Remove "EXIF " prefix from field names for cleaner display
                            let displayKey = isExif && nestedKey.startsWith('EXIF ') ? nestedKey.substring(5) : nestedKey;
                            // Shorten specific long field names
                            displayKey = shortenFieldName(displayKey);
                            const nestedFullKey = `${fullKey}.${nestedKey}`;
                            
                            // Check if nested value is GPS formatted coordinates
                            if (nestedKey === 'formatted' && typeof nestedValue === 'string' && /^-?\d+\.\d+,\s*-?\d+\.\d+$/.test(nestedValue)) {
                                const uniqueId = `gps-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                                html += `<tr><td>${escapeHtml(displayKey)}</td><td><div class="gps-coords"><span class="gps-coords-text">${escapeHtml(nestedValue)}</span><span class="copy-icon" onclick="copyGPSCoords('${escapeHtml(nestedValue)}', this)" id="${uniqueId}" title="Click to copy coordinates"></span></div></td></tr>`;
                                continue;
                            }
                            
                            if (nestedValue && typeof nestedValue === 'object' && !Array.isArray(nestedValue) && depth < 1) {
                                const nestedItemCount = Object.keys(nestedValue).length;
                                html += `<tr class="expandable" onclick="toggleRow(this)" style="cursor: pointer;"><td>${escapeHtml(displayKey)}</td><td>[Object: ${nestedItemCount} properties] <span class="toggle">+</span></td></tr>`;
                                html += `<tr class="nested" style="display:none;"><td colspan="2" style="padding-left:15px;">`;
                                html += `<table style="width:100%; margin:0; border-collapse:collapse; font-size:10px;">`;
                                for (const [deepKey, deepValue] of Object.entries(nestedValue)) {
                                    // Remove "EXIF " prefix from deep nested keys too
                                    let displayDeepKey = isExif && deepKey.startsWith('EXIF ') ? deepKey.substring(5) : deepKey;
                                    // Shorten specific long field names
                                    displayDeepKey = shortenFieldName(displayDeepKey);
                                    // Check for GPS formatted coordinates in deep nesting
                                    if (deepKey === 'formatted' && typeof deepValue === 'string' && /^-?\d+\.\d+,\s*-?\d+\.\d+$/.test(deepValue)) {
                                        const uniqueId = `gps-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                                        html += `<tr><td>${escapeHtml(displayDeepKey)}</td><td><div class="gps-coords"><span class="gps-coords-text">${escapeHtml(deepValue)}</span><span class="copy-icon" onclick="copyGPSCoords('${escapeHtml(deepValue)}', this)" id="${uniqueId}" title="Click to copy coordinates"></span></div></td></tr>`;
                                    } else {
                                        const formattedDeep = formatValueWithHighlight(deepValue, deepKey);
                                        html += `<tr><td>${escapeHtml(displayDeepKey)}</td><td>${formattedDeep}</td></tr>`;
                                    }
                                }
                                html += `</table></td></tr>`;
                            } else {
                                const formattedNested = formatValueWithHighlight(nestedValue, nestedKey);
                                html += `<tr><td>${escapeHtml(displayKey)}</td><td>${formattedNested}</td></tr>`;
                            }
                        }
                        html += `</table></td></tr>`;
                    } else {
                        // Shorten field name if needed
                        const displayKey = shortenFieldName(fullKey);
                        // Check if this is a GPS formatted coordinate string
                        if (typeof value === 'string' && /^-?\d+\.\d+,\s*-?\d+\.\d+$/.test(value) && (key.toLowerCase().includes('gps') || key.toLowerCase().includes('coordinate') || key.toLowerCase() === 'formatted')) {
                            const uniqueId = `gps-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                            const gpsColor = shouldHighlight(key) ? accentColor : '#6FC3DF';
                            html += `<tr><td>${escapeHtml(displayKey)}</td><td><div class="gps-coords"><span class="gps-coords-text" style="color: ${gpsColor};">${escapeHtml(value)}</span><span class="copy-icon" onclick="copyGPSCoords('${escapeHtml(value)}', this)" id="${uniqueId}" title="Click to copy coordinates"></span></div></td></tr>`;
                        } else {
                            const formattedValue = formatValueWithHighlight(value, key);
                            html += `<tr><td>${escapeHtml(displayKey)}</td><td>${formattedValue}</td></tr>`;
                        }
                    }
                }
            }
            
            addRows(metadata);
            html += '</tbody></table>';
            return html;
        }
        
        function addMetadataTable(metadata, sectionType = '') {
            const tableHTML = createMetadataTableHTML(metadata, sectionType);
            addLine(tableHTML);
        }
        
        function toggleRow(row) {
            // Find the next sibling row with class 'nested'
            let nested = row.nextElementSibling;
            
            // If not found, try to find it in the parent table
            if (!nested || !nested.classList.contains('nested')) {
                const parentTable = row.closest('table');
                if (parentTable) {
                    const allRows = parentTable.querySelectorAll('tr');
                    for (let i = 0; i < allRows.length; i++) {
                        if (allRows[i] === row && i + 1 < allRows.length) {
                            nested = allRows[i + 1];
                            if (nested.classList.contains('nested')) {
                                break;
                            }
                        }
                    }
                }
            }
            
            if (nested && nested.classList.contains('nested')) {
                const isHidden = nested.style.display === 'none' || !nested.style.display || window.getComputedStyle(nested).display === 'none';
                nested.style.display = isHidden ? 'table-row' : 'none';
                const toggle = row.querySelector('.toggle');
                if (toggle) toggle.textContent = isHidden ? '-' : '+';
            } else {
                console.log('Could not find nested row for:', row);
            }
        }
        
        // Make toggleRow globally accessible
        window.toggleRow = toggleRow;
        
        function copyGPSCoords(coords, iconElement) {
            // Copy coordinates to clipboard
            navigator.clipboard.writeText(coords).then(() => {
                // Visual feedback: change icon to checkmark
                iconElement.classList.add('copied');
                setTimeout(() => {
                    iconElement.classList.remove('copied');
                }, 2000);
            }).catch(err => {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = coords;
                textArea.style.position = 'fixed';
                textArea.style.opacity = '0';
                document.body.appendChild(textArea);
                textArea.select();
                try {
                    document.execCommand('copy');
                    iconElement.classList.add('copied');
                    setTimeout(() => {
                        iconElement.classList.remove('copied');
                    }, 2000);
                } catch (err) {
                    console.error('Failed to copy:', err);
                }
                document.body.removeChild(textArea);
            });
        }
        
        // Make copyGPSCoords globally accessible
        window.copyGPSCoords = copyGPSCoords;
        
        function copyGPSFromClick(coords, elementId) {
            const icon = document.getElementById(elementId);
            if (icon) {
                copyGPSCoords(coords, icon);
            } else {
                // Create a temporary icon element for feedback
                const tempIcon = document.createElement('span');
                tempIcon.className = 'copy-icon';
                copyGPSCoords(coords, tempIcon);
            }
        }
        
        window.copyGPSFromClick = copyGPSFromClick;
        
        function exportJSON(event) {
            if (!window.currentMetadata) {
                addOutput('No metadata available to export', 'error');
                return;
            }
            
            try {
                const jsonStr = JSON.stringify(window.currentMetadata, null, 2);
                const blob = new Blob([jsonStr], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                
                // Generate filename: <fileName>_<containerType>_metadata.json
                const summary = window.currentMetadata.summary || {};
                const fileName = summary.fileName || 'file';
                const containerType = summary.containerType || 'unknown';
                // Remove file extension from fileName if present
                const baseFileName = fileName.replace(/\.[^/.]+$/, '');
                // Sanitize filename (remove invalid characters)
                const sanitizedFileName = baseFileName.replace(/[^a-zA-Z0-9_-]/g, '_');
                const sanitizedContainerType = containerType.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase();
                const downloadName = `${sanitizedFileName}_${sanitizedContainerType}_metadata.json`;
                
                a.download = downloadName;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                // Visual feedback
                const icon = event ? event.target : null;
                if (icon) {
                    icon.classList.add('copied');
                    setTimeout(() => {
                        icon.classList.remove('copied');
                    }, 2000);
                }
            } catch (err) {
                addOutput(`Error exporting JSON: ${err.message}`, 'error');
            }
        }
        
        window.exportJSON = exportJSON;
        
        function addJsonOutput(data) {
            const jsonStr = JSON.stringify(data, null, 2);
            const formatted = jsonStr
                .replace(/(".*?"):/g, '<span class="json-key">$1</span>:')
                .replace(/:\s*(".*?")/g, ': <span class="json-string">$1</span>')
                .replace(/:\s*(\d+\.?\d*)/g, ': <span class="json-number">$1</span>')
                .replace(/:\s*(true|false)/g, ': <span class="json-boolean">$1</span>');
            
            addLine(`<div class="json-output">${formatted}</div>`);
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function determineProvenance(metadata) {
            const exif = metadata.metadata?.exif || {};
            const aiMeta = metadata.aiMetadata?.aiMetadata || {};
            const payloads = metadata.payloads?.payloads || [];
            const exifKeys = Object.keys(exif);
            
            const hasKey = (substr) => exifKeys.some(k => k.toLowerCase().includes(substr.toLowerCase()));
            
            // Check for camera indicators
            const hasCamera = hasKey('make') || hasKey('model') || hasKey('camera') || 
                             exif['Image Make'] || exif['Image Model'] || exif['EXIF LensModel'];
            
            // Check for AI indicators
            const hasAI = aiMeta.tool === 'ComfyUI' || 
                         payloads.some(p => {
                             const content = typeof p.content === 'string' ? p.content.toLowerCase() : 
                                           typeof p.content === 'object' ? JSON.stringify(p.content).toLowerCase() : '';
                             return p.classification === 'json' && (content.includes('comfy') || content.includes('workflow') || content.includes('nodes'));
                         });
            
            if (hasCamera && !hasAI) {
                return 'camera';
            } else if (hasAI && !hasCamera) {
                return 'ai';
            } else if (hasCamera && hasAI) {
                // Both present - check which is more prominent
                return 'unclear';
            } else {
                return 'unclear';
            }
        }
        
        function addProvenanceSummary(metadata) {
            const provenance = determineProvenance(metadata);
            const exif = metadata.metadata?.exif || {};
            const gps = metadata.metadata?.gps || {};
            const aiMeta = metadata.aiMetadata?.aiMetadata || {};
            const payloads = metadata.payloads?.payloads || [];
            const summary = metadata.summary || {};
            
            let summaryHtml = '<div class="provenance-summary">';
            
            if (provenance === 'camera') {
                summaryHtml += '<div class="provenance-summary-title">This image has metadata indicating it was taken by a camera.</div>';
                
                // Extract camera info
                const make = String(exif['Image Make'] || '').trim();
                const model = String(exif['Image Model'] || '').trim();
                const lensModel = String(exif['EXIF LensModel'] || '').trim();
                const focalLength = exif['EXIF FocalLength'];
                const fNumber = exif['EXIF FNumber'];
                
                // Calculate focal length and f-number
                let focalStr = '';
                let fstopStr = '';
                if (focalLength && fNumber) {
                    const focal = typeof focalLength === 'object' && focalLength.values ? 
                                 (focalLength.values[0].num / focalLength.values[0].den).toFixed(2) :
                                 parseFloat(focalLength).toFixed(2);
                    const fstop = typeof fNumber === 'object' && fNumber.values ? 
                                 (fNumber.values[0].num / fNumber.values[0].den).toFixed(1) :
                                 parseFloat(fNumber).toFixed(1);
                    focalStr = `${focal}mm`;
                    fstopStr = `f/${fstop}`;
                }
                
                let cameraStr = '';
                
                // Strategy: If lensModel contains model name and focal info, use lensModel as base
                // Otherwise, build from components
                if (lensModel) {
                    const lensLower = lensModel.toLowerCase();
                    const modelInLens = model && lensLower.includes(model.toLowerCase());
                    const hasFocalInLens = focalStr && lensLower.includes(focalStr.toLowerCase());
                    const hasFstopInLens = fstopStr && lensLower.includes(fstopStr.toLowerCase());
                    
                    // If lensModel contains model + focal info, it's the most complete
                    if (modelInLens && hasFocalInLens && hasFstopInLens) {
                        // Use lensModel, but prepend make if it's not already there
                        if (make && !lensLower.includes(make.toLowerCase())) {
                            cameraStr = `${make} ${lensModel}`;
                        } else {
                            cameraStr = lensModel;
                        }
                    } else {
                        // Build from components, avoiding duplicates
                        // Start with make + model (if model doesn't already contain make)
                        if (make && model) {
                            if (model.toLowerCase().includes(make.toLowerCase())) {
                                cameraStr = model;
                            } else {
                                cameraStr = `${make} ${model}`;
                            }
                        } else if (model) {
                            cameraStr = model;
                        } else if (make) {
                            cameraStr = make;
                        }
                        
                        // Add lensModel if it's not already in the string
                        if (lensModel && !cameraStr.toLowerCase().includes(lensLower)) {
                            // Check if lensModel contains model name - if so, extract unique part
                            if (modelInLens && model) {
                                // Remove model name from lensModel using simple string replacement
                                const modelLower = model.toLowerCase();
                                const lensLower = lensModel.toLowerCase();
                                const modelIndex = lensLower.indexOf(modelLower);
                                if (modelIndex !== -1) {
                                    // Remove the model name from lensModel
                                    let uniqueLens = lensModel.substring(0, modelIndex) + lensModel.substring(modelIndex + model.length);
                                    uniqueLens = uniqueLens.trim();
                                    // Clean up any double spaces
                                    uniqueLens = uniqueLens.replace(/\s+/g, ' ').trim();
                                    if (uniqueLens) {
                                        cameraStr += ` ${uniqueLens}`;
                                    }
                                } else {
                                    cameraStr += ` ${lensModel}`;
                                }
                            } else {
                                cameraStr += ` ${lensModel}`;
                            }
                        }
                        
                        // Add focal/f-number if not already in string
                        if (focalStr && fstopStr) {
                            const focalPattern = `${focalStr} ${fstopStr}`;
                            if (!cameraStr.toLowerCase().includes(focalPattern.toLowerCase())) {
                                cameraStr += ` ${focalPattern}`;
                            }
                        }
                    }
                } else {
                    // No lensModel, build from make + model + focal/f-number
                    if (make && model) {
                        if (model.toLowerCase().includes(make.toLowerCase())) {
                            cameraStr = model;
                        } else {
                            cameraStr = `${make} ${model}`;
                        }
                    } else if (model) {
                        cameraStr = model;
                    } else if (make) {
                        cameraStr = make;
                    }
                    
                    if (focalStr && fstopStr) {
                        const focalPattern = `${focalStr} ${fstopStr}`;
                        if (cameraStr) {
                            cameraStr += ` ${focalPattern}`;
                        } else {
                            cameraStr = focalPattern;
                        }
                    }
                }
                
                if (cameraStr) {
                    summaryHtml += `<div class="provenance-line"><span class="provenance-label">Camera:</span><span class="provenance-value">${escapeHtml(cameraStr)}</span></div>`;
                }
                
            } else if (provenance === 'ai') {
                summaryHtml += '<div class="provenance-summary-title">This image has AI metadata.</div>';
                
                // Extract AI model info - same logic as ComfyUI section
                let modelName = '';
                for (const payload of payloads) {
                    if (payload.classification === 'json' && payload.content) {
                        let content = payload.content;
                        if (typeof content === 'string') {
                            try {
                                content = JSON.parse(content);
                            } catch(e) {
                                continue;
                            }
                        }
                        if (content && typeof content === 'object') {
                            // Check if it's a workflow structure
                            const nodes = content.nodes || content;
                            if (nodes && typeof nodes === 'object') {
                                for (const [nodeId, node] of Object.entries(nodes)) {
                                    if (node && typeof node === 'object' && node.class_type) {
                                        // Extract from UNETLoader or CheckpointLoaderSimple
                                        if (node.class_type === 'UNETLoader' || node.class_type === 'CheckpointLoaderSimple') {
                                            if (node.inputs) {
                                                if (node.inputs.unet_name) {
                                                    modelName = String(node.inputs.unet_name);
                                                    break;
                                                } else if (node.inputs.ckpt_name) {
                                                    modelName = String(node.inputs.ckpt_name);
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                            if (modelName) break;
                        }
                    }
                }
                
                if (modelName) {
                    summaryHtml += `<div class="provenance-line"><span class="provenance-label">Model:</span><span class="provenance-value">${escapeHtml(modelName)}</span></div>`;
                }
                
                // Add date created for AI metadata
                if (summary.dateCreated) {
                    const dateCreated = new Date(summary.dateCreated);
                    summaryHtml += `<div class="provenance-line"><span class="provenance-label">Date Created:</span><span class="provenance-value">${escapeHtml(dateCreated.toLocaleString())}</span></div>`;
                }
            } else {
                summaryHtml += '<div class="provenance-summary-title">Not enough metadata to indicate provenance.</div>';
            }
            
            // Add GPS if available
            const gpsFormatted = gps.formatted || (gps.latitude !== undefined && gps.longitude !== undefined ? 
                              `${gps.latitude.toFixed(6)}, ${gps.longitude.toFixed(6)}` : null);
            if (gpsFormatted) {
                const uniqueId = `gps-provenance-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                summaryHtml += `<div class="provenance-line"><span class="provenance-label">GPS:</span><span class="provenance-value"><div class="provenance-gps"><span>${escapeHtml(gpsFormatted)}</span><span class="copy-icon" onclick="copyGPSCoords('${escapeHtml(gpsFormatted)}', this)" id="${uniqueId}" title="Click to copy coordinates"></span></div></span></div>`;
            }
            
            // Add date (for camera metadata)
            if (provenance === 'camera') {
                const dateTime = exif['EXIF DateTimeOriginal'] || exif['Image DateTime'] || exif['EXIF DateTime'];
                if (dateTime) {
                    summaryHtml += `<div class="provenance-line"><span class="provenance-label">Date:</span><span class="provenance-value">${escapeHtml(String(dateTime))}</span></div>`;
                }
            }
            
            summaryHtml += '</div>';
            addLine(summaryHtml);
        }
        
        // Function to scroll to section and highlight it
        function scrollToSection(sectionId) {
            const section = document.getElementById(sectionId);
            if (section) {
                // Remove any existing highlights
                document.querySelectorAll('.section-highlight').forEach(el => {
                    el.classList.remove('section-highlight');
                });
                
                // Scroll to section
                section.scrollIntoView({ behavior: 'smooth', block: 'start' });
                
                // Add highlight
                section.classList.add('section-highlight');
                
                // Remove highlight after animation
                setTimeout(() => {
                    section.classList.remove('section-highlight');
                }, 2000);
            }
        }
        window.scrollToSection = scrollToSection;
        
        // Map check names to section IDs
        function getSectionIdForCheck(checkName) {
            const mapping = {
                'Camera data': 'section-metadata',
                'Geo data': 'section-metadata',
                'GPS': 'section-metadata',
                'EXIF': 'section-metadata',
                'IPTC': 'section-metadata',
                'XMP': 'section-metadata',
                'ICC profiles': 'section-metadata',
                'TIFF tags': 'section-metadata',
                'JPEG APP markers': 'section-structure',
                'PNG text chunks': 'section-structure',
                'IPTC-IIM': 'section-metadata',
                'Photoshop IRB': 'section-metadata',
                'Camera maker notes': 'section-metadata',
                'Thumbnail data': 'section-metadata',
                'IFD (Image File Directory)': 'section-metadata',
                'MakerNote': 'section-metadata',
                'DNG raw metadata': 'section-metadata',
                'Rights management': 'section-metadata',
                'Descriptive keywords': 'section-metadata',
                'Administrative data': 'section-metadata',
                'Technical specs (ISO, shutter, aperture)': 'section-metadata',
                'Geolocation blocks': 'section-metadata',
                'PGP signature': 'section-ai',
                'ComfyUI workflow JSON': 'section-comfyui',
                'Prompt text files (.txt)': 'section-payload',
                'LoRA config JSON': 'section-payload',
                'Model training metadata YAML': 'section-payload',
                'Checkpoint info JSON': 'section-payload',
                'PNG tEXt chunks': 'section-structure',
                'JSON sidecar files': 'section-payload',
                'YAML prompt templates': 'section-payload',
                'ControlNet params JSON': 'section-payload',
                'A1111-style .json prompts': 'section-payload',
                'Metadata JSON embeds': 'section-payload',
                'Custom node configs YAML': 'section-payload',
                'Batch generation logs TXT': 'section-payload',
                'Upscale settings JSON': 'section-payload',
                'Seed/history JSON': 'section-payload'
            };
            return mapping[checkName] || null;
        }
        
        function addDataRecap(metadata) {
            const checks = [];
            
            // Standard metadata formats
            const exif = metadata.metadata?.exif || {};
            const structure = metadata.structure || {};
            const payloads = metadata.payloads?.payloads || [];
            const aiMeta = metadata.aiMetadata?.aiMetadata || {};
            const exifKeys = Object.keys(exif);
            const gps = metadata.metadata?.gps || {};
            
            // Helper to check if any key contains substring
            const hasKey = (substr) => exifKeys.some(k => k.toLowerCase().includes(substr.toLowerCase()));
            
            // Get GPS formatted string
            const gpsFormatted = gps.formatted || (gps.latitude !== undefined && gps.longitude !== undefined ? 
                              `${gps.latitude.toFixed(6)}, ${gps.longitude.toFixed(6)}` : null);
            const hasGPS = metadata.metadata?.gps !== undefined || hasKey('gps') || hasKey('latitude') || hasKey('longitude');
            
            // Standard metadata checks
            checks.push({name: 'Camera data', found: hasKey('make') || hasKey('model') || hasKey('camera')});
            
            // Make Geo data clickable if GPS is available
            if (hasGPS && gpsFormatted) {
                const uniqueId = `gps-recap-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                checks.push({
                    name: 'Geo data', 
                    found: true, 
                    clickable: true, 
                    gpsCoords: gpsFormatted,
                    uniqueId: uniqueId
                });
            } else {
                checks.push({name: 'Geo data', found: hasGPS});
            }
            checks.push({name: 'EXIF', found: exifKeys.length > 0});
            // Check if IPTC has actual content
            const iptcData = metadata.metadata?.iptc;
            const hasIPTCContent = iptcData && typeof iptcData === 'object' && Object.keys(iptcData).length > 0;
            checks.push({name: 'IPTC', found: hasIPTCContent || hasKey('iptc')});
            // Check if XMP has actual content (not just empty object)
            const xmpData = metadata.metadata?.xmp;
            const hasXMPContent = xmpData && typeof xmpData === 'object' && Object.keys(xmpData).length > 0;
            checks.push({name: 'XMP', found: hasXMPContent || (hasKey('xmp') && exifKeys.some(k => k.toLowerCase().includes('xmp')))});
            checks.push({name: 'ICC profiles', found: metadata.metadata?.image_properties?.has_color_profile === true});
            checks.push({name: 'GPS', found: metadata.metadata?.gps !== undefined || hasKey('gps')});
            checks.push({name: 'TIFF tags', found: hasKey('tiff')});
            checks.push({name: 'JPEG APP markers', found: structure.segments !== undefined && structure.segments.length > 0});
            checks.push({name: 'PNG text chunks', found: structure.chunks?.some(c => ['tEXt', 'zTXt', 'iTXt'].includes(c.type)) || false});
            checks.push({name: 'IPTC-IIM', found: hasKey('iptc') || metadata.metadata?.iptc !== undefined});
            checks.push({name: 'Photoshop IRB', found: hasKey('photoshop') || hasKey('irb')});
            checks.push({name: 'Camera maker notes', found: hasKey('makernote') || hasKey('maker note')});
            checks.push({name: 'Thumbnail data', found: hasKey('thumbnail') || exif['JPEGThumbnail'] !== undefined || exif['TIFFThumbnail'] !== undefined});
            checks.push({name: 'IFD (Image File Directory)', found: hasKey('ifd')});
            checks.push({name: 'MakerNote', found: hasKey('makernote')});
            checks.push({name: 'DNG raw metadata', found: hasKey('dng')});
            checks.push({name: 'Rights management', found: hasKey('copyright') || hasKey('rights')});
            checks.push({name: 'Descriptive keywords', found: hasKey('keyword') || hasKey('subject')});
            checks.push({name: 'Administrative data', found: hasKey('author') || hasKey('creator') || hasKey('artist')});
            checks.push({name: 'Technical specs (ISO, shutter, aperture)', found: hasKey('iso') || hasKey('fnumber') || hasKey('exposure') || hasKey('shutter') || hasKey('aperture')});
            checks.push({name: 'Geolocation blocks', found: metadata.metadata?.gps !== undefined});
            
            // Check for PGP signatures
            const hasPGP = aiMeta.pgpSignatureDetected || payloads.some(p => p.hasPGP === true);
            checks.push({name: 'PGP signature', found: hasPGP});
            
            // AI/Workflow specific - check payloads content
            const payloadContent = (p) => {
                if (!p || !p.content) return '';
                if (typeof p.content === 'string') return p.content.toLowerCase();
                if (typeof p.content === 'object') return JSON.stringify(p.content).toLowerCase();
                return '';
            };
            
            checks.push({name: 'ComfyUI workflow JSON', found: aiMeta.tool === 'ComfyUI' || payloads.some(p => {
                const content = payloadContent(p);
                return p.classification === 'json' && (content.includes('comfy') || content.includes('workflow') || content.includes('nodes'));
            })});
            checks.push({name: 'Prompt text files (.txt)', found: payloads.some(p => p.classification === 'text' && payloadContent(p).includes('prompt'))});
            checks.push({name: 'LoRA config JSON', found: payloads.some(p => {
                const content = payloadContent(p);
                return p.classification === 'json' && (content.includes('lora') || content.includes('loras'));
            })});
            checks.push({name: 'Model training metadata YAML', found: payloads.some(p => {
                const content = payloadContent(p);
                return p.classification === 'yaml' || content.includes('model') || content.includes('training');
            })});
            checks.push({name: 'Checkpoint info JSON', found: payloads.some(p => {
                const content = payloadContent(p);
                return p.classification === 'json' && (content.includes('checkpoint') || content.includes('model_name') || content.includes('model_name'));
            })});
            checks.push({name: 'PNG tEXt chunks', found: structure.chunks?.some(c => c.type === 'tEXt') || false});
            checks.push({name: 'JSON sidecar files', found: payloads.some(p => p.classification === 'json')});
            checks.push({name: 'YAML prompt templates', found: payloads.some(p => {
                const content = payloadContent(p);
                return p.classification === 'yaml' || (p.classification === 'text' && content.includes('yaml'));
            })});
            checks.push({name: 'ControlNet params JSON', found: payloads.some(p => {
                const content = payloadContent(p);
                return p.classification === 'json' && (content.includes('controlnet') || content.includes('control_net'));
            })});
            checks.push({name: 'A1111-style .json prompts', found: payloads.some(p => {
                const content = payloadContent(p);
                return p.classification === 'json' && (content.includes('prompt') || content.includes('negative_prompt'));
            })});
            checks.push({name: 'Metadata JSON embeds', found: payloads.some(p => p.classification === 'json')});
            checks.push({name: 'Custom node configs YAML', found: payloads.some(p => {
                const content = payloadContent(p);
                return p.classification === 'yaml' || (p.classification === 'json' && content.includes('nodes'));
            })});
            checks.push({name: 'Batch generation logs TXT', found: payloads.some(p => {
                const content = payloadContent(p);
                return p.classification === 'text' && (content.includes('batch') || content.includes('generation'));
            })});
            checks.push({name: 'Upscale settings JSON', found: payloads.some(p => {
                const content = payloadContent(p);
                return p.classification === 'json' && (content.includes('upscale') || content.includes('scale'));
            })});
            checks.push({name: 'Seed/history JSON', found: payloads.some(p => {
                const content = payloadContent(p);
                return p.classification === 'json' && (content.includes('seed') || content.includes('history'));
            })});
            
            // Helper function to check if section will have content and get the correct section ID
            function getSectionInfo(checkName, metadata) {
                if (checkName === 'LoRA config JSON') {
                    // Check if ComfyUI section exists (which would show LoRA)
                    const hasComfyUI = metadata.aiMetadata?.aiMetadata?.tool === 'ComfyUI' || 
                                     metadata.payloads?.payloads?.some(p => {
                                         const content = p.content;
                                         if (typeof content === 'object') {
                                             return content.nodes || content.workflow;
                                         }
                                         if (typeof content === 'string') {
                                             try {
                                                 const parsed = JSON.parse(content);
                                                 return parsed.nodes || parsed.workflow;
                                             } catch(e) {
                                                 return false;
                                             }
                                         }
                                         return false;
                                     });
                    // If ComfyUI section exists, LoRA will be shown there
                    if (hasComfyUI) {
                        return { hasContent: true, sectionId: 'section-comfyui' };
                    }
                    // Otherwise check if payloads section will show it
                    const hasInPayloads = metadata.payloads?.payloads?.some(p => {
                        const content = typeof p.content === 'string' ? p.content.toLowerCase() : 
                                       (typeof p.content === 'object' ? JSON.stringify(p.content).toLowerCase() : '');
                        return p.classification === 'json' && (content.includes('lora') || content.includes('loras'));
                    });
                    return { hasContent: hasInPayloads, sectionId: 'section-payload' };
                }
                if (checkName === 'XMP') {
                    const xmpData = metadata.metadata?.xmp;
                    const hasContent = xmpData && typeof xmpData === 'object' && Object.keys(xmpData).length > 0;
                    return { hasContent: hasContent, sectionId: 'section-metadata' };
                }
                if (checkName === 'IPTC') {
                    const iptcData = metadata.metadata?.iptc;
                    const hasContent = iptcData && typeof iptcData === 'object' && Object.keys(iptcData).length > 0;
                    return { hasContent: hasContent, sectionId: 'section-metadata' };
                }
                // For other checks, use default mapping
                const sectionId = getSectionIdForCheck(checkName);
                return { hasContent: true, sectionId: sectionId };
            }
            
            // Format as compact list
            let recapHtml = '<div class="data-recap">';
            checks.forEach(check => {
                if (check.clickable && check.found) {
                    // Make Geo data clickable with copy icon (special case - keep copy functionality)
                    recapHtml += `<span class="recap-item">${escapeHtml(check.name)}: <span class="geo-data-clickable" onclick="copyGPSFromClick('${escapeHtml(check.gpsCoords)}', '${check.uniqueId}')"><span class="found">found</span> <span class="copy-icon" id="${check.uniqueId}" title="Click to copy coordinates"></span></span></span> `;
                } else if (check.found) {
                    // Get section info (content check and correct section ID)
                    const sectionInfo = getSectionInfo(check.name, metadata);
                    if (sectionInfo.hasContent && sectionInfo.sectionId) {
                        recapHtml += `<span class="recap-item">${escapeHtml(check.name)}: <span class="found" onclick="scrollToSection('${sectionInfo.sectionId}')" title="Click to jump to ${escapeHtml(check.name)} section">found</span></span> `;
                    } else {
                        recapHtml += `<span class="recap-item">${escapeHtml(check.name)}: <span class="found">found</span></span> `;
                    }
                } else {
                    recapHtml += `<span class="recap-item">${escapeHtml(check.name)}: <span class="not-found">not found</span></span> `;
                }
            });
            recapHtml += '</div>';
            addLine(recapHtml);
        }
        
        // Function to extract wildcards and their resolved values
        function extractWildcards(originalPrompt, resolvedPrompt) {
            if (!originalPrompt || !resolvedPrompt) return [];
            
            const wildcards = [];
            const wildcardPattern = /__([^_]+)__/g;
            const matches = [];
            let match;
            
            // Find all wildcard patterns in original prompt
            while ((match = wildcardPattern.exec(originalPrompt)) !== null) {
                matches.push({
                    pattern: match[0], // e.g., "__dogbreed__"
                    name: match[1],   // e.g., "dogbreed" or "mklinkwildcards/catbreed"
                    index: match.index
                });
            }
            
            if (matches.length === 0) return [];
            
            // For each wildcard, extract the resolved value by comparing original and resolved prompts
            for (let i = 0; i < matches.length; i++) {
                const wildcard = matches[i];
                
                // Get text before this wildcard
                const beforeWildcard = originalPrompt.substring(0, wildcard.index);
                // Get text after this wildcard
                const afterWildcard = originalPrompt.substring(wildcard.index + wildcard.pattern.length);
                
                // Find the "before" text in resolved prompt
                let resolvedBeforeIndex = resolvedPrompt.indexOf(beforeWildcard);
                if (resolvedBeforeIndex === -1 && i > 0) {
                    // If exact match not found, try to find it after previous wildcard resolution
                    const prevWildcard = wildcards[i - 1];
                    if (prevWildcard && prevWildcard.resolved) {
                        const prevResolvedIndex = resolvedPrompt.indexOf(prevWildcard.resolved);
                        if (prevResolvedIndex > -1) {
                            const searchStart = prevResolvedIndex + prevWildcard.resolved.length;
                            resolvedBeforeIndex = resolvedPrompt.indexOf(beforeWildcard.substring(beforeWildcard.length - Math.min(20, beforeWildcard.length)), searchStart);
                        }
                    }
                }
                
                if (resolvedBeforeIndex > -1) {
                    // Find the "after" text in resolved prompt, starting after the "before" text
                    const searchStart = resolvedBeforeIndex + beforeWildcard.length;
                    const resolvedAfterIndex = resolvedPrompt.indexOf(afterWildcard, searchStart);
                    
                    if (resolvedAfterIndex > -1) {
                        // Extract the resolved value (text between "before" and "after")
                        const resolvedValue = resolvedPrompt.substring(searchStart, resolvedAfterIndex).trim();
                        
                        if (resolvedValue && resolvedValue.length > 0 && resolvedValue !== wildcard.pattern) {
                            wildcards.push({
                                name: wildcard.pattern,
                                resolved: resolvedValue
                            });
                        }
                    }
                }
            }
            
            return wildcards;
        }
        
        function addComfyUISection(metadata, targetContainer = null) {
            const payloads = metadata.payloads?.payloads || [];
            const aiMeta = metadata.aiMetadata?.aiMetadata || {};
            
            // Find ComfyUI workflow JSON - check all payloads
            let workflowData = null;
            let promptText = null;
            let negativePrompt = null;
            let allWorkflowData = [];
            let originalPromptWithWildcards = null;
            let resolvedPrompt = null;
            
            // First, try to find the main workflow (usually in "workflow" keyword)
            for (const payload of payloads) {
                if (payload.classification === 'json' && payload.keyword === 'workflow') {
                    let content = payload.content;
                    if (typeof content === 'string') {
                        try {
                            content = JSON.parse(content);
                        } catch(e) {
                            continue;
                        }
                    }
                    if (content && typeof content === 'object') {
                        workflowData = content;
                        break;
                    }
                }
            }
            
            // Also check the "prompt" keyword payload for node data and wildcard detection
            let promptNodes = null;
            for (const payload of payloads) {
                if (payload.classification === 'json' && payload.keyword === 'prompt') {
                    let content = payload.content;
                    if (typeof content === 'string') {
                        // Check if this is a string prompt with wildcards
                        if (content.includes('__') && /__[^_]+__/.test(content)) {
                            originalPromptWithWildcards = content;
                            // If this is the original prompt with wildcards, use it as promptText
                            if (!promptText) {
                                promptText = content;
                            }
                        }
                        try {
                            content = JSON.parse(content);
                        } catch(e) {
                            // If parsing fails, it might be a plain text prompt
                            if (!promptText && content.length > 10) {
                                promptText = content;
                            }
                            continue;
                        }
                    }
                    if (content && typeof content === 'object') {
                        promptNodes = content;
                        if (!workflowData) {
                            workflowData = { nodes: content };
                        } else {
                            workflowData.nodes = content;
                        }
                        break;
                    }
                }
            }
            
            // Also check text payloads for original prompt with wildcards
            if (!originalPromptWithWildcards) {
                for (const payload of payloads) {
                    if (payload.classification === 'text' || (payload.classification === 'json' && typeof payload.content === 'string')) {
                        const content = typeof payload.content === 'string' ? payload.content : String(payload.content || '');
                        if (content.includes('__') && /__[^_]+__/.test(content) && content.length > 20) {
                            originalPromptWithWildcards = content;
                            if (!promptText) {
                                promptText = content;
                            }
                            break;
                        }
                    }
                }
            }
            
            // Look for resolved prompt in workflow payload (string content)
            // The resolved prompt is typically in the workflow keyword payload as a string
            for (const payload of payloads) {
                if (payload.classification === 'json' && payload.keyword === 'workflow') {
                    let content = payload.content;
                    if (typeof content === 'string') {
                        // Check if this looks like a resolved prompt
                        // It should be a string, not contain wildcards, and be similar in structure to original
                        if (originalPromptWithWildcards) {
                            // If we have an original with wildcards, this string is likely the resolved version
                            if (!content.includes('__') && content.length >= originalPromptWithWildcards.length * 0.8) {
                                resolvedPrompt = content;
                                break;
                            }
                        } else {
                            // If no original found yet, check if this is a resolved prompt (no wildcards, contains text)
                            if (!content.includes('__') && content.length > 50 && /^[a-zA-Z0-9\s,\.\-]+$/.test(content.substring(0, 100))) {
                                // This might be a resolved prompt, but we need the original to match it
                                // Store it temporarily
                                resolvedPrompt = content;
                            }
                        }
                    }
                }
            }
            
            // Also check all payloads for resolved prompt if not found yet
            if (!resolvedPrompt && originalPromptWithWildcards) {
                for (const payload of payloads) {
                    if (payload.classification === 'json') {
                        let content = payload.content;
                        if (typeof content === 'string') {
                            // Check if this looks like a resolved prompt
                            if (!content.includes('__') && 
                                content.length > originalPromptWithWildcards.length * 0.8 &&
                                content.length < originalPromptWithWildcards.length * 2) {
                                // Check if it shares some common words with original
                                const originalWords = originalPromptWithWildcards.toLowerCase().split(/\s+/).filter(w => w.length > 3);
                                const contentWords = content.toLowerCase().split(/\s+/).filter(w => w.length > 3);
                                const commonWords = originalWords.filter(w => contentWords.includes(w));
                                if (commonWords.length >= 2) {
                                    resolvedPrompt = content;
                                    break;
                                }
                            }
                        }
                    }
                }
            }
            
            // If no workflow found, check all JSON payloads
            if (!workflowData) {
                for (const payload of payloads) {
                    // Check if payload is marked as ComfyUI or is JSON
                    if (payload.isComfyUI || payload.classification === 'json') {
                        let content = payload.content;
                        
                        // Parse if string
                        if (typeof content === 'string') {
                            try {
                                content = JSON.parse(content);
                            } catch(e) {
                                continue;
                            }
                        }
                        
                        // Check if it's a ComfyUI workflow
                        if (content && typeof content === 'object') {
                            // Check for nodes structure (ComfyUI format)
                            if (content.nodes || (typeof content === 'object' && Object.keys(content).some(k => {
                                const node = content[k];
                                return node && typeof node === 'object' && (node.class_type || node.inputs);
                            }))) {
                                allWorkflowData.push(content);
                                if (!workflowData) {
                                    workflowData = content;
                                }
                            }
                        }
                    }
                }
            }
            
            // If we found workflow data, extract prompts
            if (workflowData) {
                // Extract prompt from various possible locations
                if (workflowData.prompt) {
                    // ComfyUI prompt structure: { "node_id": [prompt_text, ...] }
                    if (typeof workflowData.prompt === 'object') {
                        const prompts = [];
                        for (const [nodeId, promptArray] of Object.entries(workflowData.prompt)) {
                            if (Array.isArray(promptArray) && promptArray.length > 0) {
                                prompts.push(...promptArray.filter(p => typeof p === 'string'));
                            }
                        }
                        promptText = prompts.join(', ');
                    } else {
                        promptText = String(workflowData.prompt);
                    }
                } else if (workflowData.workflow?.prompt) {
                    promptText = typeof workflowData.workflow.prompt === 'string' ? workflowData.workflow.prompt : JSON.stringify(workflowData.workflow.prompt);
                } else if (workflowData.nodes) {
                    // Try to find prompt in nodes - look for CLIPTextEncode nodes
                    const prompts = [];
                    const negativePrompts = [];
                    
                    // Extract from nodes - handle both object with nodes property and direct nodes object
                    const nodesToCheck = workflowData.nodes || workflowData;
                    
                    for (const [nodeId, node] of Object.entries(nodesToCheck)) {
                        if (!node || typeof node !== 'object') continue;
                        
                        // Check if this node has text directly in inputs.text (string, not array reference)
                        if (node.inputs && typeof node.inputs === 'object') {
                            // Check inputs.text - this is where the actual prompt text is stored
                            if (node.inputs.text !== undefined && node.inputs.text !== null) {
                                const textValue = node.inputs.text;
                                
                                // Only extract if it's a string (not an array reference like ["29", 1])
                                if (typeof textValue === 'string' && textValue.trim().length > 5) {
                                    const text = textValue.trim();
                                    const lowerText = text.toLowerCase();
                                    
                                    // Check if it's likely a negative prompt (shorter or contains negative keywords)
                                    if (lowerText.includes('negative') || (text.length < 100 && (lowerText.includes('bad') || lowerText.includes('worst') || lowerText.includes('nsfw')))) {
                                        if (!negativePrompts.includes(text)) {
                                            negativePrompts.push(text);
                                        }
                                    } else {
                                        // This is a positive prompt - collect all of them, we'll sort by length later
                                        if (!prompts.includes(text)) {
                                            prompts.push(text);
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                    // Sort prompts by length (longest first) to prioritize main prompts
                    prompts.sort((a, b) => b.length - a.length);
                    negativePrompts.sort((a, b) => b.length - a.length);
                    
                    if (prompts.length > 0) {
                        // Use the longest prompt (usually the main one) - FULL TEXT, NO TRUNCATION
                        promptText = prompts[0];
                    }
                    if (negativePrompts.length > 0) {
                        negativePrompt = negativePrompts[0];
                    }
                }
            }
            
            // Extract additional workflow details from nodes
            let modelName = null;
            let loraName = null;
            let samplerName = null;
            let steps = null;
            let cfg = null;
            let seed = null;
            
            if (workflowData && workflowData.nodes) {
                for (const [nodeId, node] of Object.entries(workflowData.nodes)) {
                    if (!node || typeof node !== 'object') continue;
                    
                    // Extract from KSampler node
                    if (node.class_type === 'KSampler' || node.class_type === 'KSamplerAdvanced') {
                        if (node.inputs) {
                            if (node.inputs.sampler_name) samplerName = String(node.inputs.sampler_name);
                            if (node.inputs.steps !== undefined) steps = node.inputs.steps;
                            if (node.inputs.cfg !== undefined) cfg = node.inputs.cfg;
                            if (node.inputs.seed !== undefined) seed = node.inputs.seed;
                        }
                    }
                    
                    // Extract from UNETLoader node
                    if (node.class_type === 'UNETLoader' || node.class_type === 'CheckpointLoaderSimple') {
                        if (node.inputs) {
                            if (node.inputs.unet_name) modelName = String(node.inputs.unet_name);
                            else if (node.inputs.ckpt_name) modelName = String(node.inputs.ckpt_name);
                        }
                    }
                    
                    // Extract from LoraLoader node
                    if (node.class_type === 'LoraLoader' || node.class_type === 'LoraLoaderModelOnly') {
                        if (node.inputs && node.inputs.lora_name) {
                            loraName = String(node.inputs.lora_name);
                        }
                    }
                }
            }
            
            if (workflowData) {
                const table = '<table class="metadata-table table-comfyui"><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>';
                let html = table;
                
                // Show workflow details first
                if (modelName) {
                    html += `<tr><td><strong>Model</strong></td><td style="color: #6FC3DF;">${escapeHtml(modelName)}</td></tr>`;
                }
                
                if (loraName) {
                    html += `<tr><td><strong>LoRA</strong></td><td style="color: #6FC3DF;">${escapeHtml(loraName)}</td></tr>`;
                }
                
                if (samplerName) {
                    html += `<tr><td><strong>Sampler</strong></td><td style="color: #D19A66;">${escapeHtml(samplerName)}</td></tr>`;
                }
                
                if (steps !== null && steps !== undefined) {
                    html += `<tr><td><strong>Steps</strong></td><td style="color: #D19A66;">${escapeHtml(String(steps))}</td></tr>`;
                }
                
                if (cfg !== null && cfg !== undefined) {
                    html += `<tr><td><strong>CFG Scale</strong></td><td>${escapeHtml(String(cfg))}</td></tr>`;
                }
                
                if (seed !== null && seed !== undefined) {
                    html += `<tr><td><strong>Seed</strong></td><td style="color: #6e7681;">${escapeHtml(String(seed))}</td></tr>`;
                }
                
                // Add separator row
                if (modelName || loraName || samplerName || steps !== null) {
                    html += `<tr><td colspan="2" style="border-top: 1px solid #30363d; padding-top: 5px;"></td></tr>`;
                }
                
                // Show prompt if available - FULL TEXT, NO TRUNCATION
                // Use original prompt with wildcards if available, otherwise use extracted promptText
                const displayPrompt = originalPromptWithWildcards || promptText;
                if (displayPrompt) {
                    const fullPrompt = String(displayPrompt);
                    const promptId = `prompt-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                    // Show full prompt, no truncation, with green color and copy icon
                    html += `<tr><td><strong>Prompt</strong></td><td style="white-space: pre-wrap; word-break: break-word; color: #98C379; font-weight: 500;"><div style="display: flex; align-items: flex-start; gap: 8px;"><span style="flex: 1;">${highlightBracketedText(fullPrompt)}</span><span class="copy-icon" onclick="copyGPSCoords('${escapeHtml(fullPrompt.replace(/'/g, "\\'").replace(/"/g, '&quot;'))}', this)" id="${promptId}" title="Click to copy prompt"></span></div></td></tr>`;
                }
                
                // Show resolved prompt if wildcards were detected
                if (originalPromptWithWildcards && resolvedPrompt) {
                    const resolvedId = `resolved-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                    html += `<tr><td><strong>Resolved Prompt</strong></td><td style="white-space: pre-wrap; word-break: break-word; color: #98C379; font-weight: 500;"><div style="display: flex; align-items: flex-start; gap: 8px;"><span style="flex: 1;">${highlightBracketedText(resolvedPrompt)}</span><span class="copy-icon" onclick="copyGPSCoords('${escapeHtml(resolvedPrompt.replace(/'/g, "\\'").replace(/"/g, '&quot;'))}', this)" id="${resolvedId}" title="Click to copy resolved prompt"></span></div></td></tr>`;
                    
                    // Show wildcard resolutions right after resolved prompt
                    const wildcards = extractWildcards(originalPromptWithWildcards, resolvedPrompt);
                    if (wildcards.length > 0) {
                        html += `<tr><td colspan="2" style="border-top: 1px solid #30363d; padding-top: 5px;"></td></tr>`;
                        html += `<tr><td colspan="2"><strong style="color: #6FC3DF;">Wildcard Resolutions</strong></td></tr>`;
                        for (const wc of wildcards) {
                            html += `<tr><td style="color: #D19A66; font-family: monospace;">${escapeHtml(wc.name)}</td><td style="color: #98C379;">${escapeHtml(wc.resolved)}</td></tr>`;
                        }
                    }
                }
                
                if (negativePrompt) {
                    const fullNeg = String(negativePrompt);
                    // Show full negative prompt, no truncation
                    html += `<tr><td><strong>Negative Prompt</strong></td><td style="white-space: pre-wrap; word-break: break-word; color: #6e7681;">${highlightBracketedText(fullNeg)}</td></tr>`;
                }
                
                // Show workflow info
                if (workflowData.nodes) {
                    html += `<tr><td colspan="2" style="border-top: 1px solid #30363d; padding-top: 5px;"></td></tr>`;
                    html += `<tr><td>Nodes</td><td>${Object.keys(workflowData.nodes).length} nodes</td></tr>`;
                }
                
                if (workflowData.workflow) {
                    html += `<tr><td>Workflow Type</td><td>ComfyUI Workflow</td></tr>`;
                }
                
                // Show other workflow properties
                for (const [key, value] of Object.entries(workflowData)) {
                    if (key !== 'nodes' && key !== 'workflow' && key !== 'prompt') {
                        html += `<tr><td>${escapeHtml(key)}</td><td>${escapeHtml(formatValue(value))}</td></tr>`;
                    }
                }
                
                html += '</tbody></table>';
                
                if (targetContainer) {
                    targetContainer.innerHTML = html;
                } else {
                    addLine(html);
                }
            } else {
                const errorMsg = '<div class="warning">ComfyUI workflow detected but could not parse structure</div>';
                if (targetContainer) {
                    targetContainer.innerHTML = errorMsg;
                } else {
                    addOutput('ComfyUI workflow detected but could not parse structure', 'warning');
                }
            }
        }
        
        function processFile(file) {
            addCommand(`"${file.name}"`);
            
            // Add analyzing line with placeholder for "done"
            const analyzingLine = document.createElement('div');
            analyzingLine.className = 'terminal-line';
            analyzingLine.id = 'analyzingLine';
            analyzingLine.innerHTML = '<span class="info">Analyzing file...</span>';
            terminal.appendChild(analyzingLine);
            terminal.scrollTop = terminal.scrollHeight;
            
            const formData = new FormData();
            formData.append('file', file);
            
            fetch('/analyze', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Update analyzing line to show "done"
                const analyzingEl = document.getElementById('analyzingLine');
                if (analyzingEl) {
                    analyzingEl.innerHTML = '<span class="info">Analyzing file...</span> <span class="success">done</span>';
                }
                
                if (data.error) {
                    addOutput(`Error: ${data.error}`, 'error');
                } else {
                    addOutput('Metadata extracted successfully:', 'success');
                    
                    // Store metadata for JSON export
                    window.currentMetadata = data.metadata;
                    
                    // Display provenance summary first
                    if (data.metadata) {
                        addProvenanceSummary(data.metadata);
                    }
                    
                    // Display data type recap
                    if (data.metadata) {
                        addDataRecap(data.metadata);
                    }
                    
                    // Add JSON export button
                    const jsonExportLine = document.createElement('div');
                    jsonExportLine.className = 'terminal-line';
                    jsonExportLine.innerHTML = `<span class="output">--format json</span> <span class="copy-icon" onclick="exportJSON()" title="Click to download JSON file" style="margin-left: 8px;"></span>`;
                    terminal.appendChild(jsonExportLine);
                    terminal.scrollTop = terminal.scrollHeight;
                    
                    // Create metadata grid container
                    const gridContainer = document.createElement('div');
                    gridContainer.className = 'metadata-grid';
                    terminal.appendChild(gridContainer);
                    
                    // Helper to add section to grid
                    function addGridSection(title, content, sectionType) {
                        const section = document.createElement('div');
                        section.className = 'metadata-section';
                        section.id = `section-${sectionType}`;
                        
                        const titleEl = document.createElement('div');
                        titleEl.className = `metadata-section-title ${sectionType}`;
                        titleEl.textContent = title;
                        section.appendChild(titleEl);
                        
                        const contentEl = document.createElement('div');
                        contentEl.innerHTML = content;
                        section.appendChild(contentEl);
                        
                        gridContainer.appendChild(section);
                    }
                    
                    // Display summary
                    if (data.metadata && data.metadata.summary) {
                        const summary = data.metadata.summary;
                        const formattedSummary = {};
                        
                        // Copy existing fields
                        if (summary.fileName) formattedSummary.fileName = summary.fileName;
                        if (summary.containerType) formattedSummary.containerType = summary.containerType;
                        
                        // Format file size
                        if (summary.fileSize !== undefined) {
                            formattedSummary['fileSize (b)'] = summary.fileSizeBytes || `${summary.fileSize.toLocaleString()} bytes`;
                            if (summary.fileSizeMB) {
                                formattedSummary['fileSize (MB)'] = summary.fileSizeMB;
                            } else if (summary.fileSize) {
                                const mb = (summary.fileSize / (1024 * 1024)).toFixed(2);
                                formattedSummary['fileSize (MB)'] = `${mb} MB`;
                            }
                            
                            // Add non-pixel data metrics
                            if (summary.nonPixelBytes !== undefined) {
                                formattedSummary['nonPixelBytes'] = `${summary.nonPixelBytes.toLocaleString()} bytes`;
                            }
                            if (summary.nonPixelRatio !== undefined && summary.nonPixelRatio !== null) {
                                formattedSummary['nonPixelRatio'] = summary.nonPixelRatio;
                            }
                        }
                        
                        // Add dimensions
                        if (summary.dimensions) {
                            formattedSummary.Dimensions = summary.dimensions;
                        }
                        if (summary.width !== undefined && summary.width !== null) {
                            formattedSummary.Width = summary.width;
                        }
                        if (summary.height !== undefined && summary.height !== null) {
                            formattedSummary.Height = summary.height;
                        }
                        
                        // Add date created
                        if (summary.dateCreated) {
                            formattedSummary['Date Created'] = new Date(summary.dateCreated).toLocaleString();
                        }
                        
                        // Add boolean flags
                        if (summary.hasExif !== undefined) formattedSummary.hasExif = summary.hasExif;
                        if (summary.hasPayloads !== undefined) formattedSummary.hasPayloads = summary.hasPayloads;
                        if (summary.hasAiMetadata !== undefined) formattedSummary.hasAiMetadata = summary.hasAiMetadata;
                        
                        const summaryTable = createMetadataTableHTML(formattedSummary, 'summary');
                        addGridSection('Summary', summaryTable, 'summary');
                    }
                    
                    // Display structure
                    if (data.metadata && data.metadata.structure) {
                        const structureTable = createMetadataTableHTML(data.metadata.structure, 'structure');
                        addGridSection('Structure', structureTable, 'structure');
                    }
                    
                    // Display declared metadata
                    if (data.metadata && data.metadata.metadata) {
                        const metadataTable = createMetadataTableHTML(data.metadata.metadata, 'metadata');
                        addGridSection('Declared Metadata', metadataTable, 'metadata');
                    }
                    
                    // Display ComfyUI section if workflow detected
                    const hasComfyUI = data.metadata?.aiMetadata?.aiMetadata?.tool === 'ComfyUI' || 
                                     data.metadata?.payloads?.payloads?.some(p => {
                                         const content = p.content;
                                         if (typeof content === 'object') {
                                             return content.nodes || content.workflow || content.prompt;
                                         }
                                         if (typeof content === 'string') {
                                             try {
                                                 const parsed = JSON.parse(content);
                                                 return parsed.nodes || parsed.workflow || parsed.prompt;
                                             } catch(e) {
                                                 return false;
                                             }
                                         }
                                         return false;
                                     });
                    
                    if (hasComfyUI) {
                        // Create ComfyUI section HTML
                        const comfyUISection = document.createElement('div');
                        addComfyUISection(data.metadata, comfyUISection);
                        const comfyContent = comfyUISection.innerHTML;
                        addGridSection('ComfyUI Workflow', comfyContent, 'comfyui');
                    }
                    
                    // Display AI metadata
                    if (data.metadata && data.metadata.aiMetadata) {
                        const aiTable = createMetadataTableHTML(data.metadata.aiMetadata, 'ai');
                        addGridSection('Encryption and AI', aiTable, 'ai');
                    }
                    
                    // Display anomalies
                    if (data.metadata && data.metadata.anomalies) {
                        const anomalyTable = createMetadataTableHTML(data.metadata.anomalies, 'anomaly');
                        addGridSection('Anomalies', anomalyTable, 'anomaly');
                    }
                    
                    // Display payloads (but skip if ComfyUI section already showed them)
                    if (data.metadata && data.metadata.payloads && !hasComfyUI) {
                        const payloadTable = createMetadataTableHTML(data.metadata.payloads, 'payload');
                        addGridSection('Payloads', payloadTable, 'payload');
                    }
                    
                    terminal.scrollTop = terminal.scrollHeight;
                    
                    // Store payloads and file path for chunk modal access
                    if (data.metadata && data.metadata.payloads) {
                        window.currentPayloads = data.metadata.payloads.payloads || [];
                    }
                    if (data.file_path) {
                        window.currentFilePath = data.file_path;
                    }
                    
                    // Update chunks visualization if chunks data exists
                    if (data.metadata && data.metadata.structure) {
                        console.log('Structure data:', data.metadata.structure);
                        if (data.metadata.structure.chunks && Array.isArray(data.metadata.structure.chunks) && data.metadata.structure.chunks.length > 0) {
                            console.log('Found chunks:', data.metadata.structure.chunks.length);
                            updateChunksVisualization(data.metadata.structure);
                        } else {
                            console.log('No chunks found in structure');
                        }
                    } else {
                        console.log('No structure data in metadata');
                    }
                    
                    // Full metadata table as fallback
                    if (data.metadata) {
                        addMetadataTable(data.metadata);
                    }
                    
                    if (data.json) {
                        addOutput('JSON Output:', 'info');
                        addJsonOutput(data.metadata);
                    }
                }
            })
            .catch(error => {
                addOutput(`Error: ${error.message}`, 'error');
            });
        }
        
        // Initialize file handlers after DOM is ready
        function initFileHandlers() {
            terminal = document.getElementById('terminal');
            fileInput = document.getElementById('fileInput');
            uploadArea = document.getElementById('uploadArea');
            parsingFlow = document.getElementById('parsingFlow');
            chunksContent = document.getElementById('chunksContent');
            
            if (!fileInput || !uploadArea) {
                console.error('File input or upload area not found');
                return;
            }
            
            // File input handler
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    processFile(e.target.files[0]);
                }
            });
            
            // Drag and drop
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                if (e.dataTransfer.files.length > 0) {
                    processFile(e.dataTransfer.files[0]);
                }
            });
        }
        
        // Initialize on DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initFileHandlers);
        } else {
            initFileHandlers();
        }
    </script>
</body>
</html>
"""

# Create a web-compatible version of the extractor
if MetadataExtractor:
    class MetadataExtractorWeb:
        def __init__(self):
            self.extractor = MetadataExtractor()
        
        def extract_from_file(self, file_path):
            """Extract metadata from uploaded file"""
            return self.extractor.extract_metadata(file_path)
    
    extractor_web = MetadataExtractorWeb()
else:
    extractor_web = None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if not extractor_web:
            return jsonify({'error': 'Metadata extractor not available'}), 500
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file temporarily
        upload_dir = Path('uploads')
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file.filename
        file.save(str(file_path))
        
        # Use layered inspector for detailed analysis
        try:
            from core.layered_inspector import LayeredInspector
            from rich.console import Console
            from io import StringIO
            
            # Run layered inspection
            console = Console(file=StringIO(), force_terminal=False, width=120)
            inspector = LayeredInspector(console=console, verbose=False)  # Quiet mode for web
            
            results = inspector.phase_0_orchestrate(str(file_path))
            final_report = results["phases"]["8_report"]
            
            # Convert report to JSON-serializable format
            def make_serializable(obj):
                if isinstance(obj, dict):
                    return {k: make_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [make_serializable(item) for item in obj]
                elif isinstance(obj, (int, float, str, bool, type(None))):
                    return obj
                else:
                    return str(obj)
            
            serializable_report = make_serializable(final_report)
            
            # Store file path temporarily for chunk content access
            # We'll keep the file until the session ends or a new file is uploaded
            session_file_path = str(file_path)
            
            # Clean up old files (keep only the most recent)
            try:
                for old_file in upload_dir.glob('*'):
                    if old_file != file_path:
                        old_file.unlink()
            except:
                pass
            
            return jsonify({
                'success': True,
                'metadata': serializable_report,
                'phases': {
                    '0_orchestrate': make_serializable(results.get("phases", {}).get("0_orchestrate", {})),
                    '1_intake': make_serializable(results["phases"]["1_intake"]),
                    '2_container': make_serializable(results["phases"]["2_container"]),
                    '3_structure': make_serializable(results["phases"]["3_structure"]),
                    '4_metadata': make_serializable(results["phases"]["4_metadata"]),
                    '5_payloads': make_serializable(results["phases"]["5_payloads"]),
                    '6_ai_patterns': make_serializable(results["phases"]["6_ai_patterns"]),
                    '7_anomalies': make_serializable(results["phases"]["7_anomalies"]),
                    '8_report': make_serializable(results["phases"]["8_report"])
                },
                'json': request.form.get('format') == 'json',
                'file_path': session_file_path  # Return file path for chunk content access
            })
            
        except Exception as e:
            # Fallback to simple extractor
            if extractor_web:
                metadata = extractor_web.extract_from_file(str(file_path))
                try:
                    file_path.unlink()
                except:
                    pass
                
                if metadata:
                    return jsonify({
                        'success': True,
                        'metadata': metadata,
                        'json': request.form.get('format') == 'json'
                    })
            
            try:
                file_path.unlink()
            except:
                pass
            
            return jsonify({'error': f'Inspection failed: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chunk-content', methods=['POST'])
def chunk_content():
    """Fetch chunk content from file"""
    try:
        data = request.json
        file_path = data.get('file_path')
        offset = int(data.get('offset', 0))
        length = int(data.get('length', 64))
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Limit length to prevent abuse
        length = min(length, 1024)
        
        with open(file_path, 'rb') as f:
            f.seek(offset)
            bytes_data = f.read(length)
        
        # Convert to base64 for JSON transport
        return jsonify({
            'success': True,
            'data': base64.b64encode(bytes_data).decode('utf-8'),
            'length': len(bytes_data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    import webbrowser
    from threading import Timer
    
    port = 5000
    
    def open_browser():
        webbrowser.open(f'http://localhost:{port}')
    
    print("=" * 60)
    print("BareBlocks Web Interface")
    print("=" * 60)
    print(f"\n🚀 Starting server on http://localhost:{port}")
    print("📝 Opening browser in 2 seconds...")
    print("\nPress Ctrl+C to stop the server\n")
    
    Timer(2.0, open_browser).start()
    
    app.run(host='0.0.0.0', port=port, debug=True)

