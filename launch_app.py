import subprocess
import sys

if __name__ == "__main__":
    print("🚀 Forcing Streamlit to launch inside the active Python environment...")
    # sys.executable gets the exact path of the Python running this script
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])