import numpy as np
import pytest
from bw2data import Database, Method, databases, geomapping, get_activity, methods
from bw2data.tests import bw2test

from simple_regional import OneSpatialScaleLCA as LCA


@bw2test
def test_value_error_no_method():
    empty = Database("empty")
    empty.write({("empty", "nothing"): {}})

    with pytest.raises(ValueError):
        LCA({("empty", "nothing"): 1})


@pytest.fixture
@bw2test
def import_data():
    biosphere_data = {
        ("biosphere", "F"): {
            "type": "emission",
            "exchanges": [],
        },
        ("biosphere", "G"): {
            "type": "emission",
            "exchanges": [],
        },
    }
    biosphere = Database("biosphere")
    biosphere.write(biosphere_data)

    inventory_data = {
        ("inventory", "U"): {
            "type": "process",
            "location": "L",
            "exchanges": [
                {"input": ("biosphere", "F"), "type": "biosphere", "amount": 1},
                {"input": ("biosphere", "G"), "type": "biosphere", "amount": 1},
            ],
        },
        ("inventory", "V"): {
            "type": "process",
            "location": "M",
            "exchanges": [],
        },
        ("inventory", "X"): {
            "type": "process",
            "location": "N",
            "exchanges": [],
        },
        ("inventory", "Y"): {
            "type": "process",
            "location": "O",
            "exchanges": [],
        },
        ("inventory", "Z"): {
            "type": "process",
            "location": "O",
            "exchanges": [],
        },
    }
    inventory = Database("inventory")
    inventory.write(inventory_data)

    method_data = [
        [("biosphere", "F"), 1, "L"],
        [("biosphere", "G"), 2, "L"],
    ]
    method = Method(("a", "method"))
    method.write(method_data)


def test_import_data(import_data):
    assert list(databases)
    assert list(methods)


@pytest.fixture
def lca(import_data):
    return LCA(demand={("inventory", "U"): 1}, method=("a", "method"))


def test_inventory(lca):
    lca.lci()

    assert np.allclose(lca.technosphere_matrix.todense(), np.eye(5))

    assert lca.biosphere_matrix.sum() == 2
    assert lca.biosphere_matrix.shape == (2, 5)
    assert (
        lca.biosphere_matrix[
            lca.dicts.biosphere[get_activity(("biosphere", "F")).id],
            lca.dicts.activity[get_activity(("inventory", "U")).id],
        ]
        == 1
    )
    assert (
        lca.biosphere_matrix[
            lca.dicts.biosphere[get_activity(("biosphere", "G")).id],
            lca.dicts.activity[get_activity(("inventory", "U")).id],
        ]
        == 1
    )

    # assert {("inventory", o) for o in "XUVYZ"} == set(lca.activity_dict.keys())
    # assert set(range(5)) == set(lca.activity_dict.values())
    # assert {("biosphere", "G"), ("biosphere", "F")} == set(
    #     lca.biosphere_dict.keys()
    # )
    # assert set(range(2)) == set(lca.biosphere_dict.values())

    assert lca.supply_array.sum() == 1
    assert lca.supply_array.shape == (5,)
    assert lca.supply_array[lca.dicts.product[get_activity(("inventory", "U")).id]] == 1


def test_characterization_matrix(lca):
    lca.lci()
    lca.lcia()

    print(list(lca.dicts.inv_spatial.items()))
    print(list(lca.dicts.biosphere.items()))
    print(list(geomapping.items()))
    for x in Database("biosphere"):
        print(x.id, x["code"])

    matrix = np.zeros((4, 2))
    matrix[1, 1] = 1
    matrix[1, 0] = 2
    print(lca.reg_cf_matrix.toarray())
    assert lca.reg_cf_matrix.sum() == 3
    assert lca.reg_cf_matrix.shape == (4, 2)
    assert (
        lca.reg_cf_matrix[
            lca.dicts.inv_spatial[geomapping["L"]],
            lca.dicts.biosphere[get_activity(("biosphere", "F")).id],
        ]
        == 1
    )
    assert (
        lca.reg_cf_matrix[
            lca.dicts.inv_spatial[geomapping["L"]],
            lca.dicts.biosphere[get_activity(("biosphere", "G")).id],
        ]
        == 2
    )


def test_lca_score(lca):
    lca.lci()
    lca.lcia()
    assert lca.score == 3
