# Image Merger - Phase 2 Implementation Plan

## Overview
Adding text overlay and empty cell features to the Image Merger tool.

## Feature 1: Empty Cells

### Requirements
- Allow insertion of empty/blank cells in the merge grid
- Default: White background
- Customizable background color
- **Bonus**: Color picker with palette extracted from images

### UI Design
```
Settings Panel:
├── Grid Columns: [Slider]
└── Empty Cells
    ├── [ ] Include Empty Cells
    ├── Pattern: [Before Each | After Each | Custom]
    ├── Cell Color: [Color Picker]
    └── [Pick from Image] button (extracts palette)
```

### Implementation Details

**Empty Cell Logic:**
- Modify grid structure to support `{ type: 'image', data: ... }` or `{ type: 'empty', color: '#fff' }`
- Pattern options:
  - "Before Each": `[Empty] [Image] [Empty] [Image]`
  - "After Each": `[Image] [Empty] [Image] [Empty]`
  - "Custom": User manually adds empty cells (drag to reorder)

**Color Extraction:**
- Use Canvas `getImageData()` to extract dominant colors
- Algorithm: K-means clustering or simple histogram
- Display 5-6 color swatches to choose from
- Library option: Consider `color-thief.js` or `vibrant.js`

### Code Structure
```javascript
let mergeItems = []; // Array of {type: 'image'|'empty', data/color}
let emptyCellColor = '#ffffff';

function addEmptyCell() {
    mergeItems.push({ type: 'empty', color: emptyCellColor });
}

function extractImagePalette(imageData) {
    // Extract 5-6 dominant colors
    // Return array of hex colors
}
```

---

## Feature 2: Text Overlay (Per Cell)

### Requirements
- Add text to individual cells (not just entire merged image)
- Web-safe fonts: Arial, Georgia, Courier, Times New Roman, Verdana
- Position presets: Center (default), Top, Bottom, Left, Right
- Each cell can have its own text with individual styling

### UI Design
```
Per-Cell Text Settings:
├── Selected Cell: [Dropdown - Image 1, Image 2, Empty 1, etc.]
├── Text: [Input field]
├── Font: [Dropdown - Arial, Georgia, etc.]
├── Size: [Slider: 12-120px]
├── Color: [Color Picker]
├── Position: [Buttons: Top | Center | Bottom | Left | Right]
└── Opacity: [Slider: 0-100%]
```

**Alternative UI (More intuitive):**
- Click on a cell in the preview to select it
- Text settings panel appears
- Visual indicator showing which cell is selected

### Web-Safe Fonts
```javascript
const fonts = [
    'Arial, sans-serif',
    'Georgia, serif',
    'Courier New, monospace',
    'Times New Roman, serif',
    'Verdana, sans-serif'
];
```

### Implementation Details

**Data Structure:**
```javascript
mergeItems = [
    {
        type: 'image',
        data: imageData,
        text: {
            content: 'My Text',
            font: 'Arial, sans-serif',
            size: 48,
            color: '#ffffff',
            position: 'center', // top, bottom, left, right, center
            opacity: 1.0
        }
    },
    {
        type: 'empty',
        color: '#ffffff',
        text: { ... } // Empty cells can also have text
    }
];
```

**Text Rendering on Canvas:**
```javascript
function drawTextOnCell(ctx, x, y, cellWidth, cellHeight, textConfig) {
    if (!textConfig || !textConfig.content) return;
    
    ctx.save();
    ctx.font = `${textConfig.size}px ${textConfig.font}`;
    ctx.fillStyle = textConfig.color;
    ctx.globalAlpha = textConfig.opacity;
    
    // Calculate position
    const metrics = ctx.measureText(textConfig.content);
    let textX, textY;
    
    switch(textConfig.position) {
        case 'top':
            textX = x + cellWidth / 2;
            textY = y + textConfig.size + 10;
            break;
        case 'center':
            textX = x + cellWidth / 2;
            textY = y + cellHeight / 2 + textConfig.size / 3;
            break;
        case 'bottom':
            textX = x + cellWidth / 2;
            textY = y + cellHeight - 10;
            break;
        // ... left, right
    }
    
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(textConfig.content, textX, textY);
    ctx.restore();
}
```

