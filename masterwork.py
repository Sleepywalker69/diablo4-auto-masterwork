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
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

CONFIG_FILE = 'upgrade_config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def capture_screen_region(region):
    return pyautogui.screenshot(region=region)

def preprocess_image(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return gray

def scan_for_text(region):
    image = capture_screen_region(region)
    processed_image = preprocess_image(image)
    text = pytesseract.image_to_string(processed_image)
    return text.strip()

def click_button(x, y):
    pyautogui.click(x, y)
    
def upgrade_and_check(target_word, max_count, config, window):
    count = 0
    
    while count < max_count:
        if keyboard.is_pressed('p'):  # Check if 'P' is pressed
            window.write_event_value('-UPDATE-', "Process terminated by user (P key pressed)")
            return  # Exit the function if 'P' is pressed

        for _ in range(4):
            click_button(*config['upgrade_button'])
            window.write_event_value('-UPDATE-', f"Clicked Upgrade button {_+1}/4")
            time.sleep(0.3)
        
        click_button(*config['skip_button'])
        window.write_event_value('-UPDATE-', "Clicked Skip button")
        time.sleep(2)
        
        scanned_text = scan_for_text(config['scan_region'])
        window.write_event_value('-UPDATE-', f"Scanned text: {scanned_text}")
        
        if target_word.lower() in scanned_text.lower():
            click_button(*config['close_button'])
            count += 1
            window.write_event_value('-UPDATE-', f"Found '{target_word}'. Count: {count}")
        else:
            click_button(*config['close_button'])
            time.sleep(0.3)
            click_button(*config['reset_button'])
            time.sleep(0.3)
            click_button(*config['confirm_button'])
            window.write_event_value('-UPDATE-', "Reset and confirmed")
            count = 0
        time.sleep(1)

    window.write_event_value('-UPDATE-', f"Found '{target_word}' {max_count} times. Process complete.")

def get_mouse_click():
    while True:
        if win32api.GetAsyncKeyState(0x01) & 0x8000:  # Left mouse button
            return win32gui.GetCursorPos()
        time.sleep(0.1)

def get_mouse_position(window, key):
    window.hide()
    sg.popup(f"Click on the desired position for {key}", keep_on_top=True, non_blocking=True)
    position = get_mouse_click()
    window.un_hide()
    return position

def get_scan_region(window):
    window.hide()
    sg.popup("Click on the top-left corner of the scan region", keep_on_top=True, non_blocking=True)
    top_left = get_mouse_click()
    
    sg.popup("Click on the bottom-right corner of the scan region", keep_on_top=True, non_blocking=True)
    bottom_right = get_mouse_click()
    
    window.un_hide()
    return (top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])

def create_main_window(config):
    layout = [
        [sg.Text("Upgrade and Check Configuration")],
        [sg.Text("Upgrade Button:"), sg.Input(key='UPGRADE', default_text=','.join(map(str, config.get('upgrade_button', ['', ''])))), sg.Button("Get", key='GET_UPGRADE')],
        [sg.Text("Skip Button:"), sg.Input(key='SKIP', default_text=','.join(map(str, config.get('skip_button', ['', ''])))), sg.Button("Get", key='GET_SKIP')],
        [sg.Text("Close Button:"), sg.Input(key='CLOSE', default_text=','.join(map(str, config.get('close_button', ['', ''])))), sg.Button("Get", key='GET_CLOSE')],
        [sg.Text("Reset Button:"), sg.Input(key='RESET', default_text=','.join(map(str, config.get('reset_button', ['', ''])))), sg.Button("Get", key='GET_RESET')],
        [sg.Text("Confirm Button:"), sg.Input(key='CONFIRM', default_text=','.join(map(str, config.get('confirm_button', ['', ''])))), sg.Button("Get", key='GET_CONFIRM')],
        [sg.Text("Scan Region:"), sg.Input(key='SCAN_REGION', default_text=','.join(map(str, config.get('scan_region', ['', '', '', ''])))), sg.Button("Get", key='GET_SCAN_REGION')],
        [sg.Button("Save Configuration"), sg.Button("Start Process"), sg.Button("Exit")],
        [sg.Multiline(size=(60, 10), key='OUTPUT', disabled=True)]
    ]
    return sg.Window("Upgrade and Check", layout, finalize=True)

def main():
    config = load_config()
    window = create_main_window(config)

    process_thread = None

    while True:
        event, values = window.read(timeout=100)  # Add a timeout to check for 'P' key press
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
            config = {
                'upgrade_button': list(map(int, values['UPGRADE'].split(','))),
                'skip_button': list(map(int, values['SKIP'].split(','))),
                'close_button': list(map(int, values['CLOSE'].split(','))),
                'reset_button': list(map(int, values['RESET'].split(','))),
                'confirm_button': list(map(int, values['CONFIRM'].split(','))),
                'scan_region': list(map(int, values['SCAN_REGION'].split(',')))
            }
            save_config(config)
            window['OUTPUT'].print("Configuration saved successfully.")
        elif event == "Start Process":
            if process_thread is None or not process_thread.is_alive():
                process_thread = threading.Thread(target=upgrade_and_check, args=("counteroffensive", 3, config, window), daemon=True)
                process_thread.start()
            else:
                window['OUTPUT'].print("Process is already running.")
        elif event == '-UPDATE-':
            window['OUTPUT'].print(values['-UPDATE-'])
        
        # Check for 'P' key press to terminate the process
        if keyboard.is_pressed('p') and process_thread and process_thread.is_alive():
            window['OUTPUT'].print("Process terminated by user (P key pressed)")
            process_thread = None  # Allow starting a new process

    window.close()

if __name__ == "__main__":
    main()