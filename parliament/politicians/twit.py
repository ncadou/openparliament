import email
import datetime
import re

from django.conf import settings
import twitter

from parliament.core.models import Politician, PoliticianInfo
from parliament.activity import utils as activity

import logging
logger = logging.getLogger(__name__)

_SPACES = re.compile(r'\s+', flags=re.UNICODE)


def save_tweets():
    twitter_to_pol = dict([(int(i.value), i.politician) for i in PoliticianInfo.objects.filter(schema='twitter_id').select_related('politician')])
    screen_names = set(PoliticianInfo.objects.filter(schema='twitter').values_list('value', flat=True))
    twit = twitter.Twitter(auth=twitter.OAuth(**settings.TWITTER_OAUTH))
    openparlca = twit.lists.statuses(owner_screen_name='openparlca',
                                     count=200, slug='mps')
    cdngov = twit.lists.statuses(owner_screen_name='CdnGov', count=200,
                                 slug='canadian-mps')
    for status in reversed(openparlca + cdngov):
        try:
            pol = twitter_to_pol[status['user']['id']]
        except KeyError:
            logger.error("Can't find twitter ID %s (name %s)" 
                % (status['user']['id'], status['user']['screen_name']))
            continue
        if status['user']['screen_name'] not in screen_names:
            # Changed screen name
            pol.set_info('twitter', status['user']['screen_name'])
        date = datetime.date.fromtimestamp(
            email.utils.mktime_tz(
                email.utils.parsedate_tz(status['created_at'])
            )
        ) # fuck you, time formats
        guid = 'twit_%s' % status['id']
        # Twitter apparently escapes < > but not & " 
        # so I'm clunkily unescaping lt and gt then reescaping in the template
        text = status['text'].replace('&lt;', '<').replace('&gt;', '>')
        activity.save_activity({'text': _SPACES.sub(' ', status['text'])},
            politician=pol, date=date, guid=guid, variety='twitter')
            

        
    
