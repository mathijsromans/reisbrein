from datetime import timedelta
from reisbrein.segment import Segment, TransportType
from reisbrein.planner import Point
from reisbrein.api.monotchapi import MonotchApi


class PublicGenerator:
    def __init__(self):
        self.monotch = MonotchApi()

    def create_edges(self, start, end, edges):
        response = self.monotch.search(start.location, end.location)
        for i in response['itineraries']:
            pass
            # edges.append(Segment(TransportType.TRAIN, s1, s2, 30))

