# TODO: Client-Side JavaScript Version Improvements

**Status**: Branch `feature/client-side-conversion` - NOT production ready
**Goal**: Match or exceed Python version's functionality while remaining client-side deployable

---

## Critical Issues to Fix

### 1. Missing Metadata Extraction
**Current**: Only extracting basic EXIF and some PNG chunks
**Need**: Full metadata extraction matching Python version

#### Missing Fields in Summary:
- `nonPixelBytes` - Calculate bytes used by metadata/chunks
- `nonPixelRatio` - Ratio of non-pixel data to total file size
- `Width` and `Height` - Separate fields (currently only "Dimensions")
- `Date Created` - From file metadata
- `hasExif` - Boolean flag
- `hasPayloads` - Boolean flag  
- `hasAiMetadata` - Boolean flag

**Python Reference**: `core/layered_inspector.py` - `phase_8_report_assembly()`

#### Missing Structure Section:
Currently showing nothing. Need to display:
- Full chunk array with details
- Each chunk: `{hasData, offset, size, type}`
- `format` - File format
- `nonPixelBytes` - Total metadata bytes
- `pixelDataBytes` - Image data bytes
- `totalChunks` - Count of chunks

**Implementation**: Parse PNG chunks more thoroughly, calculate pixel vs non-pixel data

---

### 2. Expandable/Collapsible Rows (The "+" Signs)

**Critical Missing Feature**: Python version has expandable rows for nested objects

#### How It Works in Python Version:
- Any object/array gets a `+` or `-` toggle
- Click to expand/collapse nested data
- Shows `[Object: N properties]` when collapsed
- Shows `[Array: N items]` when collapsed
- When expanded, shows all nested content indented

#### Example from Screenshot:
```
image_properties    [Object: 5 properties]  +  ← collapsed
```

When clicked, expands to:
```
image_properties    [Object: 5 properties]  -  ← expanded
    width           1088
    height          1488
    has_color_profile   true
    ...
```

**Implementation Needed**:
1. Detect nested objects/arrays during display
2. Create collapsible table rows
3. Add click handlers to toggle visibility
4. Indent nested content
5. Show property/item counts when collapsed

**Python Reference**: `bareblocks-web.py` - `createMetadataTableHTML()` function (~line 700-1000)

---

### 3. ComfyUI Workflow Data Extraction

#### What's Missing:
1. **Prompt not displaying** - Shows blank even though data exists
2. **Resolved Prompt not displaying** - Shows blank
3. **Wildcard Resolutions table** - Not showing individual resolutions
4. **Negative Prompt** - Not extracted or displayed
5. **All workflow node data** - Need to parse ALL node types

#### Specific Issues:
- Unicode encoding still broken in some cases (Eugène display)
- Wildcard count logic needs verification
- Not finding prompts in workflow nodes correctly
- Not matching original vs resolved prompts properly

**Python Reference**: `bareblocks-web.py` - `addComfyUISection()` function (~line 2501-2900)

#### Key Algorithm from Python Version:
```python
# 1. Find original prompt with wildcards (check multiple payload keywords)
# 2. Find resolved prompt (check prompt_resolved, workflow keyword)
# 3. Extract wildcards using regex: /__.*?__/g
# 4. Compare original vs resolved to find resolutions
# 5. Display prompt, resolved prompt, wildcard table
# 6. Extract ALL node data: model, LoRA, sampler, steps, CFG, seed
```

---

### 4. Missing Sections Entirely

#### Anomalies Section
**Not implemented at all**

Should show:
- `fileSize` - Total bytes
- `flags` - Array of anomaly flags (e.g., `[custom_chunks_present]`)
- `nonPixelBytes` - Metadata size
- `nonPixelRatio` - Ratio
- `pixelDataBytes` - Image data size

**Python Reference**: `core/layered_inspector.py` - `phase_7_anomaly_heuristics()`

#### Encryption and AI Section (Separate from ComfyUI)
Currently combined, but Python version has both:
- ComfyUI Workflow section (if ComfyUI detected)
- Encryption and AI section (general AI metadata)

Should show:
- `aiMetadata` - Nested object
- `graphDetected` - Boolean
- `pgpSignatureDetected` - Boolean
- `resolvedPromptAvailable` - Boolean
- `tool` - String (e.g., "ComfyUI")
- `wildcardsPresent` - Boolean

#### Bottom-level Full Object Display
Python version shows the ENTIRE raw data structure at bottom:
- `aiMetadata` expandable
- `anomalies` expandable
- `metadata` expandable
- `payloads` expandable
- `structure` expandable
- `summary` expandable
- `uncertainties` array
- `warnings` array

