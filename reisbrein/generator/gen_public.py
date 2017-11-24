import heapq
from datetime import timedelta, datetime
from reisbrein.primitives import Segment, TransportType, Point, Location
from reisbrein.api.monotchapi import MonotchApi


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
                    p_loc = end.location
                else:
                    p_loc = Location(p_loc_name, (p_loc_lat, p_loc_lon))
                p_time = datetime.fromtimestamp(int(leg['to']['arrival']) / 1000)
                p = Point(p_loc, p_time)
                if index != 0:  # walk to first stop will be added later
                    edges.append(Segment(transport_type, prev_point, p))
                prev_point = p
                # print('Adding edge' + str(edges[-1]))


