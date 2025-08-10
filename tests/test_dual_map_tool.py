from dual_map_tool import World, History


def test_add_node_and_save_load(tmp_path):
    world = World()
    n1 = world.add_node("A", None, 0, 0)
    n2 = world.add_node("B", n1.node_id, 0, 1)

    assert n2.node_id in world.nodes[n1.node_id].neighbors
    assert n1.node_id in world.nodes[n2.node_id].neighbors

    save_file = tmp_path / "world.json"
    world.save(save_file)

    new_world = World()
    new_world.load(save_file)
    assert len(new_world.nodes) == 2
    assert new_world.nodes[n2.node_id].neighbors == [n1.node_id]


def test_history_undo_redo():
    world = World()
    history = History(world)
    world.add_node("A", None, 0, 0)
    history.push()
    world.add_node("B", 1, 0, 1)

    assert 2 in world.nodes

    history.undo()
    assert 2 not in world.nodes

    history.redo()
    assert 2 in world.nodes
