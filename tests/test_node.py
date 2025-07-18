from src.node import Node
from src.constants import NEIGHBOR_NONE_STR, MAX_NEIGHBORS


def test_node_from_dict_normalizes_fields():
    raw = {
        "node_id": 1,
        "parent_id": None,
        "name": "Kingdom",
        "custom_name": "Svea",
        "population": 100,
        "ruler_id": "2",
        "num_subfiefs": 0,
        "children": ["2", 3],
        "neighbors": [{"id": "2", "border": "v\u00e4g"}],
        "res_type": "Resurs",
    }

    node = Node.from_dict(raw)

    assert node.node_id == 1
    assert node.parent_id is None
    assert node.ruler_id == 2
    assert node.children == [2, 3]
    assert len(node.neighbors) == MAX_NEIGHBORS
    assert node.neighbors[0].id == 2
    assert node.neighbors[0].border == "v\u00e4g"
    for nb in node.neighbors[1:]:
        assert nb.id is None and nb.border == NEIGHBOR_NONE_STR
