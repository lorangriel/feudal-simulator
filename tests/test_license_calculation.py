from world_manager import WorldManager
from constants import CRAFTSMAN_LICENSE_FEES

def test_update_license_income_from_craftsmen():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [],
                "craftsmen": [
                    {"type": "Smed", "count": 2},
                    {"type": "Bagare", "count": 1},
                ],
            },
        },
        "characters": {},
    }
    manager = WorldManager(world)
    total = manager.update_license_income(1)
    expected = (
        CRAFTSMAN_LICENSE_FEES["Smed"] * 2
        + CRAFTSMAN_LICENSE_FEES["Bagare"] * 1
    )
    assert total == expected
    assert world["nodes"]["1"]["expected_license_income"] == expected
