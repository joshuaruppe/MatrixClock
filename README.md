
# MatrixPortal M4 "Matrix Code" Clock

This project displays a digital clock on the left side of a 64×32 RGB LED matrix, separated by a thin green divider line, with a “Matrix rain” animation on the right side. The code runs on an Adafruit MatrixPortal M4 (or similar CircuitPython-compatible boards with the MatrixPortal library).

## Features

- **Clock on the Left**: Shows current hour and minute in two large labels.
- **Green Divider**: A single-column divider line.
- **Matrix Rain on the Right**: Randomized “falling columns” animation inspired by “The Matrix” aesthetic.
- **Wi-Fi Time Sync**: Fetches current time from an NTP server based on your `secrets.py` configuration.

## Hardware

- **Adafruit MatrixPortal M4**
  - [Product Page](https://www.adafruit.com/product/4745)
  - This board has an ESP32 co-processor for Wi-Fi and an M4 microcontroller to drive the matrix.
- **64×32 RGB LED Matrix Panel**
  - [Adafruit 64×32 LED Matrix](https://www.adafruit.com/product/2277)
  - Other panel sizes could work with code adjustments (width, height).
- **5V Power Supply**
  - High-current supply recommended (e.g., 5V 4A or above).
- **USB Cable**
  - For programming and powering the MatrixPortal from your computer or USB power supply.

## Software / Libraries / Required Files

- **CircuitPython 9.2.1** (or matching 9.x release)
- **Adafruit CircuitPython Library Bundle (9.x)**  
  Specifically you need:
  - `adafruit_display_text`
  - `adafruit_matrixportal`
  - `adafruit_portalbase`
  - `terminalio`
  - `displayio` (part of CircuitPython core)
- A `secrets.py` file on the `CIRCUITPY` root containing your Wi-Fi credentials and timezone:
  
  ```python

  secrets = {
      "ssid": "Your-WiFi-SSID",
      "password": "Your-WiFi-Password",
      "timezone": "America/New_York"  # or your preferred IANA timezone
  }
  ```

- A settings.toml file on the CIRCUITPY root for Adafruit IO authentication:

  ```toml

  AIO_USERNAME = "your_username"
  AIO_KEY = "your_key"

  ```

## Setup & Installation

1. **Install CircuitPython 9.x on the MatrixPortal board.**  
   Follow the instructions at [CircuitPython.org](https://circuitpython.org/).

2. **Download the 9.x Library Bundle** from the [Adafruit CircuitPython Libraries](https://circuitpython.org/libraries).  
   Unzip and copy the required libraries into the `lib` folder on your `CIRCUITPY` drive.

3. **Copy `code.py`** (this project’s main file) to the root of the `CIRCUITPY` drive.

   Your `CIRCUITPY` drive should now have something like:

   ```plaintext
   CIRCUITPY/
   ├── code.py
   ├── secrets.py
   ├── settings.toml
   └── lib/
       ├── adafruit_display_text/
       ├── adafruit_matrixportal/
       ├── adafruit_portalbase/
       ...
   ```

4. **Provide Power & Connect the Matrix**  
   - Plug the matrix cable into the MatrixPortal’s IDC connector.  
   - Use a 5V power supply that can supply sufficient current for the LED matrix.

5. **Eject / Unmount `CIRCUITPY` and reset the board.**  
   - The MatrixPortal will connect to Wi-Fi, sync the time from NTP, and start displaying the clock and the Matrix rain animation.

## Usage & Configuration

- **Time Sync**: The board uses your `secrets.py` credentials to connect to Wi-Fi, then fetches time from an NTP server for the timezone specified.
- **Dimensions**: The code is set for a 64×32 matrix. If you have a different size panel, adjust `WIDTH` and `HEIGHT` constants near the top of `code.py`.
- **Matrix Rain Characters**: The array `MATRIX_CHARS` in the code defines which characters get “rained.” In the default code, each non-space character simply appears as a green pixel (no actual letter glyph rendering). You can customize or reduce them for variety or performance reasons.
- **Animation Speed**: Tweak `UPDATE_INTERVAL` to control how quickly columns update (default is 0.05 seconds). You can also tweak column speeds and the number of columns.

## Additional Notes

- If you see an error about `'NoneType' object has no attribute 'get'`, confirm that `secrets.py` is present, your library versions match 9.x, and you have `"timezone"` spelled correctly.
- For truly rendering letters/symbols (instead of single green dots), you’d need to update the code to draw text glyphs instead of pixels in a bitmap.

## License

This project is available under the MIT License. See `LICENSE` for details.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests for:

- Bug fixes
- Feature enhancements
- Documentation improvements
