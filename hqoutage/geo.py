from osgeo import ogr, osr


class CoordTransform:
    _instance = None

    @staticmethod
    def _init_instance():
        in_spatial_ref = osr.SpatialReference()
        in_spatial_ref.ImportFromEPSG(4326)  # World (GeodeticCRS)

        out_spatial_ref = osr.SpatialReference()
        out_spatial_ref.ImportFromEPSG(2014)  # Canada - Quebec - between 75°W and 72°W (ProjectedCRS)

        CoordTransform._instance = osr.CoordinateTransformation(in_spatial_ref, out_spatial_ref)

    @staticmethod
    def get():
        if not CoordTransform._instance:
            CoordTransform._init_instance()

        return CoordTransform._instance


def transform_coord(geometry):
    geometry.Transform(CoordTransform.get())


def get_point_from_lat_lng(lat, lng):
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(lng, lat)

    transform_coord(point)

    return point


def get_geometries_from_kml(filename):
    geometries = []

    driver = ogr.GetDriverByName('KML')
    datasource = driver.Open(filename)

    layer_count = datasource.GetLayerCount()  # Should always equals 0 or 1

    for i in range(layer_count):
        layer = datasource.GetLayer(i)

        feat_count = layer.GetFeatureCount()

        for j in range(feat_count):
            feat = layer.GetFeature(j)

            geometry = feat.GetGeometryRef()
            transform_coord(geometry)

            clone = geometry.Clone()
            geometries.append(clone)

    return geometries
