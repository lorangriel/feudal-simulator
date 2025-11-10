from src.status_service import StatusService


def test_add_message_notifies_listeners():
    service = StatusService()
    received = []
    service.add_listener(received.append)
    service.add_message("hej")
    assert service.messages == ["hej"]
    assert received == ["hej"]


def test_listener_exception_is_swallowed():
    service = StatusService()

    def bad_listener(_message):
        raise RuntimeError("kaputt")

    received: list[str] = []
    service.add_listener(bad_listener)
    service.add_listener(received.append)

    # Should not raise even though the first listener errors out
    service.add_message("hej")

    assert service.messages == ["hej"]
    assert received == ["hej"]
