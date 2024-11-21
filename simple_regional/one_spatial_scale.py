from functools import partial

import matrix_utils as mu
from bw2calc.lca import LCA
from bw2data import Database, Method, get_activity, methods
from bw_processing import load_datapackage, DatapackageBase
from fsspec.implementations.zip import ZipFileSystem
from fsspec import AbstractFileSystem
from typing import Callable, Iterable, Optional, Union


def dp(fp):
    return load_datapackage(ZipFileSystem(fp, mode="r"))


def get_dependent_databases(demand_dict):
    """Demand can be activitiy ids or tuple keys."""
    db_labels = [
        x[0] if isinstance(x, tuple) else get_activity(x)["database"]
        for x in demand_dict
    ]
    return set.union(*[Database(label).find_graph_dependents() for label in db_labels])


class OneSpatialScaleLCA(LCA):
    matrix_labels = [
        "biosphere_mm",
        "inv_mapping_mm",
        "reg_cf_mm",
        "technosphere_mm",
    ]

    def __init__(self, demand, *args, **kwargs):
        r"""Perform regionalized LCA calculation, where the inventory shares the same spatial scale as impact assessment.

        The calculation formula is:

        .. math::

            h_{r} = \left[ \textbf{MR} \right]^{T} \circ [ \textbf{B} \cdot (\textbf{A}^{-1}f) ]

        Uses sparse matrix `elementwise multiplication <http://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.multiply.html>`_.

        """
        self.databases = get_dependent_databases(demand)
        self.extra_data_objs = kwargs.pop("extra_data_objs", [])
        super(OneSpatialScaleLCA, self).__init__(demand, *args, **kwargs)
        if self.method not in methods:
            raise ValueError("Must pass valid `method` name")

    def create_inventory_mapping_matrix(self):
        """Get inventory mapping matrix, **M**, which maps inventory activities to inventory locations. Rows are inventory activities and columns are inventory spatial units.

        Uses ``self.technosphere_mm.row_mapper`` and ``self.databases``.

        Creates ``self.inv_mapping_mm``, ``self.inv_mapping_matrix``, and ``self.dicts.inv_spatial``/

        """
        self.inv_mapping_mm = mu.MappedMatrix(
            packages=[dp(Database(x).filepath_processed()) for x in self.databases]
            + self.extra_data_objs,
            matrix="inv_geomapping_matrix",
            use_arrays=self.use_arrays,
            use_distributions=self.use_distributions,
            seed_override=self.seed_override,
            row_mapper=self.technosphere_mm.col_mapper,
        )
        self.inv_mapping_matrix = self.inv_mapping_mm.matrix
        self.dicts.inv_spatial = partial(self.inv_mapping_mm.col_mapper.to_dict)

    def create_regionalized_characterization_matrix(self, row_mapper=None):
        """Get regionalized characterization matrix, **R**, which gives location- and biosphere flow-specific characterization factors.

        Rows are impact assessment spatial units, and columns are biosphere flows. However, we build it transverse and transpose it, as the characterization matrix indices are provided that way.

        Uses ``self._biosphere_dict`` and ``self.method``.

        Returns:
            * ``reg_cf_params``: Parameter array with row/col of IA locations/biosphere flows
            * ``ia_spatial_dict``: Dictionary linking impact assessment locations to matrix rows
            * ``reg_cf_matrix``: The matrix **R**

        """
        use_arrays, use_distributions = self.check_selective_use("characterization_matrix")

        try:
            self.reg_cf_mm = mu.MappedMatrix(
                packages=[dp(Method(self.method).filepath_processed())]
                + self.extra_data_objs,
                matrix="characterization_matrix",
                use_arrays=use_arrays,
                use_distributions=use_distributions,
                seed_override=self.seed_override,
                row_mapper=row_mapper,
                col_mapper=self.biosphere_mm.row_mapper,
                transpose=True,
            )
        except mu.errors.AllArraysEmpty:
            raise ValueError("Given `method` or `data_objs` have no characterization data")

        self.reg_cf_matrix = self.reg_cf_mm.matrix
        if row_mapper is None:
            self.dicts.ia_spatial = partial(self.reg_cf_mm.row_mapper.to_dict)

    def load_lcia_data(
        self,
        data_objs: Optional[Iterable[Union[AbstractFileSystem, DatapackageBase]]] = None
    ) -> None:
        self.create_inventory_mapping_matrix()
        self.create_regionalized_characterization_matrix(row_mapper=self.inv_mapping_mm.col_mapper)
        self.characterization_matrix = (
            self.inv_mapping_matrix @ self.reg_cf_matrix
        ).T

    def lcia_calculation(self):
        """Do regionalized LCA calculation.

        Creates ``self.characterized_inventory``.

        """
        # `.multiply()` does elementwise multiplication
        self.characterized_inventory = self.characterization_matrix.multiply(self.inventory)

    def results_ia_spatial_scale(self):
        raise NotImplementedError("No separate IA spatial scale")

    def results_inv_spatial_scale(self):
        if not hasattr(self, "characterized_inventory"):
            raise ValueError("Must do lcia calculation first")
        return self.reg_cf_matrix.T.multiply(self.inventory * self.inv_mapping_matrix)
