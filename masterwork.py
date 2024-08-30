import PySimpleGUI as sg
import pyautogui
import pytesseract
import cv2
import numpy as np
import json
import os
import threading
import time
import win32gui
import win32api
import keyboard
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

CONFIG_FILE = 'upgrade_config.json'

# Set up logging
logging.basicConfig(filename='masterwork_assistant.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class Config:
    upgrade_button: Tuple[int, int]
    skip_button: Tuple[int, int]
    close_button: Tuple[int, int]
    reset_button: Tuple[int, int]
    confirm_button: Tuple[int, int]
    scan_region: Tuple[int, int, int, int]
    target_word: str = "Dust"
    max_count: int = 3

def load_config() -> Config:
    default_config = Config((0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0, 0, 0))
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config_dict = json.load(f)
            # Update the dictionary with default values for new fields
            default_config_dict = asdict(default_config)
            default_config_dict.update(config_dict)
            return Config(**default_config_dict)
    except json.JSONDecodeError:
        logging.error(f"Error decoding {CONFIG_FILE}. Using default configuration.")
    except KeyError as e:
        logging.error(f"Missing key in configuration: {e}. Using default configuration.")
    return default_config

def save_config(config: Config) -> None:
    with open(CONFIG_FILE, 'w') as f:
        json.dump(asdict(config), f)
    logging.info("Configuration saved successfully.")

def capture_screen_region(region: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
    try:
        screenshot = pyautogui.screenshot(region=region)
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    except Exception as e:
        logging.error(f"Error capturing screen region: {e}")
        return None

def preprocess_image(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

def scan_for_text(region: Tuple[int, int, int, int]) -> str:
    image = capture_screen_region(region)
    if image is None:
        return ""
    processed_image = preprocess_image(image)
    try:
        text = pytesseract.image_to_string(processed_image)
        return text.strip()
    except Exception as e:
        logging.error(f"Error scanning for text: {e}")
        return ""

def click_button(x: int, y: int) -> None:
    try:
        pyautogui.click(x, y)
    except Exception as e:
        logging.error(f"Error clicking button at ({x}, {y}): {e}")

class UpgradeProcess(threading.Thread):
    def __init__(self, config: Config, window: sg.Window):
        super().__init__()
        self.config = config
        self.window = window
        self.stop_event = threading.Event()

    def run(self) -> None:
        count = 0
        while count < self.config.max_count and not self.stop_event.is_set():
            try:
                self.perform_upgrade_cycle()
                scanned_text = scan_for_text(self.config.scan_region)
                self.window.write_event_value('-UPDATE-', f"Scanned text: {scanned_text}")
                
                if self.config.target_word.lower() in scanned_text.lower():
                    click_button(*self.config.close_button)
                    count += 1
                    self.window.write_event_value('-UPDATE-', f"Found '{self.config.target_word}'. Count: {count}")
                else:
                    self.reset_upgrade()
                    count = 0
                time.sleep(1)
            except Exception as e:
                logging.error(f"Error in upgrade process: {e}")
                self.window.write_event_value('-UPDATE-', f"Error occurred: {e}")
                time.sleep(5)  # Wait before retrying

        if not self.stop_event.is_set():
            self.window.write_event_value('-UPDATE-', f"Found '{self.config.target_word}' {self.config.max_count} times. Process complete.")

    def perform_upgrade_cycle(self) -> None:
        for _ in range(4):
            click_button(*self.config.upgrade_button)
            self.window.write_event_value('-UPDATE-', f"Clicked Upgrade button {_+1}/4")
            time.sleep(0.3)
        
        click_button(*self.config.skip_button)
        self.window.write_event_value('-UPDATE-', "Clicked Skip button")
        time.sleep(2)

    def reset_upgrade(self) -> None:
        click_button(*self.config.close_button)
        time.sleep(0.3)
        click_button(*self.config.reset_button)
        time.sleep(0.3)
        click_button(*self.config.confirm_button)
        self.window.write_event_value('-UPDATE-', "Reset and confirmed")

    def stop(self) -> None:
        self.stop_event.set()

def get_mouse_click() -> Tuple[int, int]:
    while True:
        if win32api.GetAsyncKeyState(0x01) & 0x8000:  # Left mouse button
            time.sleep(0.1)  # Wait for button release
            return win32gui.GetCursorPos()
        time.sleep(0.01)

def get_mouse_position(window: sg.Window, key: str) -> Tuple[int, int]:
    window.hide()
    popup = sg.Window("Get Position", [[sg.Text(f"Click on the desired position for {key}")]], no_titlebar=True, keep_on_top=True, finalize=True)
    
    position = get_mouse_click()
    
    popup.close()
    window.un_hide()
    return position

def get_scan_region(window: sg.Window) -> Tuple[int, int, int, int]:
    window.hide()
    popup = sg.Window("Get Scan Region", [[sg.Text("Click on the top-left corner of the scan region")]], no_titlebar=True, keep_on_top=True, finalize=True)
    
    top_left = get_mouse_click()
    
    popup.close()
    popup = sg.Window("Get Scan Region", [[sg.Text("Click on the bottom-right corner of the scan region")]], no_titlebar=True, keep_on_top=True, finalize=True)
    
    bottom_right = get_mouse_click()
    
    popup.close()
    window.un_hide()
    return (top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])

def create_main_window(config: Config) -> sg.Window:
    layout = [
        [sg.Text("Upgrade and Check Configuration")],
        [sg.Text("Upgrade Button:"), sg.Input(key='UPGRADE', default_text=f"{config.upgrade_button[0]},{config.upgrade_button[1]}", size=(15, 1)), sg.Button("Get", key='GET_UPGRADE')],
        [sg.Text("Skip Button:"), sg.Input(key='SKIP', default_text=f"{config.skip_button[0]},{config.skip_button[1]}", size=(15, 1)), sg.Button("Get", key='GET_SKIP')],
        [sg.Text("Close Button:"), sg.Input(key='CLOSE', default_text=f"{config.close_button[0]},{config.close_button[1]}", size=(15, 1)), sg.Button("Get", key='GET_CLOSE')],
        [sg.Text("Reset Button:"), sg.Input(key='RESET', default_text=f"{config.reset_button[0]},{config.reset_button[1]}", size=(15, 1)), sg.Button("Get", key='GET_RESET')],
        [sg.Text("Confirm Button:"), sg.Input(key='CONFIRM', default_text=f"{config.confirm_button[0]},{config.confirm_button[1]}", size=(15, 1)), sg.Button("Get", key='GET_CONFIRM')],
        [sg.Text("Scan Region:"), sg.Input(key='SCAN_REGION', default_text=','.join(map(str, config.scan_region)), size=(20, 1)), sg.Button("Get", key='GET_SCAN_REGION')],
        [sg.Text("Target Word:"), sg.Input(key='TARGET_WORD', default_text=config.target_word, size=(15, 1))],
        [sg.Text("Max Count:"), sg.Input(key='MAX_COUNT', default_text=str(config.max_count), size=(5, 1))],
        [sg.Button("Save Configuration"), sg.Button("Start Process"), sg.Button("Stop Process"), sg.Button("Exit")],
        [sg.Multiline(size=(60, 10), key='OUTPUT', disabled=True)]
    ]
    return sg.Window("Upgrade and Check", layout, finalize=True)

def validate_config(config: Config) -> bool:
    if any(v == (0, 0) for v in [config.upgrade_button, config.skip_button, config.close_button, config.reset_button, config.confirm_button]):
        return False
    if config.scan_region == (0, 0, 0, 0):
        return False
    if not config.target_word or config.max_count <= 0:
        return False
    return True

def main():
    config = load_config()
    window = create_main_window(config)

    upgrade_process = None

    while True:
        event, values = window.read(timeout=100)
        if event == sg.WINDOW_CLOSED or event == "Exit":
            break
        elif event.startswith('GET_'):
            key = event.replace('GET_', '')
            if key == 'SCAN_REGION':
                region = get_scan_region(window)
                window['SCAN_REGION'].update(','.join(map(str, region)))
            else:
                position = get_mouse_position(window, key)
                window[key].update(f"{position[0]},{position[1]}")
        elif event == "Save Configuration":
            try:
                new_config = Config(
                    upgrade_button=tuple(map(int, values['UPGRADE'].split(','))),
                    skip_button=tuple(map(int, values['SKIP'].split(','))),
                    close_button=tuple(map(int, values['CLOSE'].split(','))),
                    reset_button=tuple(map(int, values['RESET'].split(','))),
                    confirm_button=tuple(map(int, values['CONFIRM'].split(','))),
                    scan_region=tuple(map(int, values['SCAN_REGION'].split(','))),
                    target_word=values['TARGET_WORD'],
                    max_count=int(values['MAX_COUNT'])
                )
                if validate_config(new_config):
                    save_config(new_config)
                    config = new_config
                    window['OUTPUT'].print("Configuration saved successfully.")
                else:
                    window['OUTPUT'].print("Invalid configuration. Please check all fields.")
            except ValueError:
                window['OUTPUT'].print("Invalid input. Please check all fields.")
        elif event == "Start Process":
            if upgrade_process is None or not upgrade_process.is_alive():
                if validate_config(config):
                    upgrade_process = UpgradeProcess(config, window)
                    upgrade_process.start()
                else:
                    window['OUTPUT'].print("Invalid configuration. Please check all fields.")
            else:
                window['OUTPUT'].print("Process is already running.")
        elif event == "Stop Process":
            if upgrade_process and upgrade_process.is_alive():
                upgrade_process.stop()
                upgrade_process.join()
                window['OUTPUT'].print("Process stopped.")
            else:
                window['OUTPUT'].print("No process is running.")
        elif event == '-UPDATE-':
            window['OUTPUT'].print(values['-UPDATE-'])
        
        # Check for 'P' key press to terminate the process
        if keyboard.is_pressed('p') and upgrade_process and upgrade_process.is_alive():
            upgrade_process.stop()
            upgrade_process.join()
            window['OUTPUT'].print("Process terminated by user (P key pressed)")
            upgrade_process = None

    if upgrade_process and upgrade_process.is_alive():
        upgrade_process.stop()
        upgrade_process.join()

    window.close()

if __name__ == "__main__":
    main()
