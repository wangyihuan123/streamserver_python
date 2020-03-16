import sys
import os
import signal
import time
from functools import partial
from stream_engine import StreamEngine

def run_main_loop():

    try:
        while True:
            # currently nothing to do here but spin
            time.sleep(0.05)
            continue
    except KeyboardInterrupt:
        pass

def main():
    engine = StreamEngine()

    engine.start()

    # blocking call
    run_main_loop()

    # Wait until engine (and by extension all registered controllers) have shut down in an orderly manner.
    engine.join(10.0)

if __name__ == "__main__":
    main()