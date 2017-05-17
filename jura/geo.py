class Location(object):
    def __init__(self, lat, lng, address=None):
        self.lat = float(lat)
        self.lng = float(lng)
        self.address = address

    def as_dict(self):
        data = {
                'lat': self.lat,
                'lng': self.lng,
                }
        if self.address is not None:
            data['address'] = self.address

        return data
