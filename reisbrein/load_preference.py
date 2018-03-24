from numpy import array, zeros

preference_list = [
    'fast',
    'noliketransfer',
    'mindrain',
    'nocar',
    'nobike',
    'likewalk',
    'likebike',
    'no bike at start',
    'no bike at end',
    'save CO2',
]


def load_dummy_preference_condition_matrix():
    
    conditions_list = [
        'total time',  # time measured in minutes
        'time at home',  # time measured in minutes
        'involves car',
        'involves bike',
        'involves own bike',
        'involves walk',
        'rainy',
        'starts with bike',
        'ends with bike',
        'num transfers',
        'car distance',
        'train distance',
        'bus distance',
        'tram distance',
    ]
    

    Matrix = zeros((len(preference_list),len(conditions_list)))
    
    pl = preference_list
    cl = conditions_list
    M = Matrix
    
    
    # from Kamiel, value of time per minute --> costs per hour
    # car 10.098774858, train 1.012834843, bus 3.4614907766, tram 0.506417422


    CO2_conversion_number = -18/60. #18=minute --> hour
    M[pl.index('save CO2'), cl.index('car distance')] = CO2_conversion_number*10.098774858
    M[pl.index('save CO2'), cl.index('train distance')] = CO2_conversion_number*1.012834843
    M[pl.index('save CO2'), cl.index('tram distance')] = CO2_conversion_number*0.506417422
    M[pl.index('save CO2'), cl.index('bus distance')] = CO2_conversion_number*3.4614907766
    
    M[pl.index('fast'), cl.index('total time')] = -18  # per minute
    M[pl.index('fast'), cl.index('time at home')] = +3  # we get some time back for waiting at home
    M[pl.index('noliketransfer'), cl.index('num transfers')] = -12*18   
#    M[pl.index('noliketransfer'), cl.index('num transfers')] = -30
    M[pl.index('nocar'), cl.index('involves car')] = -1e10
    M[pl.index('nobike'), cl.index('involves own bike')] = -1e10
    M[pl.index('no bike at start'), cl.index('starts with bike')] = -1e10
    M[pl.index('no bike at end'), cl.index('ends with bike')] = -1e10
    M[pl.index('likewalk'), cl.index('involves walk')] = 3
    M[pl.index('likebike'), cl.index('involves bike')] = 6
    M[pl.index('mindrain'), cl.index('rainy')] = -2
    M = array(M)
    return M, preference_list, conditions_list


def load_user_preference(pref, option):
    preference_vec = zeros(len(preference_list))
    preference_vec[preference_list.index('fast')] = pref.travel_time_importance/10.0+0.02
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
    #preference_vec[preference_list.index('noliketransfer')] = float(pref.reduce_number_of_transfers)*0.9+0.1
    preference_vec[preference_list.index('noliketransfer')] = 1.0
    preference_vec[preference_list.index('save CO2')] = pref.save_CO2
    
    return preference_vec








