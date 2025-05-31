class Vehicle:
    def __init__(self, xPos, veh_length):
        self.xPos = xPos
        self.veh_length = veh_length
        self.speed=0

    def getXPos(self):
        return self.xPos

    def setXPos(self, xPos):
        self.xPos = xPos

    def getVehLength(self):
        return self.veh_length

    def getSpeed(self):
        return self.speed

    def setSpeed(self, speed):
        self.speed = speed