from threading import Thread, Event

class Sthread(Thread):
    def __init__(self,  *args, **kwargs):
        super(Sthread, self).__init__(*args, **kwargs)
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    def isStopped(self):
        return self._stop_event.is_set()