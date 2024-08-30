# Diablo 4 Masterwork Upgrade Assistant

This Python script assists with upgrading Masterwork items in Diablo 4, specifically targeting the "counteroffensive" affix.

## Installation Instructions

1. Install Python:
   - Download and install Python 3.x from [python.org](https://www.python.org/downloads/)
   - During installation, make sure to check "Add Python to PATH"

2. Install Tesseract OCR:
   - Download and install Tesseract OCR from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - Note the installation path (default is usually `C:\Program Files\Tesseract-OCR`)

3. Clone or download this repository to your local machine

4. Open a command prompt in the project directory and install required Python libraries:

pip install PySimpleGUI pyautogui pytesseract opencv-python numpy pywin32 keyboard

6. Update the Tesseract path in the script:
- Open `masterwork.py` in a text editor
- Find the line: `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`
- Modify the path if your Tesseract installation is in a different location

## Usage

1. Run the script:
python masterwork.py
Copy
2. Use the GUI to set up button positions and the scan region
3. Save the configuration
4. Start the process

## Important Notes

- This script is experimental and may require adjustments for different setups
- The 'P' key acts as a kill switch to stop the process
- Note: The kill switch may not respond instantly. If the program doesn't stop immediately, hold down the 'P' key for a few seconds until it terminates.
- Scanning a wider area may lead to more false positives, so keep the scan region focused
- The current setup is optimized for 2560x1440 resolution and the "counteroffensive" affix
- For other affixes or resolutions, you may need to adjust the scan region
- If you change from "counteroffensive" to another affix, you will need to set up a new scan region area
- You can scan just part of a word if desired, as long as the scan matches 1:1 with what you're looking for

## Configuration

The `upgrade_config.json` file contains the coordinates for various buttons and the scan region. The provided configuration is set up for 2560x1440 resolution:

json
{
 "upgrade_button": [662, 1214],
 "skip_button": [474, 1100],
 "close_button": [474, 1100],
 "reset_button": [571, 464],
 "confirm_button": [375, 1267],
 "scan_region": [221, 913, 293, 47]
}
Adjust these values as needed for your specific setup.
Limitations

The script is currently set up for the "counteroffensive" affix. Other affixes are untested.
The performance may vary depending on your system and game settings.

Contributing
This project was created with minimal Python experience, using AI assistance. If you make any improvements, please share them by creating an issue or submitting a pull request on GitHub. Working together, we can enhance the functionality and reliability of this tool.
Disclaimer
This project is for educational purposes only. Use at your own risk. The creators are not responsible for any consequences of using this script. Always ensure you're complying with the game's terms of service when using external tools.
Copy
This README provides comprehensive installation instructions, usage guidelines, important notes about the script's functionality, configuration details, known limitations, and a call for contributions. It also includes the disclaimer you mentioned. 

Feel free to modify or expand any sections as you see fit before publishing on GitHub.
