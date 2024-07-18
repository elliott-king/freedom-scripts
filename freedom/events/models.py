import decimal
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from freedom.events.types import infer_rsvp

from freedom.openai_api import categorize_text
from freedom.google_api import places_api_search_one
from freedom.utils import Location

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

class BaseModel:
    name: str
    source: str

    def is_ddb_uploaded(self, compare: dict[list[dict[str, str | set[str]]]]) -> bool:
        raise NotImplementedError

    def to_dict(self) -> dict:
        raise NotImplementedError

    def infer_types(self) -> None:
        raise NotImplementedError

@dataclass
class Event(BaseModel):
    name: str | None = None
    website: str = None  # URL of event
    source: str | None = None  # URL of host
    host: str | None = None
    location_description: str | None = None
    description: str | None = None
    datetimes: list[datetime] = field(default_factory=list[datetime])

    rsvp: bool | None = None
    types: list[str] = field(default_factory=list[str])
    photos: list[str] = field(default_factory=list[str])
    id: str = None
    location: Location | None = None

    finalized = False

    required_scalar = [ "name", "website", "source", "host", "location_description", "description",]
    required_vector = ['datetimes']

    def __repr__(self) -> str:
        return f"Event<{self.name}:{self.location_description}>"

    @property
    def dates(self) -> list[str]:
        """Correctly-formatted dates for DynamoDB & OpenSearch"""
        return [d.date().isoformat() for d in self.datetimes]

    @property
    def times(self) -> list[str]:
        """Correctly-formatted times for DynamoDB & OpenSearch"""
        return [d.time().isoformat() for d in self.datetimes]

    def cancelled(self) -> bool:
        for field in ['name', 'description']:
            fv = getattr(self, field).lower()
            if 'cancelled' in fv or 'postponed' in fv or "canceled" in fv:
                return True
        return False

    def valid(self):
        for field in self.required_scalar:
            if getattr(self, field) is None:
                return False, field
        for field in self.required_vector:
            if len(getattr(self, field)) == 0:
                return False, field
        return True, None

    def validate(self):
        v, f = self.valid()
        if not v:
            raise ValueError(f"{self} missing required field: {f}")

    def infer_types(self):
        """Infer types from name and description"""
        text = self.name + " @" + self.location_description + "\n" + self.description
        new_types = categorize_text(text)
        self.types = list(set(self.types + new_types))

    def infer_location(self):
        self.location = places_api_search_one(self.location_description)

    def is_ddb_uploaded(self, compare: dict[list[dict[str, str | set[str]]]]):
        """Check if this event is already uploaded to DynamoDB

        Args:
            compare: Each name has a list of dicts with dates and host
                     eg: {'Volleyball game': [{'dates': set({'2021-09-01'}), 'host': 'John'}]}
        """
        name = self.name.lower().strip()
        if name in compare:
            d = set(self.dates)
            for other in compare[name]:
                if not d.isdisjoint(other['dates']) and other['host'] == self.host:
                    # fixme: set as a DEBUG log
                    print('Already added', self.source, 'event:', self.name, 'with date', self.datetimes)
                    return True
        return False

    def finalize(self):
        """Fetch things from API that are needed"""

        self.validate()

        if self.website and 'http' not in self.website:
            self.website = 'http://' + self.website

        if not self.id:
            self.id = str(uuid.uuid4())

        if not self.location:
            self.infer_location()

        if len(self.types) == 0:
            self.infer_types()

        # Infer if rsvp is necessary or not
        # TODO: consider using chatgpt
        if self.rsvp is None:
            self.rsvp = infer_rsvp(self.description)

        self.finalized = True

    def to_dict(self) -> dict:
        if not self.finalized:
            raise ValueError('{self} not finalized')

        self.validate()

        curr_date_str = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        print('curr_date_str', curr_date_str)
        d = {
            'source': self.source,
            'host': self.host,
            'locationDescription': self.location_description,
            'rsvp': self.rsvp,
            'photos': self.photos,
            'name': self.name,
            'website': self.website,

            'dates': self.dates,
            'times': self.times,

            'createdAt': curr_date_str,
            'updatedAt': curr_date_str,

            'id': self.id,
            '__typename': 'Event',
        }

        # DynamoDB does not take float values.
        d = json.dumps(d, cls=DecimalEncoder)
        d = json.loads(d, parse_float=decimal.Decimal)
        return d