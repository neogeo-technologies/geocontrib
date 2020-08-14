from django.test import TestCase
import os
from geocontrib.exif import exif

TEST_IMAGES_DIR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_images")


class TestStringMethods(TestCase):

    def test_orientation(self):
        """Checks if the orientation of an image can be extracted from exif tags"""
        file_name = "DSC_0027.JPG"
        file_path = os.path.join(TEST_IMAGES_DIR_PATH, "gps", "bchartier-exif-samples", file_name)

        orientation = exif.get_image_tag_by_name(file_path, "Orientation")
        self.assertEqual(orientation, 6)

    def test_wkt_01(self):
        """Checks if the geometry x,y in WKT format can be extracted from exif tags of an image taken by bchartier."""
        file_name = "DSC_0027.JPG"
        file_path = os.path.join(TEST_IMAGES_DIR_PATH, "gps", "bchartier-exif-samples", file_name)

        wkt = exif.get_image_geoloc_as_wkt(file_path, with_alt=False, ewkt=False)
        self.assertEqual(wkt, "POINT(2.0008333333333335 49.00055555555556)")

    def test_wkt_02(self):
        """Checks if the geometry x,y in WKT format can be extracted from exif tags of an image taken by ianare."""
        file_name = "DSCN0025.jpg"
        file_path = os.path.join(TEST_IMAGES_DIR_PATH, "gps", "ianare-exif-samples", file_name)

        wkt = exif.get_image_geoloc_as_wkt(file_path, with_alt=False, ewkt=False)
        self.assertEqual(wkt, "POINT(11.881634999972222 43.468365)")

    def test_ewkt_01(self):
        """Checks if the geometry x,y,z in eWKT format can be extracted from exif tags of an image taken by bchartier.
        """
        file_name = "DSC_0027.JPG"
        file_path = os.path.join(TEST_IMAGES_DIR_PATH, "gps", "bchartier-exif-samples", file_name)

        ewkt = exif.get_image_geoloc_as_wkt(file_path, with_alt=True, ewkt=True)
        self.assertEqual(ewkt, "SRID=4326;POINT(2.0008333333333335 49.00055555555556 83.0)")

    def test_ewkt_02(self):
        """Checks if the absence of elevation can be detected in a image taken by ianare."""
        file_name = "DSCN0025.jpg"
        file_path = os.path.join(TEST_IMAGES_DIR_PATH, "gps", "ianare-exif-samples", file_name)

        with self.assertRaises(exif.NoElevationInfoException) as cm:
            ewkt = exif.get_image_geoloc_as_wkt(file_path, with_alt=True, ewkt=True)

    def test_exception_2(self):
        """Checks if the absence of GPS tags can be detected in a image taken by bchartier."""
        file_name = "DSC_0026.JPG"
        file_path = os.path.join(TEST_IMAGES_DIR_PATH, "gps", "bchartier-exif-samples", file_name)

        with self.assertRaises(exif.NoGpsInfoException) as cm:
            ewkt = exif.get_image_geoloc_as_wkt(file_path, with_alt=True, ewkt=True)
