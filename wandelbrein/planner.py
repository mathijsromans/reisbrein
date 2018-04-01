import logging
import time
import numpy
from datetime import timedelta
from geopy.distance import vincenty
from reisbrein.generator.generator import Generator
from reisbrein.generator.gen_common import FixTime
from reisbrein.primitives import Point, Location, TransportType, Segment
from reisbrein.userpreference import order_and_select
from reisbrein.models import UserTravelPreferences
from reisbrein.planner import Plan, RichRouter, Planner
from wandelbrein.models import Trail

logger = logging.getLogger(__name__)

WALKING_SPEED_KM_H = 3
WALKING_SPEED = WALKING_SPEED_KM_H / 3.6  # m/s


def get_default_trail():
    return Trail(
        title='GW660 / Bemmel: Bemmelse Waard',
        wandelpagina_id=17454,
        wandelpagina_url='http://www.wandelzoekpagina.nl/dagwandelingen/wandeling.php?wnummer=17454',
        nswandel_url='http://nswandel.nl/Album/GW-Bemmel-660/index.html',
        begin_lon=5.895478,
        begin_lat=51.8929925,
        end_lon=5.8954863,
        end_lat=51.8929898,
        distance=14158.4412752064,
    )


def sqr(x):
    return x*x


def get_weight(close_to_location, trail):
    avg_trail_gps = (0.5*(trail.begin_lat + trail.end_lat),
                     0.5*(trail.begin_lon + trail.end_lon))
    dist = vincenty(close_to_location.gps, avg_trail_gps).meters
    return 1/sqr(dist)


def get_trail(close_to_location):
    trails = Trail.objects.all()
    weights = [get_weight(close_to_location, t) for t in trails]
    s = sum(weights)
    if s == 0:
        return get_default_trail()  # no valid trails
    norm_weights = [w/s for w in weights]
    # print(norm_weights)
    return numpy.random.choice(trails, p=norm_weights)


class WandelbreinPlanner:

    def __init__(self, generator=Generator, router=RichRouter):
        self.generator = generator()
        self.router = router()

    def solve(self, start_loc_str, start_hike_time, user_preferences=UserTravelPreferences()):
        logger.info('BEGIN')
        log_start = time.time()

        reisbrein_planner = Planner()

        start = Point(Location(start_loc_str), start_hike_time - timedelta(hours=12))

        trail = get_trail(start.location)
        hike_start_loc = Location('wandeling vertrek', (trail.begin_lat, trail.begin_lon))
        hike_end_loc = Location('wandeling aankomst', (trail.end_lat, trail.end_lon))
        if hike_start_loc.distance_to(hike_end_loc).meters < 100:
            hike_end_loc = hike_start_loc
            hike_start_loc.loc_str = 'wandeling vertrek/aankomst'

        hike_start = Point(hike_start_loc, start_hike_time)
        hike_end = Point(hike_end_loc, start_hike_time + timedelta(seconds=trail.distance/WALKING_SPEED))
        end = Point(Location(start_loc_str), hike_end.time + timedelta(hours=12))

        logger.info('start=' + str(start))
        logger.info('hike_start=' + str(hike_start))
        logger.info('hike_end=' + str(hike_end))
        logger.info('end=' + str(end))

        edges = self.generator.create_edges(start, hike_start, FixTime.END)
        edges += self.generator.create_edges(hike_end, end, FixTime.START)
        hiking_segment = Segment(TransportType.WALK, hike_start, hike_end)
        hiking_segment.route_name = trail.title
        hiking_segment.map_url = trail.wandelpagina_url
        edges.append(hiking_segment)
        # for e in edges:
        #     print(e)

        plans = self.router.make_plans(start, end, edges)
        plans = list(filter(Planner.has_no_double_biking, plans))
        Planner.remove_unnecessary_waiting(plans, FixTime.START)
        order_and_select(plans, user_preferences)
        log_end = time.time()
        logger.info('END - time: ' + str(log_end - log_start))
        return plans, trail