from django import template
from reisbrein.segment import TransportType

register = template.Library()


@register.simple_tag
def transport_type_icon(transport_type):
    icon_map = {
        TransportType.TRAIN.name: 'fa-train',
        TransportType.BUS.name: 'fa-bus',
        TransportType.TRAM.name: 'fa-subway',
        TransportType.WALK.name: 'fa-blind',
        TransportType.CAR.name: 'fa-car',
        TransportType.BIKE.name: 'fa-bicycle',
        TransportType.WAIT.name: 'fa-child',
    }
    if transport_type in icon_map:
        return icon_map[transport_type]
    return 'fa-question'


@register.simple_tag
def transport_type_color(transport_type):
    color_map = {
        TransportType.TRAIN.name: 'success',
        TransportType.BUS.name: 'bus',
        TransportType.TRAM.name: 'warning',
        TransportType.WALK.name: 'info',
        TransportType.CAR.name: 'primary',
        TransportType.BIKE.name: 'warning',
        TransportType.WAIT.name: 'default',
    }
    if transport_type in color_map:
        return color_map[transport_type]
    return 'default'


@register.simple_tag
def transport_type_bgcolor(transport_type):
    color_map = {
        TransportType.TRAIN.name: 'bg-success',
        TransportType.BUS.name: 'bg-warning',
        TransportType.TRAM.name: 'bg-warning',
        TransportType.WALK.name: 'bg-info',
        TransportType.CAR.name: 'bg-primary',
        TransportType.BIKE.name: 'bg-warning',
        TransportType.WAIT.name: 'bg-danger',
    }
    if transport_type in color_map:
        return color_map[transport_type]
    return 'default'
