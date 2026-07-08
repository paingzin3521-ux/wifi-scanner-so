# WiFi Scanner (Compiled Version)

This is a compiled version of the Ruijie Scanner, optimized for performance and security.

## How to run in Termux

To run this tool in Termux, follow these steps:

1. **Update and Install Dependencies:**
   ```bash
   pkg update && pkg upgrade
   pkg install python git clang
   pip install aiohttp pycryptodome
   ```

2. **Clone the Repository:**
   ```bash
   git clone https://github.com/paingzin3521-ux/wifi-scanner-so.git
   cd wifi-scanner-so
   ```

3. **Run the Tool:**
   ```bash
   python run.py
   ```

## Note
The core logic is compiled into `wifi.so` to prevent unauthorized access to the source code.
