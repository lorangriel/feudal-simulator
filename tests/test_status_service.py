from src.status_service import StatusService


def test_add_message_notifies_listeners():
    service = StatusService()
    received = []
    service.add_listener(received.append)
    service.add_message("hej")
    assert service.messages == ["hej"]
    assert received == ["hej"]
