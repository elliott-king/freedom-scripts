import json
import os

from openai import OpenAI
from events.types import EVENT_TYPES

API_KEY = os.environ['OPENAI_API_KEY']
MODEL = "gpt-3.5-turbo"
SYSTEM=f"""
You are a categorization assistant. You will ingest a text and categorize it into any categories from this list:

{EVENT_TYPES}

You will return a JSON object with one key ("types") and a value that is the list of categories that apply to the text.
"""

EXAMPLES=[
    {
        'role': 'user',
        'content': """Trialogue on the Cloud Series 5, Sessions 24-26: Continuing our talks on literature and culture, we have chosen three renowned authors for our next session. They are: Guy de Maupassant (France), Anton Chekhov (Russia) and Shi Tie-sheng (China). We will per-announce the book chosen for each discussion, and will, during the session, explore the meanings conveyed in these books, the writing style employed by the authors, and the influence and impact to this day. As always, we encourage all the participants to join our discussion and dialogue. Presenter by John Wang, Fred Huang, and Paul Qiu. Friday evening @ 8 pm. June 21, June 19 and August 16, Zoom platform""",
    },{
        'role': 'assistant', 'content': "{'types': ['literature']}",
    },{
        'role': 'user',
        'content': """ESOL Conversation: Join the English conversation group at East Flushing Library! Take some time to practice the language in a friendly environment. No registration is required - just walk in!""",
    },{
        'role': 'assistant',
        'content': "{'types': ['education', 'library']}",
    },{
        'role': "user",
        'content': """Movie Night at the Garden: Footloose: Spend the evening in our urban oasis-turned outdoor cinema with after-hours admission. Experience big screen magic with the beautiful backdrop of golden hour in the evening. Join us for a screening of the classic 1984 film, Footloose!

Moving in from Chicago, newcomer Ren McCormack (Kevin Bacon) is in shock when he discovers the small Midwestern town he now calls home has made dancing and rock music illegal. As he struggles to fit in, Ren faces an uphill battle to change things. With the help of his new friend, Willard Hewitt (Christopher Penn), and defiant teen Ariel Moore (Lori Singer), he might loosen up this conservative town. But Ariel’s influential father, Reverend Shaw Moore (John Lithgow), stands in the way.

The movie screening will be preceded by a dance class by Margaret Batiuchok. Margaret (danceMB.com) teaches swing, ballroom, solo jazz and stretch in Manhattan and on Zoom. She holds a BFA (Cal Arts) and a MA in Dance (NYU). She is the founder and president of the NY Swing Dance Society, a Harvest Moon Ball Champion, and a Flushing local.

There will also be a bar serving alcoholic and non-alcoholic beverages, as well as a pre-screening craft activity!

ADVANCED TICKETS strongly recommended. Walk-ins welcome upon availability.""",
    },{
        'role': 'assistant',
        'content': "{'types': ['film', 'crafts', 'dance']}",
    }
]


client = OpenAI(api_key=API_KEY)

def categorize_text(text: str) -> list[str]:

    # TODO: consider using an assistant with examples on creation, then we don't send examples on each request...?
    completion = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[{
            "role": "system", "content": SYSTEM
            }] + EXAMPLES + [{
            'role': 'user', 'content': text,
            }],
    )
    if len(completion.choices) < 1:
        return []
    j = json.loads(completion.choices[0].message.content)
    if 'types' not in j:
        print(f"text: {text}")
        print(f"openai output: {completion.choices[0].message.content}")
        raise ValueError(f"OpenAI did not return correct json format.")
    return j.get('types')