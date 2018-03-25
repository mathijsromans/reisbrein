import copy
import logging
import time
from datetime import timedelta
from reisbrein.generator.generator import Generator
from reisbrein.generator.gen_common import FixTime
from reisbrein.graph import Graph, shortest_path
from reisbrein.primitives import Point, Location, TransportType, Segment
from reisbrein.userpreference import order_and_select
from reisbrein.models import UserTravelPreferences
from reisbrein.planner import Plan, RichRouter, Planner
from wandelbrein.models import Trail
from reisbrein.primitives import noon_today


logger = logging.getLogger(__name__)


class Hike:
    def __init__(self, start_loc, end_loc, time_delta):
        self.start_loc = start_loc
        self.end_loc = end_loc
        self.time_delta = time_delta


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


def get_hike():
    trails = Trail.objects.all()
    if trails:
        index = len(trails) // 2  # perfectly random choice
        trail = trails[index]
    else:
        trail = get_default_trail()
    return Hike(Location(trail.title + ' start', (trail.begin_lat, trail.begin_lon)),
                Location(trail.title + ' end', (trail.end_lat, trail.end_lon)), timedelta(hours=5))


class WandelbreinPlanner:

    def __init__(self, generator=Generator, router=RichRouter):
        self.generator = generator()
        self.router = router()

    def solve(self, start_loc_str, start_time, user_preferences=UserTravelPreferences()):
        logger.info('BEGIN')
        log_start = time.time()

        reisbrein_planner = Planner()

        hike = get_hike()
        hike_start = Point(hike.start_loc, start_time + timedelta(hours=12))
        print('hike_start=' + str(hike_start.location.full_str()))
        print('hike_end=' + str(hike.end_loc.full_str()))

        start_loc = Location(start_loc_str)
        plans = reisbrein_planner.solve(start_loc, hike_start.location, start_time, FixTime.START)
        best_start_hike_time = plans[0].route[-1].to_vertex.time

        start = Point(Location(start_loc_str), start_time)
        hike_start = Point(hike.start_loc, best_start_hike_time + timedelta(minutes=60))
        hike_end = Point(hike.end_loc, best_start_hike_time + hike.time_delta)
        end = Point(Location(start_loc_str), start_time + timedelta(hours=12))

        logger.info('start=' + str(start))
        logger.info('hike_start=' + str(hike_start))
        logger.info('hike_end=' + str(hike_end))
        logger.info('end=' + str(end))

        edges = self.generator.create_edges(start, hike_start, FixTime.END)
        hiking_segment = Segment(TransportType.WALK, hike_start, hike_end)
        edges.append(hiking_segment)
        edges += self.generator.create_edges(hike_end, end, FixTime.START)
        # for e in edges:
        #     print(e)

        routes = self.router.make_routes(start, end, edges)
        routes = list(filter(Planner.has_no_double_biking, routes))
        Planner.remove_unnecessary_waiting(routes, FixTime.START)
        plans = [Plan(r) for r in routes]
        order_and_select(plans, user_preferences)
        log_end = time.time()
        logger.info('END - time: ' + str(log_end - log_start))
        return plans