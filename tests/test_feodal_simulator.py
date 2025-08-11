from src import feodal_simulator as fs


def test_commit_pending_changes_calls_callback_and_clears():
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    called = []

    def cb():
        called.append(True)

    sim.pending_save_callback = cb
    fs.FeodalSimulator.commit_pending_changes(sim)
    assert called and sim.pending_save_callback is None
