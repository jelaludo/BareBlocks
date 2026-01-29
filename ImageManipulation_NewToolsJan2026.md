# Cursor Integration Prompt: BareBlocks Image Suite Expansion

## Project Context

**Project Name:** BareBlocks Terminal  
**Current State:** Working metadata analyzer for AI-generated images (ComfyUI, A1111, PNG chunks, EXIF, etc.)  
**Goal:** Expand into a comprehensive static web-based image manipulation suite with terminal aesthetic  
**Deployment Target:** GitHub Pages (static site, no server-side processing)  
**Primary Use Case:** Personal tool for AI artist/BJJ instructor, potential public release if polished

## Existing Codebase Analysis Required

Please analyze the current BareBlocks metadata tool and provide:

1. **File Structure Inventory:**
   - List all HTML, CSS, JS files
   - Identify shared utilities vs. page-specific code
   - Map data flow for image processing

2. **Current Architecture Assessment:**
   - How are images loaded and processed?
   - What libraries are being used? (exifr, pngjs, etc.)
   - How is the UI structured? (Three-panel layout: ComfyUI | Encryption/AI | Anomalies)
   - What metadata extraction methods exist?

3. **Code Reusability Analysis:**
   - Identify functions that can be extracted to shared utilities
   - Assess file I/O patterns (FileReader, drag-drop, etc.)
   - Evaluate UI patterns for consistency across new tools

4. **Terminal UI Elements:**
   - What CSS classes/components create the terminal aesthetic?
   - How is output formatted? (tables, progress bars, etc.)
   - What fonts, colors, spacing are used?

## New Features to Integrate

### Core Image Manipulation Tools

**1. Image Merger**
- **Functionality:**
  - Merge 2+ images horizontally or vertically
  - Configurable spacing between images (0-100px)
  - Auto-align: top/center/bottom for horizontal, left/center/right for vertical
  - Background color fill for mismatched sizes
  - Preserve aspect ratios
  
- **UI Requirements:**
  - Multi-file drag-drop zone
  - Live preview canvas
  - Controls: merge direction, spacing slider, alignment dropdown
  - Display total dimensions before merging
  
- **Output:**
  - Download as PNG
  - Option to copy metadata from first image

**2. Grid Generator**
- **Functionality:**
  - Create N×M grid from uploaded images
  - Smart auto-layout (e.g., 6 images → 3×2 or 2×3 based on aspect ratio)
  - Manual column count override (1-10 cols)
  - Configurable: cell padding, background color, border
  - Handle uneven image counts (empty cells or stretch last)
  
- **UI Requirements:**
  - Show grid preview before finalizing
  - Real-time column adjustment
  - Display: "Creating 3×2 grid (6 images, 0 empty cells)"
  
- **Output:**
  - Single merged image
  - Optional: save grid layout config as JSON

**3. Batch Resizer**
- **Functionality:**
  - Resize multiple images to target width/height
  - Maintain aspect ratio option
  - Multiple resize modes:
    - Fixed width (height auto)
    - Fixed height (width auto)
    - Max dimension (fit within bounds)
    - Exact dimensions (may distort)
  - Batch process: show progress bar
  
- **UI Requirements:**
  - Input: target dimensions
  - Preview first image
  - Show before/after dimensions table
  
- **Output:**
  - Download as ZIP or individual files
  - Preserve original filenames with suffix (e.g., `image_800w.png`)

**4. Watermark Tool**
- **Functionality:**
  - Add text or image watermark
  - Text options: font, size, color, opacity, rotation
  - Position: 9-point grid (corners, edges, center) or drag to place
  - Image watermark: opacity, scale, blend modes
  - Batch apply to multiple images
  
- **UI Requirements:**
  - Live preview with draggable watermark
  - Text input with style controls
  - Or upload watermark image
  
- **Output:**
  - Watermarked images
  - Save watermark preset for reuse

**5. Metadata Writer**
- **Functionality:**
  - **Add** custom metadata to images (PNG tEXt chunks, EXIF, XMP)
  - **Strip** all metadata (privacy tool)
  - **Copy** metadata from one image to another
  - Support AI-specific fields:
    - ComfyUI workflow JSON
    - Prompt text
    - Model/LoRA names
    - Generation parameters (seed, steps, CFG, sampler)
  - Batch operations
  
