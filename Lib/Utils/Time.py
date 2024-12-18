import time
class Time:
    __slots__ = 'dt','fixedDt','_prevTime','time','timeScale','realTime','_startTime','unscaledDeltaTime','frame'
    def __init__(self) -> None:
        self.dt = 0
        self.timeScale = 1
        self.fixedDt = 0.1


    def start(self):
        self.time = 0
        self.realTime = 0
        self.unscaledDeltaTime = 0
        self.frame = 0
        self._prevTime = self._startTime = time.perf_counter()

    
    def update(self):
        t = time.perf_counter()
        u = self.unscaledDeltaTime = (t - self._prevTime)
        self.dt = u * self.timeScale
        self.time += self.dt
        self._prevTime = t
        self.realTime = t - self._startTime
        self.frame += 1

    def getFPS(self):
        return 1 / self.unscaledDeltaTime if self.unscaledDeltaTime else 0
