import os
import pytest

os.environ["OPENAI_API_KEY"] = "fake-openai-api-key"
os.environ["MAPS_API_KEY"] = "fake-maps-api-key"

# Put imports later b/c we need to set the env vars first
from freedom.events.models import Event  # noqa: E402
from freedom.utils import Location  # noqa: E402


@pytest.fixture(autouse=True)
def mock_api_calls(monkeypatch):
    def mock_infer_location(self, *args, **kwargs):
        self.location = Location(lat=0.0, lon=0.0)

    def mock_infer_types(self, *args, **kwargs):
        self.types = ["test"]

    Event.infer_location = mock_infer_location
    Event.infer_types = mock_infer_types
