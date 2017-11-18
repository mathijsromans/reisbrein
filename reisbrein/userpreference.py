

from reisbrein.load_preference import *
from reisbrein.segment import TransportType

from numpy import array, zeros
from numpy.random import rand
from copy import copy


def order_by_preference(plans, user_preferences):
    keep_plans = []
    keep_weights = []
    weights = []
    for p in plans:
        w, corrected_weight = weight(p, user_preferences)
        weights.append(w)
#        if True:
        if corrected_weight < -750:
            keep_weights.append(w)
            keep_plans.append(copy(p))
    if keep_plans == []:
        aw = list((-array(weights)).argsort())
        for i in range(min(3,len(weights))):
            pi = aw.index(i)
            w, corrected_weight = weight(plans[pi], user_preferences)
            keep_weights.append(w)
            keep_plans.append(plans[pi])
        

    if keep_plans != []:
        zipped = list(zip(keep_weights, keep_plans))
        plans[:] = [p for _,p in sorted(zipped, reverse=True)]
    else:
        plans = []
    
#    plans.sort(key=weight, reverse=True)


def distance(option):
    w = 0
    for segment in option:
        w += segment.distance
    return w


def weight(option, user_preferences):
    
    preference_vec = load_user_preference(user_preferences)
    
    #option[0].from_vertex == user_preferences.home_address
    #option[-1].to_vertex == user_preferences.home_address
    
    
    Matrix, preference_list, conditions_list = load_dummy_preference_condition_matrix()
    
    condition_dict = {}
    # starts with car, starts with bike, includes car, includes bike, total time

    if option[0].transport_type == TransportType.CAR:
        condition_dict['starts with car'] = 1

        condition_dict['starts with bike'] = 0
        condition_dict['ends with bike'] = 0
    else:
        condition_dict['starts with car'] = 0

        # for now, since only car trips have only a single segment
        if len(option) > 1 and option[1].transport_type == TransportType.BIKE:
            condition_dict['starts with bike'] = 1
        else:
            condition_dict['starts with bike'] = 0
        if option[-1].transport_type == TransportType.BIKE:
            condition_dict['ends with bike'] = 1
        else:
            condition_dict['ends with bike'] = 0
    
    
    condition_dict['involves bike'] = 0
    condition_dict['involves car'] = 0
    condition_dict['involves train'] = 0
    condition_dict['involves walk'] = 0
    condition_dict['involves bus'] = 0
    condition_dict['total time'] = 0
    for s in option:
        if s.transport_type == TransportType.CAR:
            condition_dict['involves car'] = 1
        if s.transport_type == TransportType.WALK:
            condition_dict['involves walk'] = 1
        if s.transport_type == TransportType.BIKE:
            condition_dict['involves bike'] = 1
        if s.transport_type == TransportType.TRAIN:
            condition_dict['involves train'] = 1
        if s.transport_type == TransportType.BUS:
            condition_dict['involves bus'] = 1
        condition_dict['total time'] += s.distance



    # request weather API
    condition_dict['rainy'] = 1



    cd = condition_dict
    conditions = array( [cd[cond] for cond in conditions_list] )
    conditions_vector = Matrix.dot(conditions)
    
    
    preference = conditions_vector.dot(preference_vec)
    corrected_weight = preference - conditions_vector[0]
    return preference, corrected_weight


