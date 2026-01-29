# Metadata to Merger Integration Plan

## Concept
When you analyze an image in the **Metadata** tab, then switch to **Image Tools** and add that same image to the merger, the adjacent empty cell should automatically display a summary of the image's metadata.

## Use Cases
1. **AI Art Documentation**: Show model name, prompt, settings alongside generated images
2. **Photo Collections**: Display camera, lens, location info next to photos
3. **Before/After Comparisons**: Image + its metadata in grid format
4. **Art Portfolios**: Artwork + generation parameters
5. **Dataset Visualization**: Images with their technical specs

## Technical Architecture

### 1. Data Storage
```javascript
// Global metadata cache
let imageMetadataCache = new Map(); // key: filename, value: metadata object

// Enhanced mergeItem structure
{
    type: 'image',
    file: file,
    dataUrl: '...',
    img: img,
    width: 640,
    height: 480,
    metadata: { /* cached metadata */ },
    text: {
        content: 'Generated text from metadata',
        // ... other text properties
    }
}
```

### 2. Metadata Extraction Flow

**Step 1: Analyze in Metadata Tab**
- User uploads image to Metadata tab
- `extractMetadata()` runs and generates full metadata object
- Store in cache: `imageMetadataCache.set(file.name, metadata)`

**Step 2: Add to Image Merger**
- User switches to Image Tools tab
- Uploads same image (or different image)
- Check cache: `const cachedMetadata = imageMetadataCache.get(file.name)`
- If found, attach to mergeItem
- Generate summary text from metadata

**Step 3: Generate Summary Text**
```javascript
function generateMetadataSummary(metadata) {
    let summary = [];
    
    // AI Metadata (Priority 1)
    if (metadata.aiMetadata?.hasComfyUI) {
        if (metadata.aiMetadata.model) {
            summary.push(`Model: ${metadata.aiMetadata.model}`);
        }
        if (metadata.aiMetadata.resolvedPrompt) {
            const prompt = metadata.aiMetadata.resolvedPrompt.substring(0, 80) + '...';
            summary.push(`Prompt: ${prompt}`);
        }
        if (metadata.aiMetadata.sampler) {
            summary.push(`Sampler: ${metadata.aiMetadata.sampler}`);
        }
        if (metadata.aiMetadata.steps) {
            summary.push(`Steps: ${metadata.aiMetadata.steps}`);
        }
        if (metadata.aiMetadata.cfgScale) {
            summary.push(`CFG: ${metadata.aiMetadata.cfgScale}`);
        }
    }
    
    // Camera Metadata (Priority 2)
    else if (metadata.exif) {
        const camera = [metadata.exif.Make, metadata.exif.Model].filter(Boolean).join(' ');
        if (camera) summary.push(`Camera: ${camera}`);
        
        if (metadata.exif.LensModel) {
            summary.push(`Lens: ${metadata.exif.LensModel}`);
        }
        if (metadata.exif.FNumber) {
            summary.push(`f/${metadata.exif.FNumber}`);
        }
        if (metadata.exif.ExposureTime) {
            const exposure = metadata.exif.ExposureTime < 1 
                ? `1/${Math.round(1/metadata.exif.ExposureTime)}s`
                : `${metadata.exif.ExposureTime}s`;
            summary.push(exposure);
        }
        if (metadata.exif.ISO || metadata.exif.ISOSpeedRatings) {
            summary.push(`ISO ${metadata.exif.ISO || metadata.exif.ISOSpeedRatings}`);
        }
    }
    
    // Basic File Info (Priority 3)
    const width = metadata.exif?.ImageWidth || metadata.width || '?';
    const height = metadata.exif?.ImageLength || metadata.height || '?';
    summary.push(`${width}×${height}`);
    
    const sizeMB = (metadata.fileSize / 1024 / 1024).toFixed(2);
    summary.push(`${sizeMB} MB`);
    
    return summary.join('\n');
}
```

### 3. UI Integration Options

**Option A: Auto-populate on Empty Cell Creation**
```javascript
function rebuildMergeItems() {
    images.forEach((img, index) => {
        if (emptyCellPattern === 'after') {
            mergeItems.push({
                type: 'empty',
                color: emptyCellColor,
                text: {
                    content: img.metadata 
                        ? generateMetadataSummary(img.metadata)
                        : 'Text Here',
                    // ...
                }
            });
        }
        mergeItems.push(img);
    });
}
```

**Option B: Manual Trigger Button**
```
Text Overlay Section:
├── Text: [____________]
├── [📊 Import from Metadata] ← NEW BUTTON
```

**Option C: Dropdown Selector**
```
Text Source:
├── ( ) Manual Entry
└── (•) From Image Metadata
```

## Implementation Phases

### Phase 1: Basic Integration (1-2 hours)
1. ✅ Create `imageMetadataCache` Map
2. ✅ Store metadata when analyzing in Metadata tab
3. ✅ Retrieve and attach when adding to merger
4. ✅ Create `generateMetadataSummary()` function
5. ✅ Auto-populate empty cells with summary

### Phase 2: UI Enhancements (1 hour)
1. ✅ Add "Import from Metadata" button
2. ✅ Show cache status indicator (✓ if metadata available)
3. ✅ Option to manually refresh metadata
4. ✅ Template selector (AI, Camera, Basic)

### Phase 3: Advanced Features (2 hours)
1. ✅ Custom metadata templates
2. ✅ Metadata extraction in Image Tools tab (background)
3. ✅ Live preview of metadata summary
4. ✅ Copy metadata between cells

## Challenges & Solutions

### Challenge 1: File Identity
**Problem**: Same image uploaded twice has different `File` objects  
**Solution**: Use filename + filesize as composite key
```javascript
const cacheKey = `${file.name}_${file.size}`;
imageMetadataCache.set(cacheKey, metadata);
```

### Challenge 2: Metadata Extraction Performance
**Problem**: Extracting metadata is async and takes time  
**Solution**: 
- Extract in background when image added to merger
- Show "Loading..." placeholder
- Update text when extraction completes

### Challenge 3: Cross-Tab Communication
**Problem**: Metadata tab and Image Tools tab don't share state  
**Solution**: Use global `imageMetadataCache` Map that persists across tab switches

## Example Outputs

### AI Generated Image
```
Model: zImageBase_base.safetensors
Sampler: res_multistep
Steps: 30
CFG: 5
Prompt: A muscular gorilla kneeling in a...
1024×1024
2.48 MB
```

### Camera Photo
```
Camera: Canon EOS R6
Lens: EF50mm f/1.4 USM
f/1.4
1/200s
ISO 400
4000×3000
8.5 MB
```

### Basic File
```
PNG Image
1920×1080
1.23 MB
```

## Testing Checklist
- [ ] Analyze image in Metadata tab
- [ ] Switch to Image Tools
- [ ] Add same image
- [ ] Enable empty cells
- [ ] Verify empty cell shows metadata summary
- [ ] Test with AI image (ComfyUI)
- [ ] Test with camera photo (EXIF)
- [ ] Test with basic image (no metadata)
- [ ] Test manual edit overwrites summary
- [ ] Test cache persists across tab switches

## Success Criteria
1. Metadata summary appears automatically in empty cells
2. Summary is readable and informative
3. Works for AI, camera, and basic images
4. User can still manually edit/override
5. No performance impact on merger

---

**Next Steps:**
1. Implement Phase 1 (basic integration)
2. Test with various image types
3. Refine summary format based on feedback
4. Add Phase 2 UI enhancements if desired
