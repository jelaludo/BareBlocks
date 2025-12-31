#!/usr/bin/env python3
"""
Demo script to create and view visualizations from your metadata.

This script will:
1. Process files from the media/ directory
2. Store metadata in database
3. Generate statistical analysis
4. Create interactive visualizations
5. Open them in your web browser

Usage:
    python demo_visualizations.py
"""

import sys
import os
from pathlib import Path
import webbrowser
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("  BareBlocks Metadata Visualization Demo")
print("=" * 70)
print()

# Step 1: Check if we have files to process
print("Step 1: Checking for files...")
media_dir = Path("media")

if not media_dir.exists():
    media_dir.mkdir()
    print(f"⚠️  Created media/ directory")
    print(f"   Please add some image/video files to {media_dir.absolute()}")
    print(f"   Then run this script again.")
    sys.exit(0)

# Count files
image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
video_exts = ['.mp4', '.avi', '.mov', '.mkv']
all_files = []

for ext in image_exts + video_exts:
    all_files.extend(list(media_dir.rglob(f"*{ext}")))
    all_files.extend(list(media_dir.rglob(f"*{ext.upper()}")))

if len(all_files) == 0:
    print(f"⚠️  No media files found in {media_dir.absolute()}")
    print(f"   Please add some image/video files and run again.")
    sys.exit(0)

print(f"✓ Found {len(all_files)} files to process")

# Step 2: Process files
print("\nStep 2: Extracting metadata...")
try:
    from core.metadata_aggregator import MetadataAggregator
    
    aggregator = MetadataAggregator(verbose=False)
    files = aggregator.scan_directory("media/", recursive=True)
    
    if len(files) == 0:
        print("⚠️  No supported files found")
        sys.exit(0)
    
    print(f"  Processing {len(files)} files...")
    result = aggregator.process_batch(files, max_workers=4, show_progress=True)
    
    print(f"\n✓ Processed {result.successful} files successfully")
    if result.failed > 0:
        print(f"  ⚠️  {result.failed} files failed")
    
except Exception as e:
    print(f"✗ Error processing files: {e}")
    sys.exit(1)

# Step 3: Store in database
print("\nStep 3: Storing metadata in database...")
try:
    from core.data_storage import MetadataDatabase
    
    db = MetadataDatabase("data/metadata.db")
    
    # Clear old data
    old_count = db.get_statistics().get('total_files', 0)
    if old_count > 0:
        print(f"  Clearing {old_count} old records...")
        db.delete_all()
    
    # Insert new data
    db.insert_batch(aggregator.get_results())
    
    stats = db.get_statistics()
    print(f"✓ Stored {stats['total_files']} files in database")
    print(f"  Total size: {stats['total_size_mb']:.2f} MB")
    
except Exception as e:
    print(f"✗ Error storing data: {e}")
    sys.exit(1)

# Step 4: Generate statistics
print("\nStep 4: Analyzing metadata...")
try:
    from analysis.statistical_analyzer import StatisticalAnalyzer
    import pandas as pd
    
    # Get all data
    df = db.export_to_dataframe()
    
    if len(df) == 0:
        print("⚠️  No data to analyze")
        sys.exit(0)
    
    analyzer = StatisticalAnalyzer(df)
    report = analyzer.get_summary_report()
    
    print(f"✓ Analysis complete")
    print(f"  File types: {report['overview'].get('file_type_distribution', {})}")
    
    # Save report
    analyzer.export_report("exports/analysis_report.json")
    print(f"✓ Report saved to exports/analysis_report.json")
    
