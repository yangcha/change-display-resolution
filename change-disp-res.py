# pylint: disable=invalid-name
"""
Module for changing the display resolution on Windows.
"""

import ctypes
import threading
import tkinter as tk

DM_PELSWIDTH = 0x00080000
DM_PELSHEIGHT = 0x00100000
DISP_CHANGE_SUCCESSFUL = 0
CDS_TEST = 0x00000002


class DEVMODE(ctypes.Structure):  # pylint: disable=too-few-public-methods
    """Windows DEVMODE structure for display settings."""

    _fields_ = [
        ("dmDeviceName", ctypes.c_wchar * 32),
        ("dmSpecVersion", ctypes.c_ushort),
        ("dmDriverVersion", ctypes.c_ushort),
        ("dmSize", ctypes.c_ushort),
        ("dmDriverExtra", ctypes.c_ushort),
        ("dmFields", ctypes.c_ulong),
        ("dmPositionX", ctypes.c_long),
        ("dmPositionY", ctypes.c_long),
        ("dmDisplayOrientation", ctypes.c_ulong),
        ("dmDisplayFixedOutput", ctypes.c_ulong),
        ("dmColor", ctypes.c_short),
        ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short),
        ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short),
        ("dmFormName", ctypes.c_wchar * 32),
        ("dmLogPixels", ctypes.c_ushort),
        ("dmBitsPerPel", ctypes.c_ulong),
        ("dmPelsWidth", ctypes.c_ulong),
        ("dmPelsHeight", ctypes.c_ulong),
        ("dmDisplayFlags", ctypes.c_ulong),
        ("dmDisplayFrequency", ctypes.c_ulong),
    ]


class DISPLAY_DEVICE(ctypes.Structure):  # pylint: disable=too-few-public-methods
    """Windows DISPLAY_DEVICE structure for display enumeration."""

    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("DeviceName", ctypes.c_wchar * 32),
        ("DeviceString", ctypes.c_wchar * 128),
        ("StateFlags", ctypes.c_ulong),
        ("DeviceID", ctypes.c_wchar * 128),
        ("DeviceKey", ctypes.c_wchar * 128),
    ]


def list_displays() -> list[str]:
    """Enumerate and print all active display devices.

    Returns:
        A list of active display device names.
    """
    user32 = ctypes.windll.user32
    devices = []
    index = 0

    while True:
        display = DISPLAY_DEVICE()
        display.cb = ctypes.sizeof(DISPLAY_DEVICE)  # pylint: disable=attribute-defined-outside-init
        if not user32.EnumDisplayDevicesW(None, index, ctypes.byref(display), 0):
            break
        # DISPLAY_DEVICE_ACTIVE = 0x00000001
        if display.StateFlags & 0x00000001:
            devices.append(display.DeviceName)
            print(f"  {display.DeviceName} - {display.DeviceString}")
        index += 1

    return devices


def identify_displays(display_names: list[str], duration: int = 30) -> None:
    """Show a large number overlay on each display for identification.

    Args:
        display_names: List of display device names from list_displays().
        duration: How many seconds to show the overlay.
    """
    user32 = ctypes.windll.user32

    # Get position and size of each display
    monitors = []
    for i, name in enumerate(display_names, 1):
        devmode = DEVMODE()
        devmode.dmSize = ctypes.sizeof(DEVMODE)  # pylint: disable=attribute-defined-outside-init
        if user32.EnumDisplaySettingsW(name, -1, ctypes.byref(devmode)):
            monitors.append(
                (
                    i,
                    name,
                    devmode.dmPositionX,
                    devmode.dmPositionY,
                    devmode.dmPelsWidth,
                    devmode.dmPelsHeight,
                )
            )

    if not monitors:
        print("No display positions found.")
        return

    def show_overlays():
        # Enable DPI awareness so window coordinates match physical pixels
        ctypes.windll.shcore.SetProcessDpiAwareness(2)

        root = tk.Tk()
        root.withdraw()

        windows = []
        for number, _, x, y, w, h in monitors:
            win = tk.Toplevel(root)
            win.overrideredirect(True)
            win.attributes("-topmost", True)
            win.configure(bg="black")

            label = tk.Label(
                win,
                text=str(number),
                font=("Arial", 150, "bold"),
                fg="white",
                bg="black",
            )
            label.pack(expand=True, fill="both")

            # Center a 300x300 window on the display
            win_w, win_h = 300, 300
            cx = x + (w - win_w) // 2
            cy = y + (h - win_h) // 2
            win.geometry(f"{win_w}x{win_h}+{cx}+{cy}")
            windows.append(win)

        def close_all():
            for win in windows:
                win.destroy()
            root.destroy()

        root.after(duration * 1000, close_all)
        root.mainloop()

    overlay_thread = threading.Thread(target=show_overlays, daemon=True)
    overlay_thread.start()
    overlay_thread.join()


def change_resolution(width: int, height: int, device_name: str = None) -> bool:
    """Change the screen resolution of the specified display device on Windows.

    Args:
        width: Desired screen width in pixels.
        height: Desired screen height in pixels.
        device_name: Display device name (e.g. r'\\\\.\\DISPLAY1'). If None,
            the primary display is used.

    Returns:
        True if the resolution was changed successfully, False otherwise.
    """

    user32 = ctypes.windll.user32

    devmode = DEVMODE()
    devmode.dmSize = ctypes.sizeof(DEVMODE)  # pylint: disable=attribute-defined-outside-init

    # Enumerate current display settings for the specified device
    if not user32.EnumDisplaySettingsW(device_name, -1, ctypes.byref(devmode)):
        print("Error: Could not retrieve current display settings.")
        return False

    devmode.dmPelsWidth = width  # pylint: disable=attribute-defined-outside-init
    devmode.dmPelsHeight = height  # pylint: disable=attribute-defined-outside-init
    devmode.dmFields = DM_PELSWIDTH | DM_PELSHEIGHT  # pylint: disable=attribute-defined-outside-init

    # Test if the resolution is supported on the specified device
    result = user32.ChangeDisplaySettingsExW(
        device_name, ctypes.byref(devmode), None, CDS_TEST, None
    )
    if result != DISP_CHANGE_SUCCESSFUL:
        print(f"Error: Resolution {width}x{height} is not supported.")
        return False

    # Apply the resolution change to the specified device
    result = user32.ChangeDisplaySettingsExW(
        device_name, ctypes.byref(devmode), None, 0, None
    )
    if result == DISP_CHANGE_SUCCESSFUL:
        print(f"Resolution changed to {width}x{height} successfully.")
        return True

    print(f"Error: Failed to change resolution. Error code: {result}")
    return False


if __name__ == "__main__":
    print("Active displays:")
    display_names = list_displays()
    if not display_names:
        print("No active displays found.")
    else:
        print()
        for i, name in enumerate(display_names, 1):
            print(f"  {i}. {name}")
        print()
        identify = input("Identify displays? (y/n): ").strip().lower()
        if identify == "y":
            identify_displays(display_names)
        print()
        choice = int(input(f"Select display (1-{len(display_names)}): "))
        if 1 <= choice <= len(display_names):
            selected_device = display_names[choice - 1]
            print(f"Selected: {selected_device}")
            desired_width = int(input("Enter desired width: "))
            desired_height = int(input("Enter desired height: "))
            change_resolution(desired_width, desired_height, selected_device)
        else:
            print("Invalid selection.")