- **UI Requirements:**
  - Form to input metadata fields
  - Load template (e.g., "ComfyUI Standard")
  - Preview metadata before writing
  - Warning if overwriting existing data
  
- **Output:**
  - Modified image files
  - Verification: re-analyze to confirm metadata written

**6. Format Converter**
- **Functionality:**
  - PNG ↔ JPG ↔ WEBP ↔ BMP
  - Quality slider for lossy formats
  - Batch convert
  - Show file size comparison
  
- **UI Requirements:**
  - Source format detection
  - Target format selector
  - Quality slider (if applicable)
  - Before/after file sizes
  
- **Output:**
  - Converted files
  - Show total size saved/added

### Auxiliary Tools

**7. Wildcard Expander**
- **Functionality:**
  - Load wildcard JSON files (user's existing lists)
  - Parse prompts with `__wildcard__` syntax
  - Generate N variations (1-100)
  - Preview first 5 before generating all
  - Export as batch text file (one prompt per line)
  
- **Example:**
  ```
  Input: "watercolor painting of a __country__ warrior"
  Wildcards: {country: ["Japanese", "Brazilian", "French"]}
  Output: 3 variations with random selections
  ```
  
- **UI Requirements:**
  - Text area for prompt input
  - Upload/select wildcard JSON
  - Number of variations slider
  - "Generate" button
  - Display results in scrollable list
  
- **Output:**
  - Copy to clipboard
  - Download as `.txt` (one per line)

**8. Workflow Visualizer** (Phase 2)
- **Functionality:**
  - Parse ComfyUI workflow JSON from metadata
  - Render node graph (visual flow diagram)
  - Color-code node types (samplers, models, LoRAs, etc.)
  - Click node to see parameters
  
- **Libraries:**
  - **Cytoscape.js** or **D3.js** force-directed graph
  
- **UI Requirements:**
  - Upload image or paste workflow JSON
  - Zoomable/pannable graph
  - Export as SVG
  
- **Output:**
  - Visual workflow diagram
  - Node statistics (count, types)

**9. Token Counter** (Phase 2)
- **Functionality:**
  - Count CLIP tokens in prompt
  - Show breakdown by segment
  - Highlight overflow (>75 tokens for SD1.5, >77 for SDXL)
  - Visual progress bar
  
- **Implementation:**
  - Use **tiktoken** (GPT tokenizer as approximation)
  - Or implement basic CLIP tokenizer in JS
  
- **UI Requirements:**
  - Text area for prompt input
  - Live count updates
  - Color-coded: green (<75), yellow (75-85), red (>85)
  
- **Output:**
  - Token count
  - Truncated prompt if over limit

## Integration Architecture Recommendations

### File Structure (Proposed)

```
bareblocks/
├── index.html                    # Landing page / tool selector
├── metadata.html                 # Existing metadata analyzer
├── /tools/
│   ├── merge.html               # Image merger
│   ├── grid.html                # Grid generator
│   ├── resize.html              # Batch resizer
│   ├── watermark.html           # Watermark tool
│   ├── metadata-writer.html     # Write/strip metadata
│   ├── converter.html           # Format converter
│   ├── wildcards.html           # Wildcard expander
│   ├── workflow-viz.html        # Workflow visualizer
│   └── token-counter.html       # Token counter
├── /lib/
│   ├── core/
│   │   ├── image-processor.js   # Canvas operations, loading
│   │   ├── metadata-reader.js   # Extract metadata (existing code)
│   │   ├── metadata-writer.js   # Write PNG chunks, EXIF, XMP
│   │   └── file-handler.js      # Drag-drop, FileReader, ZIP export
│   ├── tools/
│   │   ├── merger.js            # Merge/grid logic
│   │   ├── resizer.js           # Resize operations
│   │   ├── watermark.js         # Watermark placement
│   │   └── converter.js         # Format conversion
│   ├── ui/
│   │   ├── terminal.js          # Terminal UI components
│   │   ├── progress.js          # Progress bars, animations
│   │   └── file-preview.js      # Image thumbnails, galleries
│   └── utils/
│       ├── png-chunk.js         # PNG tEXt/iTXt chunk manipulation
│       ├── crc32.js             # CRC32 for PNG integrity
│       └── validators.js        # Input validation
├── /assets/
│   ├── css/
│   │   ├── terminal.css         # Main stylesheet
│   │   └── components.css       # Reusable UI components
│   ├── data/
│   │   └── wildcards.json       # Default wildcard lists
│   └── fonts/
│       └── JetBrainsMono.woff2  # Monospace font
├── /docs/                       # Optional documentation
└── README.md
```

### Shared Library Design Principles

**1. Core Image Processor (image-processor.js)**
```javascript
export class ImageProcessor {
  constructor() {
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
  }

  // Load image from File/Blob/URL
  async loadImage(source) { }

  // Load multiple images with progress callback
  async loadImages(sources, onProgress = null) { }

  // Common canvas operations
  resize(img, width, height, maintainAspect = true) { }
  crop(img, x, y, width, height) { }
  rotate(img, degrees) { }
  flip(img, horizontal = true) { }

  // Export canvas to various formats
  toBlob(format = 'png', quality = 0.92) { }
  toDataURL(format = 'png', quality = 0.92) { }
  downloadCanvas(filename) { }
}
```

**2. Metadata Handler (metadata-reader.js + metadata-writer.js)**
```javascript
// Reader (existing functionality)
export class MetadataReader {
  async analyze(file) {
    return {
      exif: await this.extractEXIF(file),
      png: await this.extractPNGChunks(file),
      comfyui: await this.extractComfyUI(file),
      // ... etc
    };
  }
}

// Writer (new functionality)
export class MetadataWriter {
  async writePNGText(imageBlob, key, value) { }
  async writeEXIF(imageBlob, exifData) { }
  async copyMetadata(sourceFile, targetFile) { }
  async stripAllMetadata(imageBlob) { }
}
```

**3. Terminal UI Framework (ui/terminal.js)**
```javascript
export class Terminal {
  constructor(containerId) { }

  // Output methods
  print(message, type = 'info') { }      // info, success, error, warning
  printTable(data, headers = null) { }
  printProgress(current, total, label) { }
  printHeader(title) { }
  printSeparator() { }

  // Input methods
  async prompt(question) { }
  async confirm(question) { }

  // Utility
  clear() { }
  scrollToBottom() { }
  typewriter(text, speed = 30) { }       // Animated typing effect
}
```

**4. File Handler (file-handler.js)**
```javascript
export class FileHandler {
  // Drag-drop zone setup
  setupDropZone(element, onFiles) { }

  // Batch export
  async createZIP(files, zipName) { }
  async downloadMultiple(blobs, filenames) { }

  // File reading
  async readAsArrayBuffer(file) { }
  async readAsDataURL(file) { }

  // Validation
  isValidImageType(file) { }
  checkFileSize(file, maxMB) { }
}
```

### Integration Patterns

**Pattern 1: Consistent Tool Structure**

Every tool should follow this template:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BareBlocks - [Tool Name]</title>
  <link rel="stylesheet" href="../assets/css/terminal.css">
</head>
<body>
  <!-- Terminal Header -->
  <header class="terminal-header">
    <div class="breadcrumb">
      <a href="../index.html">BareBlocks</a> / <span>[Tool Name]</span>
    </div>
    <div class="tool-status" id="status">Ready</div>
  </header>

  <!-- Main Terminal Output -->
  <div class="terminal-container">
    <div id="terminal" class="terminal-output"></div>
  </div>

  <!-- File Input Zone -->
  <div class="drop-zone" id="dropZone">
    <div class="drop-icon">📁</div>
    <p>Drop images here or click to select</p>
    <input type="file" id="fileInput" multiple accept="image/*" hidden>
  </div>

  <!-- Tool-Specific Controls -->
  <div class="controls-panel">
    <!-- Custom controls here -->
  </div>

  <!-- Preview Canvas -->
  <canvas id="preview" class="preview-canvas"></canvas>

  <!-- Action Buttons -->
  <div class="action-bar">
    <button class="btn-primary" onclick="processImages()">Process</button>
    <button class="btn-secondary" onclick="exportResult()">Export</button>
    <button class="btn-tertiary" onclick="reset()">Reset</button>
  </div>

  <script type="module" src="[tool].js"></script>
</body>
</html>
```

**Pattern 2: Tool Module Structure**

```javascript
// tools/merge.js
import { ImageProcessor } from '../lib/core/image-processor.js';
import { Terminal } from '../lib/ui/terminal.js';
import { FileHandler } from '../lib/core/file-handler.js';

class ImageMerger {
  constructor() {
    this.processor = new ImageProcessor();
    this.terminal = new Terminal('terminal');
    this.fileHandler = new FileHandler();
    this.loadedImages = [];
    this.init();
  }

  init() {
    this.fileHandler.setupDropZone(
      document.getElementById('dropZone'),
      (files) => this.handleFiles(files)
    );
    this.setupControls();
  }

  async handleFiles(files) {
    this.terminal.print(`Loading ${files.length} images...`);
    
    this.loadedImages = await this.processor.loadImages(
      files,
      (current, total) => {
        this.terminal.printProgress(current, total, 'Loading');
      }
    );

    this.terminal.print(`✓ Loaded ${this.loadedImages.length} images`, 'success');
    this.displayImageInfo();
  }

  displayImageInfo() {
    const info = this.loadedImages.map((img, i) => ({
      '#': i + 1,
      'Dimensions': `${img.width}×${img.height}`,
      'Aspect': (img.width / img.height).toFixed(2)
    }));
    this.terminal.printTable(info);
  }

  async mergeHorizontal() {
    // Implementation
  }

  setupControls() {
    // Bind event listeners
  }
}

// Initialize
new ImageMerger();
```

**Pattern 3: State Management**

```javascript
// Simple state manager for complex tools
export class ToolState {
  constructor(initialState = {}) {
    this.state = { ...initialState };
    this.listeners = [];
  }

  setState(updates) {
    this.state = { ...this.state, ...updates };
    this.notify();
  }

  getState() {
    return { ...this.state };
  }

  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  notify() {
    this.listeners.forEach(listener => listener(this.state));
  }
}

// Usage in tool
const state = new ToolState({
  images: [],
  processing: false,
  result: null
});

state.subscribe((newState) => {
  updateUI(newState);
});
```

### UI/UX Consistency Guidelines

**Terminal Aesthetic:**
- **Font:** JetBrains Mono or Fira Code
- **Colors:**
  - Background: `#0a0a0a` or `#1a1a1a`
  - Text: `#00ff00` (green), `#00ffff` (cyan), `#ffff00` (yellow)
  - Accent: `#ff00ff` (magenta for errors)
- **Borders:** Single-line box drawing characters (`┌─┐│└─┘`)
- **Animations:** Typewriter effect for output, progress bars

**Output Formatting:**
```
> Loading images...
[████████████████████] 100% (5/5)

┌─ Image Analysis ─────────────────────────────────┐
│ Total Images: 5                                   │
│ Total Pixels: 15,728,640                          │
│ Average Size: 2048×1536                           │
└───────────────────────────────────────────────────┘

✓ Analysis complete
```

**Button States:**
- Default: subtle border, dim text
- Hover: brighter border, color shift
- Active: inverted colors
- Disabled: grayed out, cursor: not-allowed

**Progress Indicators:**
- Bar: `[████████░░░░░░░░░░░░] 40%`
- Spinner: `⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏` (rotating)
- Steps: `[1/5] Processing image.png...`

### Error Handling Standards

```javascript
// Centralized error handler
export class ErrorHandler {
  static handle(error, terminal, context = '') {
    const message = this.formatError(error, context);
    terminal.print(message, 'error');
    console.error('[BareBlocks]', context, error);
  }

  static formatError(error, context) {
    const prefix = context ? `[${context}] ` : '';
    
    if (error instanceof TypeError) {
      return `${prefix}Invalid input: ${error.message}`;
    } else if (error instanceof RangeError) {
      return `${prefix}Value out of range: ${error.message}`;
    } else if (error.name === 'QuotaExceededError') {
      return `${prefix}Not enough memory. Try fewer/smaller images.`;
    } else {
      return `${prefix}Error: ${error.message}`;
    }
  }
}

// Usage
try {
  await this.processImages();
} catch (error) {
  ErrorHandler.handle(error, this.terminal, 'Image Merger');
}
```

### Performance Optimization

**1. Image Loading:**
```javascript
// Use object URLs instead of data URLs for large images
const objectURL = URL.createObjectURL(file);
img.src = objectURL;
// Don't forget to revoke when done
URL.revokeObjectURL(objectURL);
```

**2. Canvas Operations:**
```javascript
// Offscreen canvas for heavy operations
const offscreen = new OffscreenCanvas(width, height);
const ctx = offscreen.getContext('2d', { willReadFrequently: true });
```

**3. Web Workers (for batch processing):**
```javascript
// worker.js
self.onmessage = async (e) => {
  const { images, operation } = e.data;
  const results = await processBatch(images, operation);
  self.postMessage({ results });
};

// main.js
const worker = new Worker('worker.js');
worker.postMessage({ images, operation: 'resize' });
worker.onmessage = (e) => {
  handleResults(e.data.results);
};
```

### Testing Strategy

**Manual Testing Checklist:**
- [ ] Drag-drop works for 1, 5, 20+ images
- [ ] File type validation (reject non-images)
- [ ] Large file handling (10MB+ images)
- [ ] Browser compatibility (Chrome, Firefox, Safari)
- [ ] Mobile responsive (if applicable)
- [ ] Keyboard shortcuts work
- [ ] Export/download functions correctly
- [ ] Metadata preservation verified

**Test Images:**
- Small (100×100px)
- Large (4000×4000px)
- Various formats (PNG, JPG, WEBP)
- With metadata (ComfyUI, EXIF)
- Without metadata
- Corrupted/malformed

### Deployment Checklist

**GitHub Pages Setup:**
1. Push to `main` branch
2. Enable Pages: Settings → Pages → Source: `main` branch
3. Custom domain (optional): Add CNAME file
4. HTTPS: Automatic via GitHub

**Optimization Before Deploy:**
- [ ] Minify CSS/JS (optional, may skip for dev tool)
- [ ] Optimize images (icons, backgrounds)
- [ ] Remove console.log() statements
- [ ] Add analytics (optional, privacy-focused: Plausible)
- [ ] Test on GitHub Pages preview URL

**Documentation:**
- README.md with tool descriptions
- Quick start guide
- Keyboard shortcuts reference
- Privacy policy (if collecting any data)

## Success Criteria

**Phase 1 (MVP):**
- [ ] Metadata analyzer integrated seamlessly
- [ ] 3 core tools working: merge, grid, resize
- [ ] Consistent terminal UI across all tools
- [ ] Local file processing (no uploads)
- [ ] Export functionality for all tools

**Phase 2 (Feature Complete):**
- [ ] All 9 tools implemented
- [ ] Wildcard expander with JSON loading
- [ ] Metadata writer with template support
- [ ] Workflow visualizer rendering graphs
- [ ] Token counter with CLIP approximation

**Phase 3 (Polish):**
- [ ] Keyboard shortcuts (Ctrl+O open, Ctrl+E export, etc.)
- [ ] Dark/light theme toggle
- [ ] Responsive mobile layout (if desired)
- [ ] Tool presets (save/load configurations)
- [ ] Batch processing with queues

## Questions for Current Codebase Analysis

Please answer these after reviewing the existing BareBlocks code:

1. **What image loading pattern is currently used?** (FileReader API, createObjectURL, etc.)
2. **How is metadata currently displayed?** (HTML tables, JSON tree, custom formatting?)
3. **Are there existing CSS variables/themes?** (for color consistency)
4. **What error handling exists?** (try-catch, user-facing messages?)
5. **Is there any state management?** (or just procedural code?)
6. **What libraries are already included?** (versions matter for compatibility)
7. **How much code can be extracted to shared utilities?** (rough estimate)
8. **Is the terminal aesthetic already implemented?** (or needs to be built from scratch?)

## Implementation Priority

**Immediate (Week 1):**
1. Analyze existing code, extract to `lib/` structure
2. Build `image-processor.js` and `terminal.js` base classes
3. Implement Image Merger tool (simplest, tests file I/O)

**Short-term (Week 2-3):**
4. Grid Generator (builds on merger)
5. Batch Resizer (tests progress indicators)
6. Metadata Writer (integrates with existing reader)

**Medium-term (Week 4+):**
7. Watermark tool (more complex UI)
8. Format converter
9. Wildcard expander (unique feature)

**Long-term (Optional):**
10. Workflow visualizer (requires D3.js/Cytoscape)
11. Token counter (needs tokenizer library)
12. Advanced features (presets, batch queues)

---

**Final Note:** This is a personal tool first, public release second. Prioritize functionality and code quality over marketing polish. The terminal aesthetic and metadata focus already differentiate it from generic tools. Keep scope manageable and iterate based on personal usage.