**Text Stroke/Outline (Optional Enhancement):**
```javascript
// Add text stroke for better visibility on varied backgrounds
ctx.strokeStyle = '#000000';
ctx.lineWidth = 2;
ctx.strokeText(textConfig.content, textX, textY);
ctx.fillText(textConfig.content, textX, textY);
```

---

## Implementation Phases

### Phase 2.1: Empty Cells (MVP)
1. ✅ Add "Include Empty Cells" checkbox
2. ✅ Pattern selector (Before Each / After Each)
3. ✅ Color picker for empty cell background
4. ✅ Update preview to show empty cells
5. ✅ Update download to render empty cells

### Phase 2.2: Text Overlay (MVP)
1. ✅ Add text input per cell
2. ✅ Font family selector (5 web-safe fonts)
3. ✅ Font size slider
4. ✅ Color picker
5. ✅ Position presets (Center default)
6. ✅ Opacity slider
7. ✅ Cell selection UI (click to select or dropdown)
8. ✅ Update preview to show text
9. ✅ Update download to render text on canvas

### Phase 2.3: Color Extraction (Enhancement)
1. ✅ "Pick from Image" button
2. ✅ Extract dominant colors from selected image
3. ✅ Display color palette swatches
4. ✅ Apply selected color to empty cells or text

### Phase 2.4: Advanced Features (Future)
- Text stroke/outline
- Text shadow
- Text rotation
- Multiple text layers per cell
- Drag-and-drop text positioning
- Custom fonts (upload .ttf/.woff)
- Text presets/templates

---

## UI Layout Proposal

```
┌─────────────────────────────────────────────────────────────┐
│ Settings                                                     │
├─────────────────────────────────────────────────────────────┤
│ Merge Direction: [→ Horizontal] [↓ Vertical] [⊞ Grid]      │
│ Grid Columns: 2 [slider]                                    │
│                                                              │
│ Image Fit: [Cover] [Contain] [Fill] [Scale Down]           │
│                                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Empty Cells                                             │ │
│ │ [✓] Include Empty Cells                                 │ │
│ │ Pattern: [Before Each ▼]                                │ │
│ │ Cell Color: [⬜ #ffffff] [Pick from Image]              │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Text Overlay                                            │ │
│ │ Selected Cell: [Image 1 ▼]                              │ │
│ │ Text: [___________________________________]              │ │
│ │ Font: [Arial ▼] Size: 48px [slider]                    │ │
│ │ Color: [⬜ #ffffff]                                      │ │
│ │ Position: [Top] [Center*] [Bottom] [Left] [Right]      │ │
│ │ Opacity: 100% [slider]                                  │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Testing Checklist

- [ ] Empty cells render correctly in preview
- [ ] Empty cells appear in final download
- [ ] Color picker updates empty cell color
- [ ] Text displays on correct cell
- [ ] Text position presets work (all 5)
- [ ] Font family changes work
- [ ] Font size scales correctly
- [ ] Text color changes work
- [ ] Text opacity works
- [ ] Multiple cells can have different text
- [ ] Text renders correctly in final download
- [ ] Preview matches final output (WYSIWYG)

---

## Dependencies

None required - using native Canvas API for all features.

Optional enhancements:
- `vibrant.js` or `color-thief.js` for better color extraction
- `opentype.js` for custom font support (future)

---

## Success Criteria

1. User can add empty cells to break up image layouts
2. User can customize empty cell colors
3. User can add text to any cell (image or empty)
4. Text positioning works with 5 presets
5. Preview accurately shows final output
6. Export includes all text and formatting

---

**Estimated Implementation Time:** 4-6 hours
- Empty Cells: 1-2 hours
- Text Overlay: 2-3 hours  
- Testing & Polish: 1 hour
