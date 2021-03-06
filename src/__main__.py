"""
This is the main module. It basically checks that there is a hapi api key, asks for one if there
is not one, and launches the main GUI. That's about it.
"""
from multiprocessing import freeze_support
import sys

from startup import fix_cwd, check_version

check_version()
fix_cwd()

from app import run

if __name__ == '__main__':
    import traceback
    freeze_support()
    try:
        sys.exit(run())
    except TypeError as err:
        print("Encountered type error:\n" + str(err))
        traceback.print_exc()
    except Exception as err:
        print("Encountered an error: \n" + str(err))
        traceback.print_exc()
