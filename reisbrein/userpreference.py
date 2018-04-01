from reisbrein.load_preference import *
from reisbrein.primitives import TransportType
from reisbrein.generator.gen_common import FixTime
from numpy import array, zeros
import heapq

MIN_SHORT_PLANS = 3


def remove_long_plans(plans):
    """Remove plans that are too long to make sure we keep a good resolution on the good plans."""
    complex_plans = [p for p in plans if len(p.route) > 1]
    if complex_plans:
        shortest_time = min(complex_plans, key=lambda x: x.travel_time).travel_time
        short_plans = [p for p in plans if p.travel_time < 2 * shortest_time]

        # keep at least MIN_SHORT_PLANS plans
        if len(short_plans) < MIN_SHORT_PLANS:
            short_plans = heapq.nsmallest(MIN_SHORT_PLANS, plans, lambda x: x.travel_time)

        plans[:] = short_plans


def remove_really_bad_plans(plans):
    plans[:] = [p for p in plans if p.score > -1e8]


def order_and_select(plans, user_preferences, fix_time):
    for p in plans:
        p.score = score(p.route, user_preferences, fix_time)
    remove_really_bad_plans(plans)
    remove_long_plans(plans)
    plans.sort(key=lambda plan: plan.score, reverse=True)
    del plans[user_preferences.show_n_results:]


def get_conditions(option, fix_time):
    condition_dict = {}
    # starts with car, starts with bike, includes car, includes bike, total time

    if option[0].transport_type == TransportType.CAR:
        condition_dict['starts with car'] = 1
        condition_dict['starts with bike'] = 0
        condition_dict['ends with bike'] = 0
    else:
        condition_dict['starts with car'] = 0

        # for now, since only car trips have only a single segment
        if (len(option) > 1 and option[1].transport_type == TransportType.BIKE ) or (option[0].transport_type == TransportType.BIKE):
            condition_dict['starts with bike'] = 1
        else:
            condition_dict['starts with bike'] = 0
        if option[-1].transport_type == TransportType.BIKE and len(option)>2:
            condition_dict['ends with bike'] = 1
        else:
            condition_dict['ends with bike'] = 0


    condition_dict['involves bike'] = 0
    condition_dict['involves own bike'] = 0
    condition_dict['involves car'] = 0
    condition_dict['involves train'] = 0
    condition_dict['involves walk'] = 0
    condition_dict['involves bus'] = 0
    condition_dict['total time'] = 0
    condition_dict['rainy'] = 0
    condition_dict['time at home'] = 0
    condition_dict['num transfers'] = 0
    condition_dict['car distance'] = 0
    condition_dict['train distance'] = 0
    condition_dict['tram distance'] = 0
    condition_dict['bus distance'] = 0

    for s in option:
        if s.transport_type in [TransportType.CAR, TransportType.TRAIN, TransportType.BUS, TransportType.TRAM]: 
            condition_dict['num transfers'] += 1
        if s.transport_type == TransportType.CAR:
            condition_dict['involves car'] = 1
            condition_dict['car distance'] += s.time_sec / 60.0
        if s.transport_type == TransportType.WALK:
            condition_dict['involves walk'] = 1
        if s.transport_type == TransportType.BIKE or s.transport_type == TransportType.OVFIETS:
            condition_dict['involves bike'] += 0.0 + s.time_sec / 60.0
        if s.transport_type == TransportType.BIKE:
            condition_dict['involves own bike'] = 1
        if s.transport_type == TransportType.TRAIN:
            condition_dict['involves train'] = 1
            condition_dict['train distance'] += s.time_sec / 60.0
        if s.transport_type == TransportType.TRAM:
            #condition_dict['involves tram'] = 1
            condition_dict['tram distance'] += s.time_sec / 60.0
        if s.transport_type == TransportType.BUS:
            condition_dict['bus distance'] += s.time_sec / 60.0
            condition_dict['involves bus'] = 1
        condition_dict['total time'] += s.time_sec / 60
        if s.weather == 'rainy':
            condition_dict['rainy'] += 1

    if option[0].transport_type == TransportType.WAIT:
        condition_dict['time at home'] = option[0].time_sec / 60

    # if an end is not fixed, waiting there should not be counted as travel time
    if option[0].transport_type == TransportType.WAIT and fix_time != FixTime.START:
        condition_dict['total time'] -= option[0].time_sec / 60
    if option[-1].transport_type == TransportType.WAIT and fix_time != FixTime.END:
        condition_dict['total time'] -= option[-1].time_sec / 60

    return condition_dict

def score(option, user_preferences, fix_time):
    preference_vec = load_user_preference(user_preferences, option)
    Matrix, preference_list, conditions_list = load_dummy_preference_condition_matrix()
    cd = get_conditions(option, fix_time)
    conditions = array( [cd[cond] for cond in conditions_list] )
    conditions_vector = Matrix.dot(conditions)
    preference = conditions_vector.dot(preference_vec)
    #print(conditions)
    #print(conditions_vector)
    #print(preference_vec)
    #print(preference)
    # print(str(list(map(str, option))) + ' has score ' + str(preference))
    return preference


