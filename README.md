# Diablo 4 Masterwork Upgrade Assistant

This Python script assists with upgrading Masterwork items in Diablo 4, specifically targeting a user-defined affix.

## Installation Instructions

1. Install Python:
   - Download and install Python 3.x from [python.org](https://www.python.org/downloads/)
   - During installation, make sure to check "Add Python to PATH"

2. Install Tesseract OCR:
   - Download and install Tesseract OCR from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - Note the installation path (default is usually `C:\Program Files\Tesseract-OCR`)

3. Clone or download this repository to your local machine

4. Open a command prompt in the project directory and install required Python libraries:
   ```
   pip install PySimpleGUI pyautogui pytesseract opencv-python numpy pywin32 keyboard
   ```

5. Update the Tesseract path in the script:
   - Open `masterwork.py` in a text editor
   - Find the line: `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`
   - Modify the path if your Tesseract installation is in a different location

## Usage

1. Run the script via command prompt: `python masterwork.py`
2. Use the GUI to set up button positions and the scan region:
   - Click "Get" next to each button to set its position
   - For the scan region, click "Get" and then:
     1. Click on the top-left corner of the desired scan area
     2. Click on the bottom-right corner of the desired scan area
3. Enter the target word (affix) and maximum count
4. Save the configuration
5. Start the process

## Important Notes

- The 'P' key serves as a kill switch to stop the process. You can also use the "Stop Process" button in the GUI.
- A wider scan area may increase the likelihood of false positives. It's recommended to keep the scan region focused.
- The configuration is saved in `upgrade_config.json` and will be loaded automatically on subsequent runs.
- This script is designed to work with any affix, not just "counteroffensive". Adjust the target word as needed.
- The script's performance may vary depending on your system and game settings.

## Configuration

The `upgrade_config.json` file contains the coordinates for various buttons, the scan region, target word, and max count. The configuration can be set and saved through the GUI.

## Limitations

- The performance may vary depending on your system and game settings.
- The script relies on image recognition, which may be affected by in-game graphical settings or overlays.

## Contributing

If you make any improvements, please share them by creating an issue or submitting a pull request on GitHub. Working together, we can enhance the functionality and reliability of this tool.

## Disclaimer

This project is for educational purposes only. Use at your own risk. The creators are not responsible for any consequences of using this script. Always ensure you're complying with the game's terms of service when using external tools.
