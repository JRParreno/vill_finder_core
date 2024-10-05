import math

class DistanceMixin:
    def haversine(self, lon1, lat1, lon2, lat2):
        """
        Calculate the great-circle distance between two points
        on the Earth specified in decimal degrees (latitude and longitude).
        
        :param lon1: Longitude of the first point
        :param lat1: Latitude of the first point
        :param lon2: Longitude of the second point
        :param lat2: Latitude of the second point
        :return: Distance between the two points in kilometers
        """
        R = 6371  # Radius of the Earth in km
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c  # Distance in km
