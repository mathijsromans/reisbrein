from reisbrein.generator.gen_common import get_locations
from reisbrein.primitives import Vehicle, VehicleType, TransportType

class OvFietsStations(object):

    def __init__(self):
        self.stations = OvFietsStations.load_ovfiets_stations()

    def has_ovfiets(self, location):
        return location.loc_str.lower() in self.stations

    def add_default_ovfiets_positions(self, vehicle_positions, segments):
        for location in get_locations(segments):
            if self.has_ovfiets(location):
                vehicle_positions.add_vehicle(location, Vehicle(TransportType.BIKE, VehicleType.OVFIETS))
        return vehicle_positions

    @staticmethod
    def load_ovfiets_stations():
        # print('load')
        stations = []
        with open('data/ovfiets_stations.txt') as f:
            lines = f.readlines()
            for line in lines:
                    stations.append(line.rstrip().lower())
        return stations

