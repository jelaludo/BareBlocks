# 🚀 BareBlocks - Quick Start Guide

## Running Locally

### Option 1: Interactive Menu (Recommended for Testing)
```bash
python run.py
```

This will show an interactive menu where you can:
- Run CLI tool
- Launch GUI
- Test with sample image
- View help

### Option 2: Direct Commands

#### CLI Tool
```bash
# Basic usage
python bareblocks-cli.py images/screenshot.png

# JSON output
python bareblocks-cli.py images/screenshot.png --format json

# Save to file
python bareblocks-cli.py images/screenshot.png --save metadata.json

# Open GPS location in maps (if available)
python bareblocks-cli.py photo.jpg --open-maps
```

#### GUI Tool
```bash
python bareblocks-gui.py
```

#### Web App (Client-Side)
```bash
python -m http.server 8000
# Open: http://localhost:8000/index.html
```

#### Other Tools
```bash
# Remove metadata from image
python bareblocks-remove.py image.jpg

# Create visualizations dashboard
python demo_visualizations.py
```

### Option 3: Quick Test Commands
```bash
# Test with sample image
python run.py test

# Run CLI interactively
python run.py cli

# Launch GUI
python run.py gui

# Show help
python run.py help
```

## Prerequisites

Make sure you have Python 3.8+ and all dependencies installed:

```bash
pip install -r requirements.txt
```

## Testing

1. **Test CLI with sample image:**
   ```bash
   python bareblocks-cli.py images/screenshot.png
   ```

2. **Test JSON output:**
   ```bash
   python bareblocks-cli.py images/screenshot.png --format json
   ```

3. **Test GUI:**
   ```bash
   python bareblocks-gui.py
   ```

## Project Structure

- `bareblocks-cli.py` - Main CLI tool
- `bareblocks-gui.py` - Graphical interface
- `run.py` - Interactive development runner
- `core/` - Core metadata extraction modules
- `analysis/` - Statistical analysis
- `visualization/` - Visualization tools

## Next Steps

After testing locally, you can:
1. Create your GitHub repo
2. Enhance visuals (colorful CLI)
3. Implement layered parsing architecture

