

from numpy import array, zeros
from numpy.random import rand




preference_list = ['fast', 'mindrain','nocar','nobike','likewalk', 'likebike', 'no bike at start', 'no bike at end']



def load_dummy_preference_condition_matrix():
    
    conditions_list = ['total time','involves car','involves bike','involves walk','rainy', 'starts with bike', 'ends with bike']

    Matrix = zeros((len(preference_list),len(conditions_list)))
    
    pl = preference_list
    cl = conditions_list
    M = Matrix
    
    M[pl.index('fast'), cl.index('total time')] = -3
    M[pl.index('nocar'), cl.index('involves car')] = -1000
#    M[pl.index('nobike'), cl.index('involves bike')] = -100
    M[pl.index('no bike at start'), cl.index('starts with bike')] = -1000
    M[pl.index('no bike at end'), cl.index('ends with bike')] = -1000
    M[pl.index('likewalk'), cl.index('involves walk')] = 10
    M[pl.index('likebike'), cl.index('involves bike')] = 10
    M[pl.index('mindrain'), cl.index('rainy')] = -5

    

    M = array(M)
    return M, preference_list, conditions_list


def load_user_preference(pref):

    preference_vec = zeros(len(preference_list))
    preference_vec[preference_list.index('fast')] = pref.travel_time_importance/10.0
    preference_vec[preference_list.index('mindrain')] = 0
    preference_vec[preference_list.index('nocar')] = not(pref.has_car)
    preference_vec[preference_list.index('nobike')] = not(pref.has_bicycle)
    preference_vec[preference_list.index('likewalk')] = 0
    preference_vec[preference_list.index('likebike')] = pref.likes_to_bike/10.0
    preference_vec[preference_list.index('no bike at start')] = 1
    preference_vec[preference_list.index('no bike at end')] = 0
        
    return preference_vec

