#!/usr/bin/env python3
"""
Analyze tech stack for BareBlocks project
"""

import os
from pathlib import Path
from collections import defaultdict

# Exclude directories
exclude_dirs = {'__pycache__', '.git', 'node_modules', 'venv', 'env', '.pytest_cache', 'uploads', '.vscode', '.idea'}
exclude_files = {'.gitignore', '.gitattributes', '.DS_Store'}

# File type categories
file_stats = defaultdict(lambda: {'count': 0, 'lines': 0, 'size': 0})

def get_file_type_category(ext):
    """Categorize file by type"""
    ext = ext.lower()
    
    if ext in ['.py']:
        return 'Python'
    elif ext in ['.html']:
        return 'HTML'
    elif ext in ['.js', '.jsx', '.ts', '.tsx']:
        return 'JavaScript/TypeScript'
    elif ext in ['.css', '.scss', '.sass']:
        return 'CSS'
    elif ext in ['.md', '.txt']:
        return 'Documentation'
    elif ext in ['.json', '.yaml', '.yml']:
        return 'Configuration'
    elif ext in ['.sh', '.bat', '.ps1']:
        return 'Scripts'
    elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
        return 'Images'
    elif ext == '':
        return 'No Extension'
    else:
        return 'Other'

def count_lines(file_path):
    """Count lines in a file"""
    try:
        with open(file_path, 'rb') as f:
            return sum(1 for _ in f)
    except:
        return 0

def get_file_size(file_path):
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except:
        return 0

# Walk through project
for root, dirs, filenames in os.walk('.'):
    # Filter out excluded directories
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    
    for filename in filenames:
        # Skip excluded files
        if filename.startswith('.') and filename not in exclude_files:
            continue
        
        file_path = Path(root) / filename
        
        if file_path.is_file():
            ext = file_path.suffix
            category = get_file_type_category(ext)
            
            lines = count_lines(file_path)
            size = get_file_size(file_path)
            
            file_stats[category]['count'] += 1
            file_stats[category]['lines'] += lines
            file_stats[category]['size'] += size

# Calculate totals
total_files = sum(stats['count'] for stats in file_stats.values())
total_lines = sum(stats['lines'] for stats in file_stats.values())
total_size = sum(stats['size'] for stats in file_stats.values())

# Print results
print("=" * 70)
print("BAREBLOCKS PROJECT - TECH STACK ANALYSIS")
print("=" * 70)
print()

print("FILE COUNT BY TYPE")
print("-" * 70)
for category, stats in sorted(file_stats.items(), key=lambda x: -x[1]['count']):
    pct = (stats['count'] / total_files * 100) if total_files > 0 else 0
    print(f"{category:25} {stats['count']:4} files ({pct:5.1f}%)")
print(f"{'TOTAL':25} {total_files:4} files")
print()

print("LINES OF CODE BY TYPE")
print("-" * 70)
for category, stats in sorted(file_stats.items(), key=lambda x: -x[1]['lines']):
    pct = (stats['lines'] / total_lines * 100) if total_lines > 0 else 0
    size_mb = stats['size'] / (1024 * 1024)
    print(f"{category:25} {stats['lines']:8,} lines ({pct:5.1f}%)  [{size_mb:.2f} MB]")
print(f"{'TOTAL':25} {total_lines:8,} lines")
print()

print("FILE SIZE BY TYPE")
print("-" * 70)
for category, stats in sorted(file_stats.items(), key=lambda x: -x[1]['size']):
    size_mb = stats['size'] / (1024 * 1024)
    pct = (stats['size'] / total_size * 100) if total_size > 0 else 0
    print(f"{category:25} {size_mb:8.2f} MB ({pct:5.1f}%)")
print(f"{'TOTAL':25} {total_size / (1024 * 1024):8.2f} MB")
print()

# Detailed breakdown
print("=" * 70)
print("DETAILED BREAKDOWN")
print("=" * 70)
print()

# Python files
python_files = []
for root, dirs, filenames in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for f in filenames:
        if f.endswith('.py'):
            fp = Path(root) / f
            if fp.is_file():
                lines = count_lines(fp)
                python_files.append((str(fp), lines))

if python_files:
    print("Python Files (Top 10 by size):")
    print("-" * 70)
    for filepath, lines in sorted(python_files, key=lambda x: -x[1])[:10]:
        rel_path = str(Path(filepath).relative_to('.'))
        print(f"  {rel_path:50} {lines:6,} lines")
    print()

# HTML files
html_files = []
for root, dirs, filenames in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for f in filenames:
        if f.endswith('.html'):
            fp = Path(root) / f
            if fp.is_file():
                lines = count_lines(fp)
                html_files.append((str(fp), lines))

if html_files:
    print("HTML Files:")
    print("-" * 70)
    for filepath, lines in sorted(html_files, key=lambda x: -x[1]):
        rel_path = str(Path(filepath).relative_to('.'))
        print(f"  {rel_path:50} {lines:6,} lines")
    print()

print("=" * 70)
print("DEPENDENCIES (from requirements.txt)")
print("=" * 70)
try:
    with open('requirements.txt', 'r') as f:
        deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        for dep in deps:
            print(f"  • {dep}")
except:
    print("  (requirements.txt not found)")
print()

