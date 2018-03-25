import heapq
import logging
from datetime import timedelta, datetime
from reisbrein.primitives import Segment, TransportType, Point, Location, get_equivalent
from reisbrein.generator.gen_common import FixTime

logger = logging.getLogger(__name__)


def get_or_add(container, item):
    existing = get_equivalent(container, item)
    if existing:
        return existing
    container.add(item)
    return item


class PublicGeneratorRequest:
    def __init__(self, start, end, fix_time, routing_api):
        self.start = start
        self.end = end
        self.fix_time = fix_time
        self.routing_api = routing_api
        req_time = self.start.time if self.fix_time == FixTime.START else self.end.time
        self.search_request = self.routing_api.add_search_request(self.start.location,
                                                                  self.end.location,
                                                                  req_time,
                                                                  self.fix_time)

    def finish(self, edges):
        translate = {
            'WALK': TransportType.WALK,
            'RAIL': TransportType.TRAIN,
            'TRAM': TransportType.TRAM,
            'BUS': TransportType.BUS,
            }
        points = set()
        points.update(s.from_vertex for s in edges)
        points.update(s.to_vertex for s in edges)
        locations = set(p.location for p in points)
        new_edges = []
        for it in self.search_request.result['itineraries']:
            prev_point = self.start
            for index, leg in enumerate(it['legs']):
                transport_type = translate.get(leg['mode'])
                if not transport_type:
                    continue
                    # print(leg)
                start_time = datetime.fromtimestamp(int(leg['startTime']) / 1000)
                end_time = datetime.fromtimestamp(int(leg['endTime']) / 1000)
                if 'departure' in leg['to']:  # plannerstack can include 1 second of waiting, which we want to ignore
                    end_dep_time = datetime.fromtimestamp(int(leg['to']['departure']) / 1000)
                    if end_dep_time - end_time <= timedelta(seconds=1):
                        end_time = end_dep_time
                p_loc_name = leg['to']['name']
                if p_loc_name == 'Destination':
                    loc = self.end.location
                else:
                    p_loc_lat = float(leg['to']['lat'])
                    p_loc_lon = float(leg['to']['lon'])
                    loc = get_or_add(locations, Location(p_loc_name, (p_loc_lat, p_loc_lon)))
                p_end = get_or_add(points, Point(loc, end_time))
                if index == 0:  # walk to first stop will be added later
                    prev_point = p_end
                    continue
                # logger.info('Arrival time ' + str(int(leg['to']['arrival'])) + ' ' + str(start_time))
                if start_time > prev_point.time:
                    p_start = get_or_add(points, Point(prev_point.location, start_time))
                    new_edges.append(Segment(TransportType.WAIT, prev_point, p_start))
                else:
                    p_start = prev_point
                segment = Segment(transport_type, p_start, p_end)
                if 'routeShortName' in leg:
                    segment.route_name = leg['routeShortName']
                if 'platformCode' in leg['from']:
                    segment.platform_code = leg['from']['platformCode']
                new_edges.append(segment)
                prev_point = p_end

        for s in new_edges:
            if not any(se.has_same_points_and_type(s) for se in edges):
                # logger.info('Adding segment ' + str(s))
                edges.append(s)


class MockPublicGeneratorRequest:
    def __init__(self, start, end, fix_time):
        self.start = start
        self.end = end
        self.fix_time = fix_time

    def finish(self, edges):
        loc_1 = Location.midpoint(self.start.location, self.end.location, 0.01)
        loc_2 = Location.midpoint(self.start.location, self.end.location, 0.5)
        loc_3 = Location.midpoint(self.start.location, self.end.location, 0.99)
        loc_4 = self.end.location

        if self.fix_time == FixTime.START:
            start_time = self.start.time
        else:
            start_time = self.end.time - timedelta(hours=1)

        time_1 = start_time + 0.25 * timedelta(hours=1)
        time_2 = start_time + 0.5 * timedelta(hours=1)
        time_3 = start_time + 0.75 * timedelta(hours=1)
        time_4 = start_time + 0.99 * timedelta(hours=1)
        p1 = Point(loc_1, time_1)
        p2 = Point(loc_2, time_2)
        p3 = Point(loc_3, time_3)
        p4 = Point(loc_4, time_4)
        edges += [
            Segment(TransportType.BUS, p1, p2),
            Segment(TransportType.TRAIN, p2, p3),
            Segment(TransportType.WALK, p3, p4),
            ]


class PublicGenerator:

    def __init__(self, routing_api):
        self.routing_api = routing_api

    def prepare_request(self, start, end, fix_time):
        return PublicGeneratorRequest(start, end, fix_time, self.routing_api)

    def do_requests(self):
        self.routing_api.do_requests()



class MockPublicGenerator:

    def __init__(self):
        pass

    def prepare_request(self, start, end, fix_time):
        return MockPublicGeneratorRequest(start, end, fix_time)

    def do_requests(self):
        pass