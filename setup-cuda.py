import subprocess
import sys
import venv


def create_virtual_environment():
    # Create a virtual environment in the "venv" directory
    try:
        venv.create('venv', with_pip=True)
    except Exception as e:
        print(f"Failed to create virtual environment. Error: {e}")
        sys.exit(1)


def install_requirements():
    # Specify the path to the Python executable in the virtual environment
    if sys.platform == 'win32':
        python_bin = 'venv\\Scripts\\python'
    else:
        python_bin = 'venv/bin/python'
    
    # Use the Python interpreter in the virtual environment to run pip
    try:
        subprocess.run([python_bin, '-m', 'pip', 'install', '-r', 'requirements-cuda.txt'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install requirements. Error: {e}")
        sys.exit(1)

def main():
    create_virtual_environment()
    install_requirements()

if __name__ == '__main__':
    main()
