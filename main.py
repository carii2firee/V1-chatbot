# What to run through terminal *Note for myself* (cd "C:\Users\carii\Downloads\voice_assistant folder")
import sys
from cli_assistant import run_cli_assistant  #
from voice_gui_assistant import run_voice_assistant_gui

def main():
    if '--cli' in sys.argv:
        run_cli_assistant()
    else:
        # Default: launch GUI voice assistant
        print("Starting GUI Voice Assistant...")
        run_voice_assistant_gui()

if __name__ == '__main__':
    main()