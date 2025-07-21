from src.world_manager import WorldManager
from src.constants import MAX_NEIGHBORS, NEIGHBOR_NONE_STR


def test_attempt_link_neighbors_directional():
    world = {
        "nodes": {
            "10": {"node_id": 10, "parent_id": 1, "neighbors": [{"id": None, "border": NEIGHBOR_NONE_STR} for _ in range(MAX_NEIGHBORS)]},
            "20": {"node_id": 20, "parent_id": 1, "neighbors": [{"id": None, "border": NEIGHBOR_NONE_STR} for _ in range(MAX_NEIGHBORS)]},
        },
        "characters": {},
    }
    manager = WorldManager(world)
    manager.get_depth_of_node = lambda _nid: 3

    ok, _ = manager.attempt_link_neighbors(10, 20, slot1=2)
    assert ok
    assert world["nodes"]["10"]["neighbors"][1]["id"] == 20
    assert world["nodes"]["20"]["neighbors"][4]["id"] == 10
