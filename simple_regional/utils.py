import numpy as np
from bw2data import Method, methods
from bw_processing import load_datapackage
from fsspec.implementations.zip import ZipFileSystem

# def import_regionalized_cfs(
#     geocollection,
#     method_tuple,
#     mapping,
#     scaling_factor=1,
#     global_cfs=None,
#     nan_value=None,
# ):
#     """Import data from a vector geospatial dataset into a ``Method``.

#     A ``Method`` can have both site-generic and regionalized characterization factors.

#     The ``mapping`` defines which field (vector) maps to which biosphere flows. Some methods may
#     only define regionalized chracterization factors for a single biosphere flow, but it is much
#     more common to have each field or band map to multiple biosphere flows. Therefore, mapping
#     should be defined as:

#     .. code-block:: python

#         {
#             field name (str): [list of biosphere flows (tuples)]
#         }

#     Args:
#         * *geocollection*: A ``geocollection`` name.
#         * *method_tuple*: A method tuple.
#         * *mapping*: Mapping from fields or bands to biosphere flows. See above.
#         * *scaling_factor*: Optional. Rescale the values in the spatial data source.
#         * *global_cfs*: An optional list of CFs to add when writing the method.
#         * *nan_value*: Sentinel value for missing values if ``NaN`` is not used directly.

#     """
#     assert (
#         geocollection in geocollections
#         and geocollections[geocollection].get("kind") == "vector"
#         and "field" in geocollections[geocollection]
#     )
#     gdf = gp.read_file(geocollections[geocollection]["filepath"])
#     id_label = geocollections[geocollection]["field"]

#     method = Method(method_tuple)
#     method.metadata["geocollections"] = [geocollection]
#     methods.flush()

#     data = []
#     if global_cfs:
#         data.extend(global_cfs)

#     for index, feature in gdf.iterrows():
#         for field_label, biosphere_flows in mapping.items():
#             value = feature[field_label]
#             if value is None or value == nan_value or np.isnan(value):
#                 continue
#             else:
#                 for flow in biosphere_flows:
#                     data.append(
#                         (
#                             flow,
#                             float(value) * scaling_factor,
#                             (geocollection, feature[id_label]),
#                         )
#                     )

#     method.write(data)


def dp(fp):
    return load_datapackage(ZipFileSystem(fp, mode="r"))
