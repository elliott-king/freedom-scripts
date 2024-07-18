import datetime
import pytest

from unittest.mock import patch

from freedom.events.models import Event
from freedom.utils import Location

FAKE_TIME = datetime.datetime(2024, 12, 25, 17, 5, 55)


@pytest.fixture
def e():
    return Event(
        name="test event",
        website="example.com/event",
        source="example.com",
        host="test library host",
        location_description="the middle of the moon",
        description="a test event",
        datetimes=[FAKE_TIME],
    )


class TestEvent:

    def test__empty_event__invalid(self):
        e = Event()
        v, _ = e.valid()
        assert v is False

    def test__valid_event__valid(self, e):
        v, r = e.valid()
        assert v is True
        assert r is None

    def test__type_assignment__returns_test_types_after_calling(self, e):
        assert e.types == []
        e.infer_types()
        assert e.types == ["test"]

    def test__infer_location__returns_test_location_after_calling(self, e):
        assert e.location is None
        e.infer_location()
        assert e.location == Location(lat=0.0, lon=0.0)

    def test__finalize__updates_values_and_sets_boolean(self, e):
        assert e.types == []
        assert e.finalized is False
        assert e.location is None
        assert "http" not in e.website
        assert e.id == None
        assert e.rsvp is None

        e.finalize()

        assert e.types == ["test"]
        assert e.finalized is True
        assert e.location == Location(lat=0.0, lon=0.0)
        assert "http" in e.website
        assert e.id != ""
        assert e.rsvp == False

    def test__to_dict__raises_error_if_not_finalized(self, e):
        with pytest.raises(ValueError):
            e.to_dict()

    def test__to_dict__returns_dict_with_correct_values(self, e):
        e.finalize()

        # Only patching datetime w/in events/models.py
        with patch("freedom.events.models.datetime") as md:
            md.now.return_value = FAKE_TIME
            d = e.to_dict()

        assert d == {
            "source": "example.com",
            "host": "test library host",
            "locationDescription": "the middle of the moon",
            "rsvp": False,
            "photos": [],
            "name": "test event",
            "website": "http://example.com/event",
            "dates": [d.date().isoformat() for d in e.datetimes],
            "times": [d.time().isoformat() for d in e.datetimes],
            "createdAt": FAKE_TIME.isoformat().replace("+00:00", "Z"),
            "updatedAt": FAKE_TIME.isoformat().replace("+00:00", "Z"),
            "id": e.id,
            "__typename": "Event",
        }

    def test__is_ddb_uploaded__correct_response(self, e):
        has = {
            "test event": [
                {
                    "dates": set([d.date().isoformat() for d in e.datetimes]),
                    "host": "test library host",
                }
            ]
        }
        not_has = {
            "test event": [
                {
                    "dates": set(
                        [datetime.datetime(2023, 12, 25, 17, 5, 55).date().isoformat()]
                    ),
                    "host": "not test library host",
                },
                {"dates": set(e.dates), "host": "different host"},
            ]
        }
        assert e.is_ddb_uploaded(has) is True
        assert e.is_ddb_uploaded(not_has) is False
