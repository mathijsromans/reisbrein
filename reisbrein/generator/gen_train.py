from reisbrein.segment import Segment, TransportType

class TrainGenerator:
    def __init__(self):
        pass

    def create_segments(start, end):
        segments = [Segment(TransportType.BIKE, 'a', 'b', 20),
                 Segment(TransportType.TRAIN, 'a', 'c', 80),
                 Segment(TransportType.TRAIN, 'a', 'd', 50),
                 Segment(TransportType.TRAIN, 'b', 'c', 10),
                 Segment(TransportType.BIKE, 'c', 'e', 30),
                 Segment(TransportType.TRAIN, 'd', 'e', 40),
                 Segment(TransportType.CAR, 'a', 'e', 70)]
        return segments