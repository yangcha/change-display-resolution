# Change Display Resolution

A Python script to change display resolution on Windows systems with multi-monitor support.

## Features

- List all active display devices
- Automatically detect which display your mouse cursor is on
- Interactively select which display to configure
- Change resolution for any connected display
- Validates resolution support before applying changes

## Requirements

- Windows OS
- Python 3.10+ (uses modern type hints with `|` union operator)

## Usage

Run the script:

```bash
python change-disp-res.py
```

The script will:
1. List all active displays
2. Show which display your mouse cursor is currently on
3. Prompt you to select a display
4. Ask for desired width and height
5. Apply the resolution change

## Example

```
Active displays:
  \\.\DISPLAY1 - NVIDIA GeForce RTX 3080
  \\.\DISPLAY2 - Generic PnP Monitor

  1. \\.\DISPLAY1
  2. \\.\DISPLAY2

Mouse cursor is on: \\.\DISPLAY1

Select display (1-2): 1
Selected: \\.\DISPLAY1
Enter desired width: 1920
Enter desired height: 1080
Resolution changed to 1920x1080 successfully.
```

## API Usage

You can also import and use the functions programmatically:

```python
from change_disp_res import list_displays, get_display_at_cursor, change_resolution

# List all displays
displays = list_displays()

# Find display under cursor
cursor_display = get_display_at_cursor(displays)

# Change resolution
change_resolution(1920, 1080, displays[0])
```
