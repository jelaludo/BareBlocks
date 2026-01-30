# 🧪 Local Testing Guide

## Quick Start

### Option 1: Interactive Menu (Easiest)
```bash
python run.py
```

This opens an interactive menu where you can:
1. Run CLI tool with any file
2. Launch GUI
3. Test with sample image
4. View help
5. Exit

### Option 2: Direct Commands

#### Test CLI with sample image:
```bash
python run.py test
```

#### Run CLI interactively:
```bash
python run.py cli
```

#### Launch GUI:
```bash
python run.py gui
```

#### Show help:
```bash
python run.py help
```

### Option 3: Direct Python Commands

#### CLI Tool
```bash
# Basic usage
python bareblocks-cli.py images/screenshot.png

# JSON output
python bareblocks-cli.py images/screenshot.png --format json

# Save to file
python bareblocks-cli.py images/screenshot.png --save metadata.json

# Help
python bareblocks-cli.py --help
```

#### GUI Tool
```bash
python bareblocks-gui.py
```

#### Web App (Client-Side)
```bash
python -m http.server 8080
# Open: http://localhost:8080/index.html
```

## What to Test

1. ✅ **CLI Basic Functionality**
   ```bash
   python bareblocks-cli.py images/screenshot.png
   ```

2. ✅ **JSON Output**
   ```bash
   python bareblocks-cli.py images/screenshot.png --format json
   ```

3. ✅ **GUI Interface**
   ```bash
   python bareblocks-gui.py
   ```

4. ✅ **Help Command**
   ```bash
   python bareblocks-cli.py --help
   ```

## Expected Output

When you run the CLI, you should see:
- Rich formatted table with metadata
- File information (name, size, dates)
- Image properties (format, size, DPI)
- EXIF data (if present)
- GPS coordinates (if present)

## Troubleshooting

### If you get "ModuleNotFoundError":
```bash
pip install -r requirements.txt
```

### If you get encoding errors:
The `run.py` script handles Windows encoding automatically.

### If GUI doesn't open:
Make sure tkinter is installed (usually comes with Python):
```bash
python -c "import tkinter; print('tkinter OK')"
```

## Next Steps After Testing

Once everything works locally:
1. ✅ Create GitHub repo
2. ✅ Enhance visuals (colorful CLI)
3. ✅ Implement layered parsing architecture

