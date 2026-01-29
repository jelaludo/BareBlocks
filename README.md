# 📸 BareBlocks - Comprehensive Metadata Tool  

how to run from cursor : python run.py web

<p align="center">
  <img src="images/ExIF-Logo_BackgroundWhite.png" alt="GUI Screenshot" width="200">
</p>

## 🔎 Overview  
**BareBlocks** is a powerful metadata extraction and management tool that supports multiple file types including **images, videos, audio, and documents**.  
It provides:  
- 🖥️ A **modern GUI** for beginners  
- 💻 A **command-line interface (CLI)** for advanced users  

Use BareBlocks to **extract, analyze, edit, and remove metadata** with ease.  

---

## 🖼️ GUI Screenshots  

### Main Interface  
<p align="center">
  <img src="images/screenshot.png" alt="BareBlocks GUI Main Interface" width="800">
</p>

### Document Metadata View  
<p align="center">
  <img src="images/screenshot_pdf.png" alt="BareBlocks GUI PDF Metadata" width="800">
</p>

---

## 🚀 Features  

### Image Support  
- Extract EXIF data (camera model, ISO, shutter speed, etc.)  
- View image properties (dimensions, color profile, format)  
- Extract GPS data & view location on Google Maps  
- Remove metadata for privacy  

### Video Support  
- Extract video metadata (codec, duration, resolution, frame rate)  
- Get audio stream details  
- View technical specifications  

### Audio Support  
- Extract ID3 tags (artist, album, track)  
- View bitrate, sample rate, channels  
- Manage audio properties  

### Document Support  
- Extract metadata from **PDF, DOCX, TXT**  
- Read author, title, creation/modification dates  

### Location Features  
- Generate Google Maps links from GPS metadata  
- View exact file location in browser  

---

## 📂 Supported File Formats  

| Category   | Formats |
|------------|---------|
| **Images** | JPG, JPEG, PNG, GIF, BMP, TIFF |
| **Videos** | MP4, AVI, MOV, MKV |
| **Audio**  | MP3, WAV, FLAC |
| **Docs**   | PDF, DOC/DOCX, TXT |

### 📊 Visualization Dashboard (NEW!)
- **Interactive visualizations** of metadata across multiple files
- **Dark mode dashboard** with Power BI-style layout
- **7+ chart types**: pie charts, bar charts, timelines, scatter plots, histograms, box plots
- **Statistical analysis**: file type distribution, camera usage, ISO/aperture patterns, resolution analysis
- **Export options**: View charts in browser, save as HTML
- **Fully interactive**: Hover for details, zoom, pan, and more

## Installation
---

## ⚡ Installation  

### Prerequisites  
- Python **3.8+**  
- Install dependencies:  
```bash
pip install -r requirements.txt
```

