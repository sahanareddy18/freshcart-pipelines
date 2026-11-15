from stream.routing import topic_matches
from stream.dispatcher import make_request


def test_topic_wildcards_match_assignment_examples():
    assert topic_matches("bangalore.koramangala.*", "bangalore.koramangala.food")
    assert topic_matches("bangalore.*.ride", "bangalore.whitefield.ride")
    assert topic_matches("bangalore.#", "bangalore.koramangala")
    assert not topic_matches("bangalore.*.ride", "bangalore.koramangala")
    assert not topic_matches("chennai.tnagar.food", "chennai.whitefield.ride")


def test_dispatcher_marks_each_tenth_message_malformed():
    key, good = make_request(9, "bangalore.koramangala.food")
    bad_key, bad = make_request(10, "bangalore.koramangala.food")

    assert key == bad_key == "bangalore.koramangala.food"
    assert good["zone"] == "koramangala"
    assert "zone" not in bad