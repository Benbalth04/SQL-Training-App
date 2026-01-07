import subprocess
import os
import winreg
import sys

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
requirements_file = os.path.join(current_dir, 'requirements.txt')

# Define color codes for terminal output
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
RESET = '\033[0m' 

# Function to read requirements.txt and extract module names
def read_requirements(file_path):
    with open(file_path, 'r') as file:
        modules = [line.strip() for line in file.readlines() if line.strip()]
    return modules

# Function to install modules using HTTPS Automatic Configuration Script address with proxy
def install_modules(modules, proxy):
    for module in modules:
        # Check if the module is already installed
        result = subprocess.run([sys.executable, "-m", "pip", "show", module], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # If the module is not installed, proceed with installation
        if result.returncode != 0:
            print(f"Installing module: {GREEN}{module}{RESET}")
            
            install_command = [sys.executable, "-m", "pip", "install"]
            if proxy:
                install_command += [f"--proxy={proxy}"]
            install_command.append(module)
            
            subprocess.run(install_command)
        else:
            print(f"{GREEN}{module}{RESET} is already installed. Skipping...")

# Function to get proxy address from Windows registry
def get_proxy_address():
    proxy_address = None
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
        proxy_address, _ = winreg.QueryValueEx(key, "AutoConfigURL")
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Error: {e}")
    return proxy_address

if __name__ == '__main__':
    requirements_file = os.path.join(current_dir, 'requirements.txt')

    if not os.path.exists(requirements_file):
        with open(requirements_file, 'w') as file:
            print("Created requirements.txt file. Please add module names to install.")

    modules_to_install = read_requirements(requirements_file)

    proxy_address = get_proxy_address()

    if modules_to_install:
        install_modules(modules_to_install, proxy_address)
        print("Modules installation complete.")
    else:
        print("No modules to install.")