# pylint: disable=invalid-name
"""
Module for changing the display resolution on Windows.
"""

import ctypes

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


def get_display_at_cursor(display_names: list[str]) -> str | None:
    """Find the display device name where the mouse cursor is located.

    Args:
        display_names: List of display device names from list_displays().

    Returns:
        The device name of the display under the cursor, or None if not found.
    """
    user32 = ctypes.windll.user32
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

    # Get cursor position
    class POINT(ctypes.Structure):  # pylint: disable=too-few-public-methods
        """Windows POINT structure."""

        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    cursor = POINT()
    user32.GetCursorPos(ctypes.byref(cursor))

    # Check which display contains the cursor
    for name in display_names:
        devmode = DEVMODE()
        devmode.dmSize = ctypes.sizeof(DEVMODE)  # pylint: disable=attribute-defined-outside-init
        if user32.EnumDisplaySettingsW(name, -1, ctypes.byref(devmode)):
            left = devmode.dmPositionX
            top = devmode.dmPositionY
            right = left + devmode.dmPelsWidth
            bottom = top + devmode.dmPelsHeight
            if left <= cursor.x < right and top <= cursor.y < bottom:
                return name

    return None


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
        cursor_display = get_display_at_cursor(display_names)
        if cursor_display:
            print(f"Mouse cursor is on: {cursor_display}")
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
