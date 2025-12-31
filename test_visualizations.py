#!/usr/bin/env python3
"""
Quick visualization test with sample data.
Run this to see visualizations without needing real files!
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("  Quick Visualization Test")
print("=" * 70)
print()

# Create sample data
print("Creating sample data...")
try:
    import pandas as pd
    import numpy as np
    
    np.random.seed(42)
    
    # Generate realistic sample metadata
    n_files = 150
    
    cameras = ['Canon EOS 5D Mark IV', 'Nikon D850', 'Sony A7III', 'iPhone 13 Pro', 'Canon EOS R5']
    file_types = ['image', 'video']
    
    data = pd.DataFrame({
        'file_name': [f'IMG_{i:04d}.jpg' for i in range(n_files)],
        'file_type': np.random.choice(file_types, n_files, p=[0.85, 0.15]),
        'file_size': np.random.randint(2_000_000, 25_000_000, n_files),
        'camera_make': np.random.choice(['Canon', 'Nikon', 'Sony', 'Apple'], n_files),
        'camera_model': np.random.choice(cameras, n_files),
        'iso': np.random.choice([100, 200, 400, 800, 1600, 3200], n_files),
        'aperture': np.random.choice([1.4, 1.8, 2.0, 2.8, 4.0, 5.6, 8.0], n_files),
        'focal_length': np.random.choice([24, 35, 50, 85, 135, 200], n_files),
        'width': np.random.choice([1920, 3840, 4000, 6000], n_files),
        'height': np.random.choice([1080, 2160, 3000, 4000], n_files),
        'created_date': pd.date_range('2023-01-01', periods=n_files, freq='D')
    })
    
    print(f"✓ Created sample dataset with {len(data)} files")
    print(f"  File types: {data['file_type'].value_counts().to_dict()}")
    print(f"  Cameras: {len(data['camera_model'].unique())} unique models")
    
except ImportError as e:
    print(f"✗ Error: {e}")
    print("\nPlease install required packages:")
    print("  pip install pandas numpy")
    sys.exit(1)

# Create visualizer
print("\nInitializing visualizer...")
try:
    from visualization.visualizer import ChartGenerator
    
    viz = ChartGenerator(data, theme='plotly_dark')
    print("✓ Visualizer ready")
    
except ImportError as e:
    print(f"✗ Error: {e}")
    print("\nPlease install required packages:")
    print("  pip install plotly")
    sys.exit(1)

# Create output directory
output_dir = Path("exports/test_visualizations")
output_dir.mkdir(parents=True, exist_ok=True)

# Create charts
print("\nCreating visualizations...")
charts_created = []

try:
    # 1. File type pie chart
    print("  [1/7] File type distribution...")
    fig = viz.create_pie_chart('file_type', 'File Type Distribution')
    filepath = output_dir / "01_file_types.html"
    fig.write_html(str(filepath))
    charts_created.append(("File Types", filepath))
    
    # 2. Camera bar chart
    print("  [2/7] Camera distribution...")
    fig = viz.create_bar_chart('camera_model', 'Camera Models Used', top_n=10)
    filepath = output_dir / "02_cameras.html"
    fig.write_html(str(filepath))
    charts_created.append(("Camera Models", filepath))
    
    # 3. Timeline
    print("  [3/7] Timeline...")
    fig = viz.create_timeline('created_date', 'Files Over Time', group_by='week')
    filepath = output_dir / "03_timeline.html"
    fig.write_html(str(filepath))
    charts_created.append(("Timeline", filepath))
    
    # 4. File size histogram
    print("  [4/7] File size distribution...")
    data['file_size_mb'] = data['file_size'] / (1024 * 1024)
    viz_temp = ChartGenerator(data, theme='plotly_dark')
    fig = viz_temp.create_histogram('file_size_mb', 'File Size Distribution (MB)', bins=25)
    filepath = output_dir / "04_file_sizes.html"
    fig.write_html(str(filepath))
    charts_created.append(("File Sizes", filepath))
    
    # 5. Resolution scatter
    print("  [5/7] Resolution distribution...")
    fig = viz.create_scatter_plot('width', 'height', 'Resolution Distribution', color_field='file_type')
    filepath = output_dir / "05_resolution.html"
    fig.write_html(str(filepath))
    charts_created.append(("Resolution", filepath))
    
    # 6. ISO histogram
    print("  [6/7] ISO distribution...")
    fig = viz.create_histogram('iso', 'ISO Settings Distribution', bins=15)
    filepath = output_dir / "06_iso.html"
    fig.write_html(str(filepath))
    charts_created.append(("ISO Settings", filepath))
    
    # 7. Aperture box plot
    print("  [7/7] Aperture distribution...")
    fig = viz.create_box_plot('aperture', group_by='camera_model', title='Aperture by Camera')
    filepath = output_dir / "07_aperture.html"
    fig.write_html(str(filepath))
    charts_created.append(("Aperture", filepath))
    
    print(f"\n✓ Created {len(charts_created)} visualizations!")
    
except Exception as e:
    print(f"\n✗ Error creating charts: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Create Power BI style dashboard
print("\nCreating dashboard page...")
index_path = output_dir / "index.html"

with open(index_path, 'w') as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BareBlocks Metadata Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0d1117;
            height: 100vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
            border-bottom: 1px solid #30363d;
            color: #e6edf3;
            padding: 12px 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .header h1 {
            font-size: 1.4em;
            font-weight: 600;
            color: #58a6ff;
        }
        .header-info {
            font-size: 0.85em;
            opacity: 0.9;
            color: #8b949e;
        }
        .dashboard {
            flex: 1;
            padding: 12px;
            overflow: hidden;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            grid-template-rows: repeat(2, 1fr);
            gap: 12px;
            height: calc(100vh - 60px);
        }
        .chart-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.4);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
        }
        .chart-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.6);
            border-color: #58a6ff;
        }
        .chart-header {
            padding: 10px 12px;
            border-bottom: 1px solid #30363d;
            background: #0d1117;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .chart-title {
            font-size: 0.9em;
            font-weight: 600;
            color: #e6edf3;
        }
        .chart-icon {
            color: #58a6ff;
            cursor: pointer;
            font-size: 0.85em;
            text-decoration: none;
        }
        .chart-icon:hover {
            color: #79c0ff;
        }
        .chart-body {
            flex: 1;
            overflow: hidden;
            position: relative;
        }
        iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
        /* Specific grid positions for optimal layout */
        .chart-card:nth-child(1) { grid-column: 1 / 2; grid-row: 1 / 2; }
        .chart-card:nth-child(2) { grid-column: 2 / 3; grid-row: 1 / 2; }
        .chart-card:nth-child(3) { grid-column: 3 / 5; grid-row: 1 / 2; }
        .chart-card:nth-child(4) { grid-column: 1 / 2; grid-row: 2 / 3; }
        .chart-card:nth-child(5) { grid-column: 2 / 3; grid-row: 2 / 3; }
        .chart-card:nth-child(6) { grid-column: 3 / 4; grid-row: 2 / 3; }
        .chart-card:nth-child(7) { grid-column: 4 / 5; grid-row: 2 / 3; }
        
        @media (max-width: 1400px) {
            .dashboard {
                grid-template-columns: repeat(3, 1fr);
                grid-template-rows: repeat(3, 1fr);
            }
            .chart-card:nth-child(1) { grid-column: 1 / 2; grid-row: 1 / 2; }
            .chart-card:nth-child(2) { grid-column: 2 / 3; grid-row: 1 / 2; }
            .chart-card:nth-child(3) { grid-column: 3 / 4; grid-row: 1 / 2; }
            .chart-card:nth-child(4) { grid-column: 1 / 2; grid-row: 2 / 3; }
            .chart-card:nth-child(5) { grid-column: 2 / 3; grid-row: 2 / 3; }
            .chart-card:nth-child(6) { grid-column: 3 / 4; grid-row: 2 / 3; }
            .chart-card:nth-child(7) { grid-column: 1 / 4; grid-row: 3 / 4; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 BareBlocks Metadata Dashboard</h1>
        <div class="header-info">150 files • 5 cameras • 7 visualizations</div>
    </div>
    <div class="dashboard">
""")
    
    chart_descriptions = {
        "File Types": "Distribution of file types (pie chart)",
        "Camera Models": "Top cameras used (bar chart)",
        "Timeline": "Files created over time (line chart)",
        "File Sizes": "File size distribution with statistics (histogram)",
        "Resolution": "Image dimensions scatter plot",
        "ISO Settings": "ISO values distribution (histogram)",
        "Aperture": "Aperture settings by camera (box plot)"
    }
    
    for title, filepath in charts_created:
        filename = filepath.name
        f.write(f"""
        <div class="chart-card">
            <div class="chart-header">
                <div class="chart-title">{title}</div>
                <a href="{filename}" target="_blank" class="chart-icon" title="Open in new tab">⤢</a>
            </div>
            <div class="chart-body">
                <iframe src="{filename}" title="{title}"></iframe>
            </div>
        </div>
""")
    
    f.write("""
    </div>
</body>
</html>
""")

print(f"✓ Dashboard created: {index_path}")

# Open in browser
print("\nOpening in browser...")
try:
    import webbrowser
    webbrowser.open(f"file://{index_path.absolute()}")
    print("✓ Browser opened")
except:
    print("⚠️  Could not open browser automatically")
    print(f"   Open manually: {index_path.absolute()}")

# Summary
print("\n" + "=" * 70)
print("  ✅ Test Complete!")
print("=" * 70)
print()
print(f"Location: {output_dir.absolute()}")
print()
print("Charts created:")
for title, filepath in charts_created:
    print(f"  • {title}: {filepath.name}")
print()
print("All charts are fully interactive:")
print("  • Hover for details")
print("  • Click and drag to zoom")
print("  • Double-click to reset")
print("  • Use toolbar to save as PNG")
print()
print("=" * 70)
