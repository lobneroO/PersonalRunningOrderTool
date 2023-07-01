# /bin/bash

echo "Creating Linux Release"
python -m PyInstaller -F  PersonalRunningOrderTool.py 
 
echo "Creating Windows Release via Wine"
wine python -m PyInstaller -F  PersonalRunningOrderTool.py 
