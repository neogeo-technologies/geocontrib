import unittest
import os
import exif


class TestStringMethods(unittest.TestCase):

    def test_orientation(self):
        file_name = "DSC_0027.JPG"
        file_path = os.path.join("test_images", "gps", "bchartier-exif-samples", file_name)

        orientation = exif.get_image_tag_by_name(file_path, "Orientation")
        self.assertEqual(orientation, 6)

    def test_wkt_01(self):
        file_name = "DSC_0027.JPG"
        file_path = os.path.join("test_images", "gps", "bchartier-exif-samples", file_name)

        wkt = exif.get_image_geoloc_as_wkt(file_path, with_alt=False, ewkt=False)
        self.assertEqual(wkt, "POINT(49.00055555555556 2.0008333333333335)")

    def test_wkt_02(self):
        file_name = "DSCN0025.jpg"
        file_path = os.path.join("test_images", "gps", "ianare-exif-samples", file_name)

        wkt = exif.get_image_geoloc_as_wkt(file_path, with_alt=False, ewkt=False)
        self.assertEqual(wkt, "POINT(43.468365 11.881634999972222)")

    def test_ewkt_01(self):
        file_name = "DSC_0027.JPG"
        file_path = os.path.join("test_images", "gps", "bchartier-exif-samples", file_name)

        ewkt = exif.get_image_geoloc_as_wkt(file_path, with_alt=True, ewkt=True)
        self.assertEqual(ewkt, "SRID=4326;POINT(49.00055555555556 2.0008333333333335 83.0)")

    def test_ewkt_02(self):
        file_name = "DSCN0025.jpg"
        file_path = os.path.join("test_images", "gps", "ianare-exif-samples", file_name)

        with self.assertRaises(exif.NoElevationInfoException) as cm:
            ewkt = exif.get_image_geoloc_as_wkt(file_path, with_alt=True, ewkt=True)

    def test_exception_2(self):
        file_name = "DSC_0026.JPG"
        file_path = os.path.join("test_images", "gps", "bchartier-exif-samples", file_name)

        with self.assertRaises(exif.NoGpsInfoException) as cm:
            ewkt = exif.get_image_geoloc_as_wkt(file_path, with_alt=True, ewkt=True)


if __name__ == '__main__':
    unittest.main()
