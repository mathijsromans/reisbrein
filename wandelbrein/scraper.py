import os
import subprocess

import requests
import lxml.html

import gpxpy.parser
import gpxpy.gpx


class TrailData(object):

    def __init__(self, nswandel_url, wandelpagina_id, wandelpagina_url,
                 begin_point, end_point, distance_m, gpx_str, geojson_str):
        self.nswandel_url = nswandel_url
        self.wandelpagina_id = wandelpagina_id
        self.wandelpagina_url = wandelpagina_url
        self.begin_point = begin_point
        self.end_point = end_point
        self.distance_m = distance_m
        self.gpx = gpx_str
        self.geojson = geojson_str


def get_groene_wissels_data(max_results=None):
    trail_data_list = []
    urls = get_groene_wissel_urls()
    for index, nswandel_url in enumerate(urls):
        print(nswandel_url)
        wandelpagina_url = get_wandelzoekpagina_url(nswandel_url)
        print(wandelpagina_url)
        if wandelpagina_url is None:
            continue
        gw_url_split = wandelpagina_url.split('wnummer=')
        if len(gw_url_split) != 2:
            print('ERROR: could not find wandel id for url', wandelpagina_url)
            continue
        wandel_id = gw_url_split[1]
        print('wandel id', wandel_id)
        gpx_url = get_wandzoekpagina_gpx(wandel_id)
        response = requests.get(gpx_url)
        gpx_str = response.text
        begin_point, end_point, distance_m = find_begin_end_distance_gpx(gpx_str)
        gpx_filepath = gpx_to_file(gpx_str, wandel_id)
        geojson_str = gpx_to_geojson(gpx_filepath)
        if begin_point is None:
            print('ERROR: parsing gpx file failed')
            continue
        print(begin_point.latitude, begin_point.longitude)
        print(end_point.latitude, end_point.longitude)
        print('distance', distance_m / 1000, 'm')
        trail_data = TrailData(nswandel_url, wandel_id, wandelpagina_url, begin_point, end_point, distance_m, gpx_str, geojson_str)
        trail_data_list.append(trail_data)
        if max_results is not None and index == max_results:
            break
    return trail_data_list


def get_groene_wissel_urls():
    urls = []
    url_table = 'http://nswandel.nl'
    page = requests.get(url_table)
    tree = lxml.html.fromstring(page.content)
    rows = tree.xpath("//tbody/tr")
    for row in rows:
        for column in row.iter():
            if column.tag == 'a':
                page_url = 'http://nswandel.nl/' + column.attrib['href']
                urls.append(page_url)
    return urls


def get_wandelzoekpagina_url(groene_wissle_url):
    page = requests.get(groene_wissle_url)
    tree = lxml.html.fromstring(page.content)
    links = tree.xpath("//a")
    for link in links:
        if 'wandelzoekpagina.nl' in link.get('href'):
            return link.get('href')
    return None


def get_wandzoekpagina_gpx(wandel_id):
    return 'https://www.wandelzoekpagina.nl/lib/gpx.php?wnummer=' + wandel_id


def gpx_to_file(gpx_str, wandel_id):
    outdir = 'data'
    gpx_filepath = os.path.join(outdir, wandel_id + '.gpx')
    with open(gpx_filepath, 'w') as fileout:
        fileout.write(gpx_str)
    return gpx_filepath


def gpx_to_geojson(file_gpx):
    args = ['togeojson', file_gpx]
    try:
        output = subprocess.check_output(args)
    except subprocess.CalledProcessError as e:
        print(e)
        raise
    return output.decode('utf-8')


def find_begin_end_distance_gpx(gpx_xml_str):
    try:
        gpx_parser = gpxpy.parser.GPXParser(gpx_xml_str)
        gpx = gpx_parser.parse()
    except gpxpy.gpx.GPXXMLSyntaxException as e:
        print(e)
        return None, None, None
    point_begin = None
    point_end = None
    if gpx.routes:
        point_begin = gpx.routes[0].points[0]
        point_end = gpx.routes[-1].points[-1]
    elif gpx.tracks:
        point_begin = gpx.tracks[0].segments[0].points[0]
        point_end = gpx.tracks[-1].segments[-1].points[-1]
    distance_m = gpx.length_3d()
    return point_begin, point_end, distance_m


if __name__ == "__main__":
    get_groene_wissels_data(max_results=5)