### Quick Setup
Run the automated setup script:
```bash
bash setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up the project structure
- Configure the environment

### GUI Application
1. Clone the repository:
### GUI Application  
```bash
git clone https://github.com/AryanVBW/BareBlocks.git
cd BareBlocks
python bareblocks-gui.py
```

### CLI Tool  
```bash
git clone https://github.com/AryanVBW/BareBlocks.git
cd BareBlocks
python bareblocks-cli.py path/to/file
```

---

## 🛠️ Usage Examples  

### Extract metadata from image  
```bash
python bareblocks-cli.py photo.jpg
```

### 📊 Visualization Dashboard

#### Quick Test (Sample Data)
Run a quick test with automatically generated sample data:
```bash
python test_visualizations.py
```
This will:
- Generate 150 sample files with realistic metadata
- Create 7 interactive visualizations
- Open the dashboard in your browser
- Save charts to `exports/test_visualizations/`

#### Full Demo (Your Files)
Process your actual media files and create visualizations:
```bash
python demo_visualizations.py
```
This will:
- Scan your `media/` directory for files
- Extract metadata from all supported file types
- Perform statistical analysis
- Generate comprehensive visualizations
- Create an interactive dashboard
- Save to `exports/` directory

#### Dashboard Features
The visualization dashboard includes:
- **File Types**: Pie chart showing file type distribution
- **Camera Models**: Bar chart of most-used cameras
- **Timeline**: Line chart of files over time
- **File Sizes**: Histogram with size distribution
- **Resolution**: Scatter plot of image dimensions
- **ISO Settings**: Distribution of ISO values
- **Aperture**: Box plot of aperture settings by camera

All charts are **fully interactive**:
- Hover to see detailed information
- Click and drag to zoom into specific areas
- Double-click to reset the view
- Use toolbar to save charts as PNG
- Click "⤢" icon to open chart in new tab

## Supported File Types

### Images
- JPG/JPEG
- PNG
- GIF
- BMP
- TIFF

### Videos
- MP4
- AVI
- MOV
- MKV

### Audio
- MP3
- WAV
- FLAC

### Documents
- PDF
- DOC/DOCX
- TXT

## Requirements

### Core Dependencies
- Python 3.8+
- Pillow
- exifread
- moviepy
- eyed3
- python-magic
- ffmpeg
- pdfplumber
- python-docx
- mutagen
- rich

### Visualization Dependencies
- plotly (5.11+) - Interactive charts
- pandas - Data manipulation
- numpy - Numerical operations
- matplotlib - Static visualizations
- seaborn - Statistical graphics

### Installation
All dependencies can be installed with:
```bash
pip install -r requirements.txt
pip install -r requirements-dashboard.txt
```

Or use the automated setup:
```bash
bash setup.sh
```

## Project Structure

```
BareBlocks/
├── bareblocks-gui.py        # GUI application (tkinter-based)
├── bareblocks-cli.py         # Command-line interface tool
├── bareblocks-main.py       # Main CLI script
├── bareblocks.py            # Terminal output version
├── bareblocks-remove.py     # Remove EXIF data from images
├── bareblocks-cdv.py        # CSV export version
├── test_visualizations.py   # Quick test with sample data
├── demo_visualizations.py   # Full demo with your files
├── setup.sh                 # Automated setup script
├── requirements.txt         # Core dependencies
├── requirements-dashboard.txt # Visualization dependencies
├── core/                    # Core modules
│   ├── data_models.py       # Data structures (Pydantic models)
│   ├── metadata_aggregator.py # Batch processing & extraction
│   └── data_storage.py      # SQLite database operations
├── analysis/                # Analysis modules
│   └── statistical_analyzer.py # Statistical analysis
├── visualization/           # Visualization modules
│   └── visualizer.py        # Chart generation (Plotly)
├── exports/                 # Generated visualizations
├── media/                   # Your media files (for processing)
└── data/                    # Database storage
```

## Usage Examples

### Extract Metadata from Single File
```bash
python bareblocks-cli.py photo.jpg
```

### Process Multiple Files
```bash
python demo_visualizations.py
```

### View in GUI
```bash
python bareblocks-gui.py
```

### Quick Visualization Test
```bash
python test_visualizations.py
```

## Dashboard Screenshots
The visualization dashboard provides a modern, dark-mode interface similar to Power BI:
- All charts visible at once (no scrolling)
- 4x2 grid layout on desktop
- Fully responsive design
- Interactive tooltips and zoom
- Professional dark theme

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Credits
Created by AryanVBW

## Features
- Extract exif data of images jpg, jpeg, png.
- Clear exif data of images.
- Save data in a text file.
- Modern GUI application for easy metadata extraction.
- Support for multiple file types including images, videos, and audio.
## Supported Formats
 - Images:
     - PNG, JPG, JPEG, GIF, BMP, TIFF
 - **Videos** :
     - MP4, MKV, AVI, MOV
 - **Audio** :
     - MP3 (limited support, additional library may be required)
 - OutputThe script will display metadata information for each file.If the output is set to a file, the results will be saved in exif_data.txt.
## Installation and usage instructions:

### Command Line Usage
- Add .jpg to subfolder ./images from where the script is stored. 
- Note: Most social media sites strip exif data from uploaded photos.

### GUI Application Usage
1. Install the required dependencies:
### Save metadata to JSON  
```bash
python bareblocks-cli.py video.mp4 --format json --save metadata.json
```

### Remove EXIF data from image  
```bash
python bareblocks-remove.py image.jpg
```

### Auto-open GPS in Google Maps  
```bash
python bareblocks-cli.py photo.jpg --open-maps
```

### Batch process multiple files  
```bash
python bareblocks-cli.py *.jpg --format json
```

---

## 📖 Command Reference  

| Command | Description | Example |
|---------|-------------|---------|
| `--format json` | Export metadata in JSON format | `python bareblocks-cli.py file.jpg --format json` |
| `--save file.json` | Save metadata to file | `python bareblocks-cli.py file.mp4 --save meta.json` |
| `--open-maps` | Open GPS location in Google Maps | `python bareblocks-cli.py photo.jpg --open-maps` |
| `-all=` | Remove all metadata from file | `python bareblocks-remove.py file.jpg` |
| `-overwrite_original` | Overwrite files without backup | `python bareblocks-cli.py file.jpg -overwrite_original` |

---

## 🏷️ Metadata Fields Explained  

- **EXIF (Exchangeable Image File Format)** → Camera settings (aperture, shutter speed, ISO, flash, orientation)  
- **IPTC (International Press Telecommunications Council)** → Captions, copyright, creator, keywords  
- **XMP (Extensible Metadata Platform)** → Adobe fields (title, description, author, subject)  
- **GPS Metadata** → Latitude, longitude, altitude, timestamp  
- **Audio Tags (ID3, Vorbis, etc.)** → Artist, album, track number, genre  

---

## 🛑 Troubleshooting  

| Problem | Solution |
|---------|----------|
| `Permission denied` | Run with `sudo` on Linux/macOS |
| Backup files clutter folder (`_original`) | Use `-overwrite_original` flag |
| Missing metadata fields | Not all file formats support every tag |
| Garbled characters in output | Use UTF-8 encoding: `exiftool -charset UTF8 file.jpg` |
| GUI not starting | Ensure all dependencies from `requirements.txt` are installed |

---

## ❓ FAQ  

**Q1: Is BareBlocks safe to use?**  
✅ Yes, but always back up your files before modifying metadata.  

**Q2: Does BareBlocks overwrite files?**  
By default, backups are created. Use `-overwrite_original` to skip them.  

**Q3: Is it cross-platform?**  
Yes, works on **Windows, macOS, and Linux**.  

**Q4: Can BareBlocks handle videos and audio files?**  
Yes, basic metadata extraction is supported for video and audio formats.  

**Q5: How can I see all available metadata fields in a file?**  
Run:  
```bash
python bareblocks-cli.py file.jpg --format json
```

---

## 📜 License  
This project is licensed under the MIT License – see [LICENSE](LICENSE).  

---

## 👨‍💻 Credits  
- Developed by **AryanVBW**  
- Inspired by David Bombal’s [Exif script](https://github.com/davidbombal/red-python-scripts/blob/main/exif.py)  
- Thanks to the open-source community for contributions and testing  

---

