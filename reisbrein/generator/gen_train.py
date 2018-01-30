import csv
import heapq
from datetime import timedelta
from geopy.distance import vincenty
from reisbrein.primitives import Segment, TransportType, Point


def skip_first(iterable):
    it = iter(iterable)
    next(it, None)
    for item in it:
        yield item

class Station:
    def __init__(self, row):
        self.id = row[0]
        self.code = row[1]
        self.uic = row[2]
        self.naam = row[3]
        self.middel_naam = row[4]
        self.korte_naam = row[5]
        self.friendly = row[6]
        self.land = row[7]
        self.type = row[8]
        self.geo_lat = row[9]
        self.geo_lng = row[10]

    def gps(self):
        return self.geo_lat, self.geo_lng

    def __str__(self):
        return 'Station: ' + self.naam

class TrainGenerator:
    def __init__(self):
        self.stations=[]
        with open('data/stations-nl-2015-08_from_openov_nl.csv', 'rt', encoding='utf-8') as stations_file:
            reader = csv.reader(stations_file, delimiter=';', quotechar='|')
            for row in skip_first(reader):
                self.stations.append(Station(row))
        # print(list(map(str, self.stations)))

    def closest_stations(self, location, n):
        return heapq.nsmallest(n, self.stations, lambda x: vincenty(location.gps(), x.gps()).meters)

    def create_edges(self, start, end, fix_time, edges):
        st_start_loc = self.closest_stations(start.location, 2)
        st_end_loc = self.closest_stations(end.location, 2)
        stops_1 = [Point(s, start.time + timedelta(minutes=50)) for s in st_start_loc]
        stops_2 = [Point(s, start.time + timedelta(minutes=140)) for s in st_end_loc]
        for s1 in stops_1:
            for s2 in stops_2:
                # take the train
                edges.append(Segment(TransportType.TRAIN, s1, s2))

