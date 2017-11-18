from datetime import timedelta, datetime
from reisbrein.segment import Segment, TransportType
from reisbrein.planner import Point, Location
from reisbrein.api.monotchapi import MonotchApi


class PublicGenerator:
    def __init__(self):
        self.monotch = MonotchApi()

    def create_edges(self, start, end, edges):
        translate = {
            'RAIL': TransportType.TRAIN,
            'TRAM': TransportType.TRAM,
            'BUS': TransportType.BUS,
        }
        response = self.monotch.search(start.location, end.location, start.time)
        for it in response['itineraries']:
            for leg in it['legs']:
                transport_type = translate.get(leg['mode'])
                if not transport_type:
                    continue
                    # print(leg)
                s1_loc = Location(leg['from']['name'])
                s2_loc = Location(leg['to']['name'])
                s1_time = datetime.fromtimestamp(int(leg['from']['departure'])/1000)
                s2_time = datetime.fromtimestamp(int(leg['to']['arrival']) / 1000)
                s1 = Point(s1_loc, s1_time)
                s2 = Point(s2_loc, s2_time)
                edges.append(Segment(transport_type, s1, s2, (s2_time-s1_time).seconds/60))
                # print('Adding edge' + str(edges[-1]))


