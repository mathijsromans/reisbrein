import heapq
import logging
from datetime import timedelta, datetime
from reisbrein.primitives import Segment, TransportType, Point, Location, get_equivalent
from reisbrein.api.monotchapi import MonotchApi

logger = logging.getLogger(__name__)


def get_or_add(container, item):
    existing = get_equivalent(container, item)
    if existing:
        return existing
    container.add(item)
    return item


class PublicGenerator:
    def __init__(self):
        self.monotch = MonotchApi()

    def create_edges(self, start, end, edges):
        translate = {
            'WALK': TransportType.WALK,
            'RAIL': TransportType.TRAIN,
            'TRAM': TransportType.TRAM,
            'BUS': TransportType.BUS,
        }
        response = self.monotch.search(start.location, end.location, start.time)
        points = set()
        points.update(s.from_vertex for s in edges)
        points.update(s.to_vertex for s in edges)
        locations = set(p.location for p in points)
        new_edges = []
        for it in response['itineraries']:
            prev_point = start
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
                    loc = end.location
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
                new_edges.append(segment)
                prev_point = p_end

        for s in new_edges:
            if not any(se.has_same_points_and_type(s) for se in edges):
                # logger.info('Adding segment ' + str(s))
                edges.append(s)


