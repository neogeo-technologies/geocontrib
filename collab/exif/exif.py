from PIL import Image
from PIL.ExifTags import TAGS


class ExifException(Exception):
    def __init__(self, message, image_file_path):
        self.message = message
        self.image_file_path = image_file_path

    def __str__(self):
        return self.message


class NoExifException(ExifException):
    def __init__(self, image_file_path):
        message = "No EXIF metadata in file."
        super().__init__(message, image_file_path)


class NoGpsInfoException(ExifException):
    def __init__(self, image_file_path):
        message = "No GPSInfo in EXIF metadata."
        super().__init__(message, image_file_path)


class NoElevationInfoException(ExifException):
    def __init__(self, image_file_path):
        message = "No elevation in GPSInfo in EXIF metadata."
        super().__init__(message, image_file_path)


class EmptyGpsInfoException(ExifException):
    def __init__(self, image_file_path):
        message = "Empty GPSInfo in EXIF metadata."
        super().__init__(message, image_file_path)


get_float = lambda x: float(x[0]) / float(x[1])


class Exif():

    WKT_POINT_TEMPLATE = "POINT({lat} {lon})"
    WKT_POINT_Z_TEMPLATE = "POINT({lat} {lon} {alt})"
    EWKT_POINT_TEMPLATE = "SRID=4326;POINT({lat} {lon})"
    EWKT_POINT_Z_TEMPLATE = "SRID=4326;POINT({lat} {lon} {alt})"

    def __init__(self, image_file_path):
        self.exif = None
        self.image_file_path = image_file_path

        image = Image.open(self.image_file_path)
        image.verify()
        self.exif = image._getexif()

        if self.exif is None:
            raise NoExifException(self.image_file_path)

    def get_labelled_tags(self):
        labelled = {}
        for (key, val) in self.exif.items():
            labelled[TAGS.get(key)] = val

        return labelled

    def get_tag_by_id(self, tag_id, default_value=None):
        return self.exif.get(tag_id, default_value)

    def get_tag_by_name(self, tag_name, default_value=None):
        labelled = self.get_labelled_tags()
        return labelled.get(tag_name, default_value)

    def get_geoloc_tag(self):
        if 34853 not in self.exif.keys():
            raise NoGpsInfoException(self.image_file_path)
        elif not self.exif[34853]:
            raise EmptyGpsInfoException(self.image_file_path)
        return self.exif[34853]

    def __get_decimal_from_dms(self, dms, ref):
        d = get_float(dms[0])
        m = get_float(dms[1])
        s = get_float(dms[2])

        seconds = (d * 3600.0) + (m * 60.0) + (s)

        if ref in ['S', 'W']:
            seconds *= -1.

        return seconds / 3600.

    def __get_decimal_from_zref(self, z, ref):
        alt = get_float(z)
        if ref != b'\x00':
            alt *= -1.

        return alt

    def __get_lat(self):
        geoloc_tags = self.get_geoloc_tag()
        lat = self.__get_decimal_from_dms(
            geoloc_tags[2],
            geoloc_tags[1]
        )
        return lat

    def __get_lon(self):
        geoloc_tags = self.get_geoloc_tag()
        lon = self.__get_decimal_from_dms(
            geoloc_tags[4],
            geoloc_tags[3]
        )
        return lon

    def __get_alt(self):
        geoloc_tags = self.get_geoloc_tag()
        if 6 not in geoloc_tags.keys() or 5 not in geoloc_tags.keys():
            raise NoElevationInfoException(self.image_file_path)
        alt = self.__get_decimal_from_zref(
            geoloc_tags[6],
            geoloc_tags[5]
        )
        return alt

    def get_geoloc_as_wkt(self, with_alt=False, ewkt=False):
        lat = self.__get_lat()
        lon = self.__get_lon()
        if with_alt:
            alt = self.__get_alt()
            if ewkt:
                wkt_template = self.EWKT_POINT_Z_TEMPLATE
            else:
                wkt_template = self.WKT_POINT_Z_TEMPLATE
        else:
            alt = None
            if ewkt:
                wkt_template = self.EWKT_POINT_TEMPLATE
            else:
                wkt_template = self.WKT_POINT_TEMPLATE

        return wkt_template.format(lat=lat, lon=lon, alt=alt)


def get_image_geoloc_as_wkt(image_file_path, with_alt=False, ewkt=False):
    exif = Exif(image_file_path)
    return exif.get_geoloc_as_wkt(with_alt=with_alt, ewkt=ewkt)


def get_image_labelled_tags(image_file_path):
    exif = Exif(image_file_path)
    return exif.get_labelled_tags()


def get_image_tag_by_name(image_file_path, tag_name):
    exif = Exif(image_file_path)
    return exif.get_tag_by_name(tag_name)


def get_image_tag_by_id(image_file_path, tag_id):
    exif = Exif(image_file_path)
    return exif.get_tag_by_id(tag_id)

