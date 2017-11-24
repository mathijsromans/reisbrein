

from numpy import array, zeros
from numpy.random import rand




preference_list = ['fast', 'mindrain','nocar','nobike','likewalk', 'likebike', 'no bike at start', 'no bike at end']



def load_dummy_preference_condition_matrix():
    
    conditions_list = ['total time','involves car','involves bike','involves own bike','involves walk','rainy', 'starts with bike', 'ends with bike']

    Matrix = zeros((len(preference_list),len(conditions_list)))
    
    pl = preference_list
    cl = conditions_list
    M = Matrix
    
    M[pl.index('fast'), cl.index('total time')] = -3
    M[pl.index('nocar'), cl.index('involves car')] = -1e10
    M[pl.index('nobike'), cl.index('involves own bike')] = -1e10
    M[pl.index('no bike at start'), cl.index('starts with bike')] = -1e10
    M[pl.index('no bike at end'), cl.index('ends with bike')] = -1e10
    M[pl.index('likewalk'), cl.index('involves walk')] = 30
    M[pl.index('likebike'), cl.index('involves bike')] = 30
    M[pl.index('mindrain'), cl.index('rainy')] = -20
    M = array(M)
    return M, preference_list, conditions_list


def load_user_preference(pref, option):
    preference_vec = zeros(len(preference_list))
    preference_vec[preference_list.index('fast')] = pref.travel_time_importance/10.0+0.1
    preference_vec[preference_list.index('mindrain')] = 1
    preference_vec[preference_list.index('nocar')] = not pref.has_car
    preference_vec[preference_list.index('nobike')] = not pref.has_bicycle
    preference_vec[preference_list.index('likewalk')] = 0
    preference_vec[preference_list.index('likebike')] = pref.likes_to_bike/10.0-0.5
    no_bike_at_start = str(option[0].from_vertex.location) != pref.home_address and\
                       str(option[-1].from_vertex.location) == pref.home_address  # going to home
    no_bike_at_end = str(option[0].from_vertex.location) == pref.home_address and\
                     str(option[-1].from_vertex.location) != pref.home_address  # going from home
    preference_vec[preference_list.index('no bike at start')] = no_bike_at_start
    preference_vec[preference_list.index('no bike at end')] = no_bike_at_end
    return preference_vec