**This is the most detailed view and is completely missing**

---

### 5. PNG Chunk Parsing Issues

#### Current Problems:
1. **iTXt chunks** - Complex structure not fully parsed
   - Format: keyword, null, compression flag, compression method, language tag, null, translated keyword, null, text
   - Current code attempts this but may have offset errors

2. **zTXt chunks** - Compressed text chunks
   - Need to decompress using pako.js or similar
   - Currently trying to decode without decompression (will fail)

3. **Chunk data extraction**
   - Not capturing all chunk metadata
   - Need: offset, size, type, CRC, hasData flag

**Solution**: 
- Add pako.js for zlib decompression
- Fix iTXt parsing offsets
- Store complete chunk metadata

**Reference**: Look at how Python's PIL handles PNG chunks

---

### 6. Metadata Table Display Logic

#### Need to Replicate Python's `createMetadataTableHTML()`:

**Features Required**:
1. **Nested object detection** - Recursively process objects/arrays
2. **Collapsible rows** - With `+`/`-` toggles
3. **Indentation** - Nested items indented with padding-left
4. **Type indicators** - `[Object: N properties]`, `[Array: N items]`
5. **Smart display** - Some fields expanded by default (like EXIF)
6. **Category grouping** - Group related metadata

**Current Implementation**: 
- Flat display only
- No nesting support
- No collapsing
- Very limited

**Python Code Location**: `bareblocks-web.py` lines ~700-1000

---

### 7. Data Recap Section

#### What It Is:
The compact list showing "found" or "not found" for various metadata types

Example:
```
Camera data: not found  Geo data: not found  EXIF: found  
IPTC: not found  XMP: not found  ComfyUI workflow JSON: found
LoRA config JSON: found  ...
```

#### Current Status: 
**Not implemented in client-side version**

#### Need:
- Check for presence of each metadata type
- Display compact list
- Make "found" items clickable (scroll to section)
- Color code (green for found, red for not found)

**Python Reference**: `bareblocks-web.py` - `addDataRecap()` function (~line 2244-2434)

---

## Architecture Issues

### Current Architecture (Simplified):
```
File Upload → Parse with exifr → Display basic data
```

### Needed Architecture (Matching Python):
```
File Upload
  ↓
Phase 1: File Intake
  ↓
Phase 2: Container Identification  
  ↓
Phase 3: Structural Enumeration (parse ALL chunks/segments)
  ↓
Phase 4: Declared Metadata Extraction (EXIF, IPTC, XMP, ICC)
  ↓
Phase 5: Opaque Payload Detection (JSON, text, binary data)
  ↓
Phase 6: AI Pattern Recognition (ComfyUI, SD, wildcards)
  ↓
Phase 7: Anomaly Heuristics (size analysis, ratios)
  ↓
Phase 8: Report Assembly (organize all data)
  ↓
Display with expandable sections
```

**Python Reference**: `core/layered_inspector.py` - All `phase_X` methods

---

## Specific Code Files to Reference

### From Python Version:

1. **`bareblocks-web.py`** - Main web interface
   - Lines 700-1000: `createMetadataTableHTML()` - Nested object display
   - Lines 1800-1900: Toggle row functionality
   - Lines 2244-2434: `addDataRecap()` - Data recap section
   - Lines 2436-2499: `extractWildcards()` - Wildcard resolution
   - Lines 2501-2900: `addComfyUISection()` - ComfyUI display
   - Lines 1942-2174: `addProvenanceSummary()` - Provenance detection

2. **`core/layered_inspector.py`** - Core parsing logic
   - Phase 1-8 methods
   - PNG chunk parsing
   - JPEG segment parsing
   - Metadata extraction
   - AI pattern recognition

3. **`bareblocks_cli_web.py`** - Metadata extractor class
   - EXIF extraction
   - GPS conversion
   - File type detection

---

## JavaScript Libraries Needed

### Current:
- `exifr` - EXIF extraction ✅

### Need to Add:
1. **pako.js** - zlib decompression for zTXt chunks
   - CDN: `https://cdn.jsdelivr.net/npm/pako@2.1.0/dist/pako.min.js`
   - Usage: `pako.inflate(compressedData)`

2. **Consider exif-parser** - More control over EXIF
   - May be better than exifr for detailed extraction

---

## Display Issues

