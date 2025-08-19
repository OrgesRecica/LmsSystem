import subprocess
import sys
import os

def run_streamlit():
    """Run the Streamlit application"""
    try:
        # Change to the directory containing the streamlit app
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Run streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
    except KeyboardInterrupt:
        print("\nStreamlit application stopped.")

if __name__ == "__main__":
    run_streamlit()
