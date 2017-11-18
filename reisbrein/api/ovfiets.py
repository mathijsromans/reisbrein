
class OvFietsStations(object):

    def __init__(self):
        self.stations = OvFietsStations.load_ovfiets_stations()

    @staticmethod
    def load_ovfiets_stations():
        print('load')
        stations = []
        with open('data/ovfiets_stations.txt') as f:
            lines = f.readlines()
            for line in lines:
                    stations.append(line.rstrip().lower())
        return stations

