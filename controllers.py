import weakref
import threading


class Controller(object):
    """Base class for stream engine UI views/controllers"""

    # Commands passed from controllers to engine

    CMD_START = 1

    def __init__(self):
        self._engine = None

    def __del__(self):

        if self._engine is not None:
            # Unplug self from engine
            try:
                self._engine.deregister_controller(self)
            except ReferenceError:
                pass

    def _set_engine(self, engine):

        if engine is not None:
            # Use weakref proxies between engine and controllers to avoid circular reference leading to undead objects
            self._engine = weakref.proxy(engine)
        else:
            self._engine = None

    # Calls made by controller to direct behaviour of engine

    def signal_start_capture(self):
        if self._engine is not None:
            try:
                self._engine.post_command(Controller.CMD_START_CAPTURE)
            except ReferenceError:
                self._engine = None

    # Callbacks invoked by engine
    def notify_start_controller_threads(self):
        pass

    # publish the frame data(image)
    def notify_frame_data(self, image):
        pass


class ThreadedController(Controller):

    def __init__(self):

        # Controller.__init__(self)
        super().__init__()

        self._run_thread = False
        self._worker_thread = threading.Thread(target=self._thread_run)
        self._worker_thread.daemon = True

    def _thread_run(self):
        print("_thread_run!!!!")
        try:
            self.run()
        except Exception as e:
            print(e)
        except:
            print('Unhandled exception')

    def notify_start_controller_threads(self):
        # Start worker thread on notification of engine start
        if not self._run_thread:
            self._run_thread = True
            self._worker_thread.start()
