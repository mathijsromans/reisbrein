from enum import Enum
from reisbrein.primitives import Segment, TransportType

class FixTime(Enum):
    START = 0
    END = 1

def create_wait_and_move_segments(generator, start, end, fix, transport_type):
    edges = []
    segment, new_point = generator.create_segment(start, end, fix, transport_type)
    if fix == FixTime.START:  # move then wait
        if new_point.time < end.time:
            edges.append(segment)
            edges.append(Segment(TransportType.WAIT, new_point, end))
    else:  # wait then move
        if new_point.time > start.time:
            edges.append(Segment(TransportType.WAIT, start, new_point))
            edges.append(segment)
    return edges