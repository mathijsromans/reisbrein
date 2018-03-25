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

logger = logging.getLogger(__name__)


class Hike:
    def __init__(self, start_loc, end_loc, time_delta):
        self.start_loc = start_loc
        self.end_loc = end_loc
        self.time_delta = time_delta


def get_hikes():
    return [
        Hike(Location('Zeewolde'), Location('Swifterbant'), timedelta(hours=5)),
        Hike(Location('Lage Vuursche'), Location('Hoge Vuursche'), timedelta(hours=3)),
    ]


class WandelbreinPlanner:

    def __init__(self, generator=Generator, router=RichRouter):
        self.generator = generator()
        self.router = router()

    def solve(self, start_loc_str, start_time, user_preferences=UserTravelPreferences()):
        logger.info('BEGIN')
        log_start = time.time()

        reisbrein_planner = Planner()

        hike = get_hikes()[0]
        hike_start = Point(hike.start_loc, start_time + timedelta(hours=12))

        plans = reisbrein_planner.solve(start_loc_str, hike_start.location.loc_str, start_time, FixTime.START)
        best_start_hike_time = plans[0].route[-1].to_vertex.time

        start = Point(Location(start_loc_str), start_time)
        hike_start = Point(hike.start_loc, best_start_hike_time + timedelta(minutes=30))
        hike_end = Point(hike.end_loc, best_start_hike_time + hike.time_delta)
        end = Point(Location(start_loc_str), start_time + timedelta(hours=12))

        print('start=' + str(start))
        print('hike_start=' + str(hike_start))
        print('hike_end=' + str(hike_end))
        print('end=' + str(end))

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
        # print(str(routes))
        log_end = time.time()
        logger.info('END - time: ' + str(log_end - log_start))
        return plans