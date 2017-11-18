from datetime import timedelta, datetime
from reisbrein.segment import Segment, TransportType
from reisbrein.planner import Point, Location
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
                s1_loc = Location(legs[0]['from']['name'])
                s1_time = datetime.fromtimestamp(int(legs[0]['from']['departure']) / 1000)
                prev_point = Point(s1_loc, s1_time)
            for leg in legs:
                transport_type = translate.get(leg['mode'])
                if not transport_type:
                    continue
                    # print(leg)
                p_loc = Location(leg['to']['name'])
                p_time = datetime.fromtimestamp(int(leg['to']['arrival']) / 1000)
                p = Point(p_loc, p_time)
                edges.append(Segment(transport_type, prev_point, p, (p_time-prev_point.time).seconds/60))
                prev_point = p
                # print('Adding edge' + str(edges[-1]))


