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
                if start_time - prev_point.time > timedelta(seconds=1):
                    p_start = get_or_add(points, Point(prev_point.location, start_time))
                    new_edges.append(Segment(TransportType.WAIT, prev_point, p_start))
                else:
                    p_start = prev_point
                new_edges.append(Segment(transport_type, p_start, p_end))
                prev_point = p_end

        for s in new_edges:
            if not any(se.has_same_points_and_type(s) for se in edges):
                logger.info('Adding segment ' + str(s))
                edges.append(s)