### 1. Unicode Handling
- Still showing `\u00e8` instead of `è` in some places
- Need comprehensive Unicode decode function
- Apply to ALL text display, not just some fields

### 2. Copy Buttons
- Using `[ ]` but should show `[✓]` feedback
- Should handle all text types (including multiline)
- Base64 encoding should work for ALL special characters

### 3. Mobile Responsiveness
**Current**: Basic media queries
**Need**:
- Touch-friendly toggles (bigger + buttons)
- Horizontal scroll for wide tables
- Collapsible sections by default on mobile
- Larger fonts for readability
- Better spacing
- Test on actual devices (iPhone, Android)

### 4. Section Highlighting
**Python version has**: Click "found" → scroll + highlight section
**Client version**: Not implemented

---

## Testing Requirements

### Test Files Needed:
1. **PNG with ComfyUI workflow** (with wildcards) ✅
2. **PNG with ComfyUI workflow** (without wildcards)
3. **JPEG with EXIF** (camera photo)
4. **PNG with compressed zTXt chunks**
5. **PNG with iTXt chunks** (international text)
6. **Image with GPS data**
7. **Image with IPTC/XMP metadata**
8. **Large file** (>10MB) - test performance
9. **Various ComfyUI node types** - ensure all extracted

### Test on Browsers:
- [ ] Chrome Desktop
- [ ] Firefox Desktop
- [ ] Safari Desktop
- [ ] Safari iOS
- [ ] Chrome Android
- [ ] Samsung Internet

### Test on Devices:
- [ ] iPhone SE (small screen)
- [ ] iPhone 13 (standard)
- [ ] iPad (tablet)
- [ ] Android phone
- [ ] Desktop 4K monitor

---

## Implementation Priority

### Phase 1: Core Functionality (Must Have)
1. **Fix PNG text chunk parsing** - Properly extract all text from iTXt, zTXt
2. **Fix ComfyUI data extraction** - Get all workflow data
3. **Fix wildcard resolution** - Proper counting and matching
4. **Fix Unicode display** - No more escape sequences

### Phase 2: Data Display (Must Have)
1. **Implement expandable rows** - The `+`/`-` toggle system
2. **Add Structure section** - Show chunk details
3. **Add Anomalies section** - File analysis
4. **Add Data Recap** - Compact found/not found list
5. **Add full object display** - Bottom section with all raw data

### Phase 3: Polish (Should Have)
1. **Mobile optimization** - Better responsive design
2. **Section highlighting** - Clickable navigation
3. **Better copy functionality** - All text copyable
4. **Loading indicators** - Show progress for large files
5. **Error handling** - Graceful failures

### Phase 4: Enhancement (Nice to Have)
1. **Chunk visualization** - Interactive heatmap
2. **JSON export** - Matching Python output exactly
3. **Comparison mode** - Compare two images
4. **Batch processing** - Multiple files
5. **PWA support** - Installable app

---

## Key Algorithms to Port

### 1. Wildcard Extraction (Python → JavaScript)
```python
# Python version (lines 2436-2499)
def extractWildcards(originalPrompt, resolvedPrompt):
    wildcards = []
    wildcardPattern = /__([^_]+)__/g
    # Find each wildcard position
    # Extract text before/after wildcard
    # Find corresponding text in resolved prompt
    # Extract resolved value between before/after markers
    return wildcards
```

**Status**: Partially implemented, needs debugging

### 2. Nested Object Display (Python → JavaScript)
```python
# Python version (lines 700-1000)
def createMetadataTableHTML(data, indent=0):
    for key, value in data.items():
        if isinstance(value, dict):
            # Show [Object: N properties] with toggle
            # Recursively display nested content
        elif isinstance(value, list):
            # Show [Array: N items] with toggle
            # Display each item
        else:
            # Display simple value
```

**Status**: Not implemented

### 3. PNG Chunk Parser (Python → JavaScript)
```python
# Python version uses PIL, need pure JS
def parsePngChunks(arrayBuffer):
    # Read signature (8 bytes)
    # Loop through chunks:
    #   - Read length (4 bytes)
    #   - Read type (4 bytes)
    #   - Read data (length bytes)
    #   - Read CRC (4 bytes)
    #   - Store: {type, length, offset, data, crc}
    # Return array of chunks
```

**Status**: Basic implementation exists, needs enhancement

---

## Known Bugs

