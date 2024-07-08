# encoding: utf-8

import googlemaps
from secret import GOOGLE_MAPS_API_KEY


def get_reviews_from_lat_long(latlon, name=None,  address=None):

    API_KEY = GOOGLE_MAPS_API_KEY
    gmaps = googlemaps.Client(key=API_KEY)

    if name is None:
        name = ""

    if address is None:
        address = ""

    if name == "" and address == "":
        places_result = gmaps.places_nearby(
            location=latlon, language="zh-TW", radius=100)
    else:
        places_result = gmaps.places(
            query=name + address, location=latlon, language="zh-TW"
        )

    if not places_result['results']:
        return ""

    place = places_result['results'][0]
    place_id = place['place_id']
    place_details = gmaps.place(place_id=place_id, language="zh-TW")

    reviews = ""
    if 'reviews' in place_details['result']:
        for review in place_details['result']['reviews']:
            reviews += f"""{review['text']}\n"""

    return reviews


if __name__ == "__main__":
    print(get_reviews_from_lat_long(latlon=(25.02996195508232,
          121.56138034612799), name="waku waku burger 101店", address="No. 117, Wuxing St, Xinyi District, Taipei City, 110"))
