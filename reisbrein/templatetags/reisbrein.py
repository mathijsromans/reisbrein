from django import template
from reisbrein.segment import TransportType

register = template.Library()


@register.simple_tag
def transport_type_icon(transport_type):
    icon_map = {
        TransportType.TRAIN.name: 'fa-train',
        TransportType.WALK.name: 'fa-blind',
        TransportType.CAR.name: 'fa-car',
        TransportType.BIKE.name: 'fa-bicycle',
        TransportType.WAIT.name: 'fa-child',
    }
    if transport_type in icon_map:
        return icon_map[transport_type]
    return 'fa-question'


# @register.simple_tag
# def transport_type_color(transport_type):
#     return datetime.datetime.now().strftime(format_string)