except Exception as e:
    print(f"✗ Error analyzing data: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Create visualizations
print("\nStep 5: Creating visualizations...")
try:
    from visualization.visualizer import ChartGenerator
    
    viz = ChartGenerator(df, theme='plotly_dark')
    
    # Create output directory
    output_dir = Path("exports/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    charts_created = []
    
    # 1. File type distribution
    if 'file_type' in df.columns:
        print("  Creating file type distribution chart...")
        fig = viz.create_pie_chart('file_type', 'File Type Distribution')
        filepath = output_dir / "01_file_types.html"
        fig.write_html(str(filepath))
        charts_created.append(filepath)
    
    # 2. Camera distribution (if images present)
    if 'camera_model' in df.columns and df['camera_model'].notna().any():
        print("  Creating camera distribution chart...")
        fig = viz.create_bar_chart('camera_model', 'Top Cameras Used', top_n=10)
        filepath = output_dir / "02_cameras.html"
        fig.write_html(str(filepath))
        charts_created.append(filepath)
    
    # 3. Timeline
    if 'created_date' in df.columns:
        print("  Creating timeline chart...")
        fig = viz.create_timeline('created_date', 'Files Created Over Time', group_by='day')
        filepath = output_dir / "03_timeline.html"
        fig.write_html(str(filepath))
        charts_created.append(filepath)
    
    # 4. File size distribution
    if 'file_size' in df.columns:
        print("  Creating file size distribution...")
        df_temp = df.copy()
        df_temp['file_size_mb'] = df_temp['file_size'] / (1024 * 1024)
        viz_temp = ChartGenerator(df_temp, theme='plotly_dark')
        fig = viz_temp.create_histogram('file_size_mb', 'File Size Distribution (MB)', bins=20)
        filepath = output_dir / "04_file_sizes.html"
        fig.write_html(str(filepath))
        charts_created.append(filepath)
    
    # 5. Resolution scatter plot (if available)
    if 'width' in df.columns and 'height' in df.columns:
        if df[['width', 'height']].notna().any().any():
            print("  Creating resolution distribution...")
            fig = viz.create_scatter_plot(
                'width', 'height',
                'Image Resolution Distribution',
                color_field='file_type' if 'file_type' in df.columns else None
            )
            filepath = output_dir / "05_resolutions.html"
            fig.write_html(str(filepath))
            charts_created.append(filepath)
    
    # 6. ISO distribution (if available)
    if 'iso' in df.columns and df['iso'].notna().any():
        print("  Creating ISO distribution...")
        fig = viz.create_histogram('iso', 'ISO Settings Distribution', bins=15)
        filepath = output_dir / "06_iso_distribution.html"
        fig.write_html(str(filepath))
        charts_created.append(filepath)
    
    # 7. Metadata completeness heatmap
    print("  Creating metadata completeness heatmap...")
    important_fields = [col for col in df.columns if col in [
        'camera_model', 'lens_model', 'iso', 'aperture', 
        'focal_length', 'width', 'height', 'gps_latitude'
    ]]
    if important_fields:
        fig = viz.create_heatmap(important_fields, 'Metadata Completeness')
        filepath = output_dir / "07_completeness.html"
        fig.write_html(str(filepath))
        charts_created.append(filepath)
    
    print(f"\n✓ Created {len(charts_created)} visualizations")
    
except Exception as e:
    print(f"✗ Error creating visualizations: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 6: Create Power BI style dashboard
print("\nStep 6: Creating dashboard page...")
try:
    index_html = output_dir / "index.html"
    
    with open(index_html, 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BareBlocks Metadata Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
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
        .stats-bar {
            display: flex;
            gap: 20px;
            font-size: 0.85em;
            color: #8b949e;
        }
        .stat-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .stat-value {
            font-weight: 600;
            font-size: 1.1em;
            color: #58a6ff;
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
            display: flex;
            align-items: center;
            gap: 8px;
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
        @media (max-width: 1400px) {
            .dashboard {
                grid-template-columns: repeat(3, 1fr);
                grid-template-rows: repeat(3, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 BareBlocks Metadata Dashboard</h1>
        <div class="stats-bar">
            <div class="stat-item">
                <span>📁 Files:</span>
                <span class="stat-value">""" + str(stats['total_files']) + """</span>
            </div>
            <div class="stat-item">
                <span>💾 Size:</span>
                <span class="stat-value">""" + str(stats.get('total_size_mb', 0)) + """ MB</span>
            </div>
            <div class="stat-item">
                <span>📷 Cameras:</span>
                <span class="stat-value">""" + str(stats.get('unique_cameras', 0)) + """</span>
            </div>
            <div class="stat-item">
                <span>📊 Charts:</span>
                <span class="stat-value">""" + str(len(charts_created)) + """</span>
            </div>
        </div>
    </div>
    <div class="dashboard">
""")
        
        chart_info = [
            ("01_file_types.html", "📁", "File Types"),
            ("02_cameras.html", "📷", "Camera Models"),
            ("03_timeline.html", "📅", "Timeline"),
            ("04_file_sizes.html", "💾", "File Sizes"),
            ("05_resolutions.html", "🖼️", "Resolutions"),
            ("06_iso_distribution.html", "⚙️", "ISO Settings"),
            ("07_completeness.html", "✅", "Completeness"),
        ]
        
        for filename, icon, title in chart_info:
            if (output_dir / filename).exists():
                f.write(f"""
        <div class="chart-card">
            <div class="chart-header">
                <div class="chart-title">{icon} {title}</div>
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
    
    print(f"✓ Index page created: {index_html}")
    
except Exception as e:
    print(f"⚠️  Could not create index page: {e}")

# Step 7: Open in browser
print("\n" + "=" * 70)
print("  🎉 Success! Visualizations created!")
print("=" * 70)
print()
print(f"Charts saved to: {output_dir.absolute()}")
print()
print("Opening in your web browser...")
print()

# Open the index page
try:
    webbrowser.open(f"file://{index_html.absolute()}")
    print("✓ Opened in browser")
except:
    print(f"⚠️  Could not open browser automatically")
    print(f"   Please open this file manually: {index_html.absolute()}")

print()
print("You can also open individual charts:")
for chart in charts_created:
    print(f"  • {chart.name}")

print()
print("=" * 70)
print("Next steps:")
print("  • Add more files to media/ directory")
print("  • Run this script again to update visualizations")
print("  • Check GETTING_STARTED.md for more features")
print("=" * 70)
