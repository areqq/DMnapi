from enigma import eTimer as Timer

try:
    Timer().callback
except AttributeError:
    # eTimer has changed interface on DMM images
    class  eTimer(object):
        def __init__(self):
            self._timer = Timer()
            
        def __getattr__(self, key):
            if key == "callback" and not hasattr(self._timer,"callback"):
                timeout = self._timer.timeout
                timeout.append = timeout.connect
                return timeout
            else:
                return getattr(self._timer, key)
else:
    eTimer = Timer
