import heapq
from datetime import timedelta, datetime
from reisbrein.primitives import Segment, TransportType, Point, Location, get_equivalent
from reisbrein.api.monotchapi import MonotchApi


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
        for it in response['itineraries']:
            legs = it['legs']
            if legs:
                prev_point = start
            for index, leg in enumerate(legs):
                transport_type = translate.get(leg['mode'])
                if not transport_type:
                    continue
                    # print(leg)
                p_loc_name = leg['to']['name']
                p_loc_lat = float(leg['to']['lat'])
                p_loc_lon = float(leg['to']['lon'])

                if p_loc_name == 'Destination':
                    loc = end.location
                else:
                    loc_new = Location(p_loc_name, (p_loc_lat, p_loc_lon))
                    loc = get_or_add(locations, loc_new)
                p_time = datetime.fromtimestamp(int(leg['to']['arrival']) / 1000)
                p_new = Point(loc, p_time)
                p = get_or_add(points, p_new)
                if index != 0:  # walk to first stop will be added later
                    s1 = Segment(transport_type, prev_point, p)
                    if not any(s1.has_same_points_and_type(s) for s in edges):
                        edges.append(s1)
                prev_point = p
                # print('Adding edge' + str(edges[-1]))


