from geopy.geocoders import Nominatim


def get_geoposition(params):
    if 'text' not in params:
        raise EnvironmentError('Request must contain \'text\' field')

    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    location = geolocator.geocode(params['text'])
    return {'latitude': location.latitude, 'longitude': location.longitude}


