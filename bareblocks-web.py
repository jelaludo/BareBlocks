#!/usr/bin/env python3
"""
BareBlocks Web Interface - Browser-based CLI-style metadata inspector
Runs on localhost with a terminal-like interface
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory
import os
import json
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
            color: #6FC3DF;
            font-weight: bold;
            font-size: 12px;
            margin-bottom: 8px;
            padding-bottom: 5px;
            border-bottom: 1px solid #30363d;
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
            width: 28%;
            max-width: 160px;
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
        }
        
        .not-found {
            color: #6e7681;
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
                </div>
            </div>
            <div class="terminal-controls">
                <button class="control-btn close" onclick="window.close()"></button>
                <button class="control-btn minimize"></button>
                <button class="control-btn maximize"></button>
            </div>
        </div>
        
        <div class="terminal-body" id="terminal"><div class="terminal-line"><span class="prompt">$</span> <span class="title">BareBlocks - Metadata Inspector</span></div><div class="terminal-line"><span class="prompt">$</span> <span class="subtitle">Making image files legible beyond their pixels</span></div><div class="terminal-line"><span class="prompt">$</span> <span class="command">bareblocks --help</span></div><div class="terminal-line output">Usage: bareblocks &lt;file_path&gt; [options]</div><div class="terminal-line output">Options:</div><div class="terminal-line output">&nbsp;&nbsp;--format json    Output as JSON</div><div class="terminal-line output">&nbsp;&nbsp;--save FILE      Save metadata to file</div><div class="terminal-line"><span class="prompt">$</span> <span class="command">bareblocks &lt;file&gt;</span></div></div>
        
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
        
        <div class="input-area">
            <span class="input-prompt">$</span>
            <input type="file" id="fileInput" class="file-input" accept="image/*,video/*,audio/*,.pdf,.docx">
            <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
                <span class="info">📁 Click or drag file here to analyze</span>
            </div>
        </div>
    </div>
    
    <script>
        const terminal = document.getElementById('terminal');
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        const parsingFlow = document.getElementById('parsingFlow');
        
        function switchTab(tab) {
            const mainTab = document.getElementById('mainTab');
            const flowTab = document.getElementById('flowTab');
            
            if (tab === 'main') {
                terminal.style.display = 'flex';
                parsingFlow.classList.remove('active');
                mainTab.classList.add('active');
                flowTab.classList.remove('active');
            } else {
                terminal.style.display = 'none';
                parsingFlow.classList.add('active');
                mainTab.classList.remove('active');
                flowTab.classList.add('active');
            }
        }
        
        // Make switchTab globally accessible
        window.switchTab = switchTab;
        
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
            
            function addRows(obj, prefix = '', depth = 0) {
                if (depth > 2) return; // Limit nesting depth
                for (const [key, value] of Object.entries(obj)) {
                    const fullKey = prefix ? `${prefix}.${key}` : key;
                    if (value && typeof value === 'object' && !Array.isArray(value)) {
                        // For nested objects, show summary and expand on click
                        const itemCount = Object.keys(value).length;
                        html += `<tr class="expandable" onclick="toggleRow(this)" style="cursor: pointer;"><td>${escapeHtml(fullKey)}</td><td>[Object: ${itemCount} properties] <span class="toggle">+</span></td></tr>`;
                        // Add nested rows (hidden by default) - use proper table structure
                        html += `<tr class="nested" style="display:none;"><td colspan="2" style="padding-left:20px; padding-top:0; padding-bottom:0;">`;
                        // Create nested table for proper structure
                        html += `<table style="width:100%; margin:0; border-collapse:collapse; font-size:10px;">`;
                        for (const [nestedKey, nestedValue] of Object.entries(value)) {
                            const nestedFullKey = `${fullKey}.${nestedKey}`;
                            if (nestedValue && typeof nestedValue === 'object' && !Array.isArray(nestedValue) && depth < 1) {
                                const nestedItemCount = Object.keys(nestedValue).length;
                                html += `<tr class="expandable" onclick="toggleRow(this)" style="cursor: pointer;"><td>${escapeHtml(nestedKey)}</td><td>[Object: ${nestedItemCount} properties] <span class="toggle">+</span></td></tr>`;
                                html += `<tr class="nested" style="display:none;"><td colspan="2" style="padding-left:15px;">`;
                                html += `<table style="width:100%; margin:0; border-collapse:collapse; font-size:10px;">`;
                                for (const [deepKey, deepValue] of Object.entries(nestedValue)) {
                                    html += `<tr><td>${escapeHtml(deepKey)}</td><td>${escapeHtml(formatValue(deepValue))}</td></tr>`;
                                }
                                html += `</table></td></tr>`;
                            } else {
                                html += `<tr><td>${escapeHtml(nestedKey)}</td><td>${escapeHtml(formatValue(nestedValue))}</td></tr>`;
                            }
                        }
                        html += `</table></td></tr>`;
                    } else {
                        html += `<tr><td>${escapeHtml(fullKey)}</td><td>${escapeHtml(formatValue(value))}</td></tr>`;
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
        
        function addDataRecap(metadata) {
            const checks = [];
            
            // Standard metadata formats
            const exif = metadata.metadata?.exif || {};
            const structure = metadata.structure || {};
            const payloads = metadata.payloads?.payloads || [];
            const aiMeta = metadata.aiMetadata?.aiMetadata || {};
            const exifKeys = Object.keys(exif);
            
            // Helper to check if any key contains substring
            const hasKey = (substr) => exifKeys.some(k => k.toLowerCase().includes(substr.toLowerCase()));
            
            // Standard metadata checks
            checks.push({name: 'Camera data', found: hasKey('make') || hasKey('model') || hasKey('camera')});
            checks.push({name: 'Geo data', found: metadata.metadata?.gps !== undefined || hasKey('gps') || hasKey('latitude') || hasKey('longitude')});
            checks.push({name: 'EXIF', found: exifKeys.length > 0});
            checks.push({name: 'IPTC', found: hasKey('iptc') || metadata.metadata?.iptc !== undefined});
            checks.push({name: 'XMP', found: metadata.metadata?.xmp !== undefined || hasKey('xmp')});
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
            
            // Format as compact list
            let recapHtml = '<div class="data-recap">';
            checks.forEach(check => {
                const status = check.found ? '<span class="found">found</span>' : '<span class="not-found">not found</span>';
                recapHtml += `<span class="recap-item">${escapeHtml(check.name)}: ${status}</span> `;
            });
            recapHtml += '</div>';
            addLine(recapHtml);
        }
        
        function addComfyUISection(metadata, targetContainer = null) {
            const payloads = metadata.payloads?.payloads || [];
            const aiMeta = metadata.aiMetadata?.aiMetadata || {};
            
            // Find ComfyUI workflow JSON - check all payloads
            let workflowData = null;
            let promptText = null;
            let negativePrompt = null;
            let allWorkflowData = [];
            
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
            
            // Also check the "prompt" keyword payload for node data
            let promptNodes = null;
            for (const payload of payloads) {
                if (payload.classification === 'json' && payload.keyword === 'prompt') {
                    let content = payload.content;
                    if (typeof content === 'string') {
                        try {
                            content = JSON.parse(content);
                        } catch(e) {
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
                    html += `<tr><td><strong>Sampler</strong></td><td>${escapeHtml(samplerName)}</td></tr>`;
                }
                
                if (steps !== null && steps !== undefined) {
                    html += `<tr><td><strong>Steps</strong></td><td>${escapeHtml(String(steps))}</td></tr>`;
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
                if (promptText) {
                    const fullPrompt = String(promptText);
                    // Show full prompt, no truncation, with green color
                    html += `<tr><td><strong>Prompt</strong></td><td style="white-space: pre-wrap; word-break: break-word; color: #98C379; font-weight: 500;">${highlightBracketedText(fullPrompt)}</td></tr>`;
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
                    
                    // Display data type recap
                    if (data.metadata) {
                        addDataRecap(data.metadata);
                    }
                    
                    // Create metadata grid container
                    const gridContainer = document.createElement('div');
                    gridContainer.className = 'metadata-grid';
                    terminal.appendChild(gridContainer);
                    
                    // Helper to add section to grid
                    function addGridSection(title, content, sectionType) {
                        const section = document.createElement('div');
                        section.className = 'metadata-section';
                        
                        const titleEl = document.createElement('div');
                        titleEl.className = 'metadata-section-title';
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
                            formattedSummary['fileSize (bytes)'] = summary.fileSizeBytes || `${summary.fileSize.toLocaleString()} bytes`;
                            if (summary.fileSizeMB) {
                                formattedSummary['fileSize (MB)'] = summary.fileSizeMB;
                            } else if (summary.fileSize) {
                                const mb = (summary.fileSize / (1024 * 1024)).toFixed(2);
                                formattedSummary['fileSize (MB)'] = `${mb} MB`;
                            }
                            
                            // Add non-pixel data metrics
                            if (summary.nonPixelBytes !== undefined) {
                                formattedSummary['nonPixelBytes'] = summary.nonPixelBytes.toLocaleString();
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
                        addGridSection('AI Metadata', aiTable, 'ai');
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
            
            # Clean up
            try:
                file_path.unlink()
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
                'json': request.form.get('format') == 'json'
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

