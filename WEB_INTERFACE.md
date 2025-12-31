# 🌐 BareBlocks Web Interface

## Browser-Based Terminal Interface

BareBlocks now includes a **web-based terminal interface** that runs on `localhost:5000` and looks like a CLI terminal in your browser!

## Quick Start

### Option 1: Using run.py (Recommended)
```bash
python run.py web
```

Or from the interactive menu:
```bash
python run.py
# Then select option 2
```

### Option 2: Direct Command
```bash
python bareblocks-web.py
```

## What You'll See

1. **Terminal-style interface** in your browser
2. **Dark theme** with syntax highlighting
3. **Drag & drop** file upload
4. **Real-time metadata extraction**
5. **Formatted output** with tables and JSON

## Features

- ✅ Terminal aesthetic (looks like a real CLI)
- ✅ Drag & drop file upload
- ✅ Click to browse files
- ✅ Real-time metadata display
- ✅ JSON output option
- ✅ Responsive design
- ✅ Dark theme

## Access

Once started, the server will:
- Run on `http://localhost:5000`
- Automatically open your browser
- Show a terminal-style interface

## Usage

1. **Start the server:**
   ```bash
   python run.py web
   ```

2. **Browser opens automatically** (or go to http://localhost:5000)

3. **Upload a file:**
   - Click the upload area, OR
   - Drag & drop a file

4. **View metadata:**
   - See formatted table output
   - View JSON representation
   - All in terminal style!

## Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

## Troubleshooting

### Port already in use?
Change the port in `bareblocks-web.py`:
```python
port = 5001  # or any other port
```

### Browser doesn't open?
Manually navigate to: `http://localhost:5000`

### Import errors?
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Next Steps

This web interface is the foundation for:
- Enhanced visual styling
- Layered parsing architecture
- Interactive metadata exploration
- Educational tooltips

