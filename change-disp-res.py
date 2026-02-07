# pylint: disable=invalid-name
"""
Module for changing the display resolution on Windows.
"""

import ctypes

DM_PELSWIDTH = 0x00080000
DM_PELSHEIGHT = 0x00100000
DISP_CHANGE_SUCCESSFUL = 0
CDS_TEST = 0x00000002


def change_resolution(width: int, height: int) -> bool:
    """Change the screen resolution on Windows.

    Args:
        width: Desired screen width in pixels.
        height: Desired screen height in pixels.

    Returns:
        True if the resolution was changed successfully, False otherwise.
    """

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

    user32 = ctypes.windll.user32

    devmode = DEVMODE()
    devmode.dmSize = ctypes.sizeof(DEVMODE)  # pylint: disable=attribute-defined-outside-init

    # Enumerate current display settings
    if not user32.EnumDisplaySettingsW(None, -1, ctypes.byref(devmode)):
        print("Error: Could not retrieve current display settings.")
        return False

    devmode.dmPelsWidth = width  # pylint: disable=attribute-defined-outside-init
    devmode.dmPelsHeight = height  # pylint: disable=attribute-defined-outside-init
    devmode.dmFields = DM_PELSWIDTH | DM_PELSHEIGHT  # pylint: disable=attribute-defined-outside-init

    # Test if the resolution is supported
    result = user32.ChangeDisplaySettingsW(ctypes.byref(devmode), CDS_TEST)
    if result != DISP_CHANGE_SUCCESSFUL:
        print(f"Error: Resolution {width}x{height} is not supported.")
        return False

    # Apply the resolution change
    result = user32.ChangeDisplaySettingsW(ctypes.byref(devmode), 0)
    if result == DISP_CHANGE_SUCCESSFUL:
        print(f"Resolution changed to {width}x{height} successfully.")
        return True

    print(f"Error: Failed to change resolution. Error code: {result}")
    return False


if __name__ == "__main__":
    desired_width = int(input("Enter desired width: "))
    desired_height = int(input("Enter desired height: "))
    change_resolution(desired_width, desired_height)
