import datetime
from reisbrein.primitives import Segment, TransportType, Point
from reisbrein.generator.gen_public import PublicGenerator
from reisbrein.generator.gen_walk import WalkGenerator
from reisbrein.generator.gen_car import CarGenerator
from reisbrein.generator.gen_parkride import ParkRideGenerator


class Generator:
    def __init__(self):
        self.walk_generator = WalkGenerator()
        self.public_generator = PublicGenerator()
        self.car_generator = CarGenerator()
        self.parkride_generator = ParkRideGenerator()

    @staticmethod
    def remove_duplicates(edges):
        points = []
        for e in edges:
            points.append(e.from_vertex)
            points.append(e.to_vertex)
        locations = [p.location for p in points]

        # remove duplicate locations
        for index, l1 in enumerate(locations):
            for l2 in locations[index+1:]:
                if not l1 is l2 and l1 == l2:
                    for p in points:
                        if p.location is l2:
                            p.location = l1

        # remove duplicate points
        for index, p1 in enumerate(points):
            for p2 in points[index+1:]:
                if not p1 is p2 and p1 == p2:
                    for e in edges:
                        if e.from_vertex is p2:
                            e.from_vertex = p1
                        if e.to_vertex is p2:
                            e.to_vertex = p1

        # remove duplicate segments
        duplicates = set()
        for index, e1 in enumerate(edges):
            for e2 in edges[index+1:]:
                if e1.has_same_points_and_type(e2):
                    duplicates.add(e2)
        edges[:] = [e for e in edges if e not in duplicates]


    def create_edges(self, start, end):
        edges = []
        self.public_generator.create_edges(start, end, edges)
        self.parkride_generator.create_edges(start, end, edges)
        self.walk_generator.create_edges(start, end, edges)
        self.car_generator.create_edges(start, end, edges)
        self.remove_duplicates(edges)
        # for e in edges:
        #     print(e)
        return edges


class TestGenerator:

    def create_edges(self, start, end):
        b = Point('b', start.time+datetime.timedelta(seconds=20))
        c = Point('c', start.time+datetime.timedelta(seconds=80))
        d = Point('d', start.time+datetime.timedelta(seconds=50))
        edges = [Segment(TransportType.BIKE, start, b),
                 Segment(TransportType.TRAIN, start, c),
                 Segment(TransportType.TRAIN, start, d),
                 Segment(TransportType.TRAIN, b, c),
                 Segment(TransportType.BIKE, c, end),
                 Segment(TransportType.TRAIN, d, end),
                 Segment(TransportType.CAR, start, end)]
        return edges
