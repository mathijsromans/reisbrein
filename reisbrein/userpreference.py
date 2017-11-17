

def order_by_preference(plans):
    plans.sort(key=weight)


def weight(option):
    w = 0
    for segment in option:
        w += segment.distance
    return w
