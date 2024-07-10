# /bin/bash

echo "Creating Linux Release"
python -m PyInstaller --clean -F --hidden-import='PIL._tkinter_finder' PersonalRunningOrderTool.py

echo "Creating Windows Release via Wine"
wine python -m PyInstaller --clean -F PersonalRunningOrderTool.py
