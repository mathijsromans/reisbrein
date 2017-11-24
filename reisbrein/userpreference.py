from reisbrein.load_preference import *
from reisbrein.primitives import TransportType
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

def order_and_select(plans, user_preferences):
    for p in plans:
        p.score = score(p.route, user_preferences)
    remove_really_bad_plans(plans)
    remove_long_plans(plans)
    plans.sort(key=lambda plan: plan.score, reverse=True)

def get_conditions(option):
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
    for s in option:
        if s.transport_type == TransportType.CAR:
            condition_dict['involves car'] = 1
        if s.transport_type == TransportType.WALK:
            condition_dict['involves walk'] = 1
        if s.transport_type == TransportType.BIKE or s.transport_type == TransportType.OVFIETS:
            condition_dict['involves bike'] += 0.0 + s.distance / 30.0
        if s.transport_type == TransportType.BIKE:
            condition_dict['involves own bike'] = 1
        if s.transport_type == TransportType.TRAIN:
            condition_dict['involves train'] = 1
        if s.transport_type == TransportType.BUS:
            condition_dict['involves bus'] = 1
        condition_dict['total time'] += s.distance
        if s.weather == 'rainy':
            condition_dict['rainy'] += 1
    return condition_dict

def score(option, user_preferences):
    preference_vec = load_user_preference(user_preferences, option)
    Matrix, preference_list, conditions_list = load_dummy_preference_condition_matrix()
    cd = get_conditions(option)
    conditions = array( [cd[cond] for cond in conditions_list] )
    conditions_vector = Matrix.dot(conditions)
    preference = conditions_vector.dot(preference_vec)
    # print(str(list(map(str, option))) + ' has score ' + str(preference))
    return preference