1. **Unicode not displaying** - `Eugène` shows as `Eug\u00e8ne`
2. **Wildcard count wrong** - Shows 0 when should be 3
3. **Model not extracted** - Shows "Unknown" when it's in workflow
4. **Prompt not displaying** - Blank even though data exists
5. **Resolved prompt not displaying** - Blank even though data exists
6. **No expandable rows** - Can't drill into nested data
7. **No Structure section** - Missing entirely
8. **No Anomalies section** - Missing entirely
9. **No Data Recap** - Missing entirely
10. **Missing bottom raw data display** - Can't see full object

---

## Performance Considerations

### Current Performance:
- ✅ Fast for small files (<5MB)
- ❓ Unknown for large files (>10MB)
- ❓ Unknown for complex workflows (>50 nodes)

### Optimization Needed:
1. **Lazy loading** - Don't display all data at once
2. **Virtual scrolling** - For large tables
3. **Web Workers** - Parse files in background thread
4. **Progressive rendering** - Show sections as they're ready
5. **Caching** - Cache parsed data to avoid re-parsing

---

## Deployment Readiness

### Blockers for Production:
- [ ] Fix all "Known Bugs" above
- [ ] Implement expandable rows (critical for usability)
- [ ] Add missing sections (Structure, Anomalies, etc.)
- [ ] Mobile testing on real devices
- [ ] Performance testing with large files

### Current State:
**❌ NOT READY** - Missing too much functionality

### When Ready:
1. Test thoroughly with all test files
2. Deploy to Cloudflare Pages
3. Add to jelaludo.com navigation
4. Monitor for errors
5. Collect user feedback

---

## References

### Python Version Files:
- `bareblocks-web.py` - Main web interface (3,544 lines)
- `core/layered_inspector.py` - Core parsing (870 lines)
- `bareblocks_cli_web.py` - Metadata extractor (308 lines)

### Current JavaScript Version:
- `index.html` - Complete standalone app (~1,000 lines)

### Documentation Created:
- `CLIENT_SIDE_CONVERSION_PLAN.md` - Original analysis
- `CONVERSION_SUMMARY.md` - What was done
- `README_CLIENT_SIDE.md` - Usage guide
- `DEPLOYMENT.md` - Deployment instructions
- **`TODO_CLIENT_SIDE_IMPROVEMENTS.md`** - This file

---

## Next Session Action Plan

### Start Here:
1. **Read this entire TODO document**
2. **Open `bareblocks-web.py`** - Study the `createMetadataTableHTML()` function
3. **Test Python version** - Run it on the same test image to see exact output
4. **Implement expandable rows** - This is the biggest missing feature
5. **Fix wildcard extraction** - Port the exact Python logic
6. **Add missing sections** - Structure, Anomalies, Data Recap
7. **Test, test, test** - Use the same test images for both versions

### Code to Write First:
```javascript
// 1. Expandable row system
function createNestedTableRows(data, indent = 0) {
    // Detect objects/arrays
    // Create toggle buttons
    // Return HTML with collapsible rows
}

// 2. Complete PNG chunk parser
function parsePngChunksComplete(arrayBuffer) {
    // Extract ALL chunk data
    // Calculate pixel vs non-pixel bytes
    // Return detailed chunk array
}

// 3. Fix wildcard extraction
function extractWildcardsFixed(original, resolved) {
    // Use exact Python algorithm
    // Handle all edge cases
    // Return array of {name, resolved} objects
}
```

---

## Questions to Answer

1. **Can we match Python's functionality 100% in JavaScript?**
   - Answer: Yes, but need proper implementation

2. **Performance concerns with large files?**
   - Answer: Need Web Workers for background processing

3. **Can exifr extract everything we need?**
   - Answer: Maybe, or add custom parsers

4. **How to handle zlib compression in browser?**
   - Answer: Use pako.js library

5. **Mobile performance acceptable?**
   - Answer: TBD, need testing

---

## Success Criteria

### When is it "done"?

1. ✅ **Feature Parity**: All sections from Python version present
2. ✅ **Data Accuracy**: Extracts same data as Python version
3. ✅ **Display Quality**: Expandable rows, proper formatting
4. ✅ **Mobile Ready**: Works smoothly on phones/tablets
5. ✅ **Performance**: <2 seconds for typical image analysis
6. ✅ **No Bugs**: All "Known Bugs" fixed
7. ✅ **Tested**: All test files pass, all browsers work
8. ✅ **Deployed**: Live on Cloudflare Pages, linked from jelaludo.com

---

**Status**: Branch `feature/client-side-conversion`
**Last Updated**: 2026-01-04
**Next Review**: When user returns

**Priority**: Get expandable rows working first - this is the key to matching Python's UI

