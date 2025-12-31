#!/bin/bash
# Setup script for BareBlocks Metadata Dashboard Project

echo "======================================================"
echo "  BareBlocks Metadata Dashboard - Setup Script"
echo "======================================================"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
else
    echo -e "${RED}✗${NC} Python 3.8 or higher is required"
    echo "  Current version: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${YELLOW}!${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓${NC} pip upgraded"

# Install base requirements
echo ""
echo "Installing base requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Base requirements installed"
    else
        echo -e "${RED}✗${NC} Failed to install base requirements"
        exit 1
    fi
else
    echo -e "${YELLOW}!${NC} requirements.txt not found"
fi

# Install dashboard requirements
echo ""
echo "Installing dashboard requirements..."
if [ -f "requirements-dashboard.txt" ]; then
    pip install -r requirements-dashboard.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Dashboard requirements installed"
    else
        echo -e "${RED}✗${NC} Failed to install dashboard requirements"
        exit 1
    fi
else
    echo -e "${YELLOW}!${NC} requirements-dashboard.txt not found"
fi

# Create necessary directories
echo ""
echo "Setting up directories..."
mkdir -p data exports media tests/fixtures
touch data/.gitkeep exports/.gitkeep media/.gitkeep
echo -e "${GREEN}✓${NC} Directories created"

# Verify installations
echo ""
echo "Verifying installations..."

# Test core modules
python3 -c "from core.data_models import FileMetadata" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Core data models OK"
else
    echo -e "${RED}✗${NC} Core data models failed"
fi

python3 -c "from core.metadata_aggregator import MetadataAggregator" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Metadata aggregator OK"
else
    echo -e "${RED}✗${NC} Metadata aggregator failed"
fi

python3 -c "from core.data_storage import MetadataDatabase" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Database storage OK"
else
    echo -e "${RED}✗${NC} Database storage failed"
fi

python3 -c "from analysis.statistical_analyzer import StatisticalAnalyzer" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Statistical analyzer OK"
else
    echo -e "${RED}✗${NC} Statistical analyzer failed"
fi

# Test key dependencies
python3 -c "import pandas" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Pandas installed"
else
    echo -e "${YELLOW}!${NC} Pandas not installed"
fi

python3 -c "import plotly" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Plotly installed"
else
    echo -e "${YELLOW}!${NC} Plotly not installed"
fi

python3 -c "import streamlit" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Streamlit installed"
else
    echo -e "${YELLOW}!${NC} Streamlit not installed"
fi

# Create sample test script
echo ""
echo "Creating test script..."
cat > test_setup.py << 'EOF'
#!/usr/bin/env python3
"""
Quick test script to verify setup.
"""

print("\n" + "="*60)
print("  Testing BareBlocks Metadata Dashboard Setup")
print("="*60 + "\n")

# Test imports
print("Testing imports...")
try:
    from core.data_models import FileMetadata, ImageMetadata
    print("✓ Data models imported successfully")
except ImportError as e:
    print(f"✗ Data models import failed: {e}")

try:
    from core.metadata_aggregator import MetadataAggregator
    print("✓ Metadata aggregator imported successfully")
except ImportError as e:
    print(f"✗ Metadata aggregator import failed: {e}")

try:
    from core.data_storage import MetadataDatabase
    print("✓ Database storage imported successfully")
except ImportError as e:
    print(f"✗ Database storage import failed: {e}")

try:
    from analysis.statistical_analyzer import StatisticalAnalyzer
    print("✓ Statistical analyzer imported successfully")
except ImportError as e:
    print(f"✗ Statistical analyzer import failed: {e}")

# Test database creation
print("\nTesting database...")
try:
    db = MetadataDatabase("data/test_metadata.db")
    print("✓ Database created successfully")
    
    # Test statistics
    stats = db.get_statistics()
    print(f"✓ Database statistics: {stats['total_files']} files")
except Exception as e:
    print(f"✗ Database test failed: {e}")

# Test aggregator initialization
print("\nTesting aggregator...")
try:
    aggregator = MetadataAggregator(verbose=False)
    print("✓ Aggregator initialized successfully")
except Exception as e:
    print(f"✗ Aggregator test failed: {e}")

print("\n" + "="*60)
print("  Setup verification complete!")
print("="*60 + "\n")

print("Next steps:")
print("1. Add some sample files to the ./media directory")
print("2. Run: python core/metadata_aggregator.py media/ --recursive")
print("3. Check the output in exports/")
print()
EOF

chmod +x test_setup.py
echo -e "${GREEN}✓${NC} Test script created: test_setup.py"

# Run the test
echo ""
echo "Running setup verification..."
python3 test_setup.py

# Final message
echo ""
echo "======================================================"
echo "  Setup Complete!"
echo "======================================================"
echo ""
echo "Project structure:"
echo "  ✓ Virtual environment (venv/)"
echo "  ✓ Core modules (core/)"
echo "  ✓ Analysis modules (analysis/)"
echo "  ✓ Visualization modules (visualization/)"
echo "  ✓ Dashboard (dashboard/)"
echo "  ✓ Data directory (data/)"
echo "  ✓ Exports directory (exports/)"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To test the aggregator:"
echo "  python core/metadata_aggregator.py media/ --recursive"
echo ""
echo "Documentation:"
echo "  - PROJECT_CONTEXT.md - Full project overview"
echo "  - QUICK_START.md - Quick reference guide"
echo "  - IMPLEMENTATION_PLAN.md - Detailed plan"
echo "  - PROGRESS.md - Current progress"
echo ""
echo "Happy coding! 🚀"
echo ""
