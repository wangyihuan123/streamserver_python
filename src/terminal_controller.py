from controllers import ThreadedController
import sys
import os
import signal
import termios
import time


class TerminalController(ThreadedController):
    """Control and display status messages for an ImageCaptureEngine instance from a terminal window.  Doesn't actually display images"""

    def __init__(self):
        super().__init__()
        self._running = True
        print("init terminal controller")

    def run(self):
        print("start terminal thread")
        # Modify terminal settings to a)not buffer input characters till RETURN key recieved b) not echo input characters.
        # Linux specific code, use msvcrt on Windows
        try:
            orig_settings = termios.tcgetattr(sys.stdin)
            new_settings = list(orig_settings)
            new_settings[3] = new_settings[3] & ~(termios.ICANON | termios.ECHO)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)
        except termios.error:
            # Modification not available in particular terminal/terminal emulator we're currently running in.
            orig_settings = None

        try:
            try:
                while self._running:

                    k = sys.stdin.read(1)[0]  # Blocking call

                    # Mask out all but the equivalent ASCII key code in the low byte
                    k = ord(k) & 0xFF

                    if k == 32:  # SPACE to start stream
                        print("space from terminal controller")
                        self.signal_start_stream()
                    elif k == ord('s'):  # stop
                        self.signal_stop_stream()
                    elif k == ord('r'):  # record
                        self.signal_start_record()
                    elif k == ord('e'):  # end
                        self.signal_stop_record()

                    elif k == ord('q'):
                        self.signal_shutdown()
                        self._running = False

            except KeyboardInterrupt:
                pass

        finally:
            if orig_settings is not None:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)

    def notify_shutdown(self):

        # Interrupt stdin key reading loop in run().  thread.interrupt_main() doesn't work, but the following does.
        os.kill(os.getpid(), signal.SIGINT)
