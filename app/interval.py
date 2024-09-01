
class Interval():
    def __init__(self, value):
        self.value = int(value)
        self.artifact = None
        self.correction_methods = {
            "linear interpolation": 0,
            "cubic splain": 0,
            "moving average": 0,
            "pre mean": 0
        }
