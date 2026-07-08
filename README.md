# WiFi Scanner (Compiled Version)

This is a compiled version of the Ruijie Scanner, optimized for performance and security.

## How to run in Termux

To run this tool in Termux, follow these steps:

1. **Update and Install Dependencies:**
   ```bash
   pkg update && pkg upgrade
   pkg install python git clang make -y
   pip install aiohttp pycryptodome cython
   ```

2. **Clone the Repository:**
   ```bash
   git clone https://github.com/paingzin3521-ux/wifi-scanner-so.git
   cd wifi-scanner-so
   ```

3. **Compile on your device:**
   (This step ensures the code works on your specific phone architecture)
   ```bash
   python setup.py build_ext --inplace
   ```

4. **Run the Tool:**
   ```bash
   python run.py
   ```

## Note
After compilation, `wifi.so` is created specifically for your device. You can delete `wifi.py` and `setup.py` if you want to keep only the compiled version.
