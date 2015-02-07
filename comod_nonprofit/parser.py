"""
Must define three methods:

* answer_pattern(pattern, args)
* render_answer_html(answer_data)
* render_answer_json(answer_data)
"""
from .patterns import PATTERNS

import json
from django.template import loader, Context
from random import Random
from collections import defaultdict
import requests
import re
import pdb
import os

PATTERN_ARGS_RE = re.compile(r'{([A-Za-z0-9_]+)}')

NONPROFITS_ROOT_URL = "https://projects.propublica.org/nonprofits/api/v1/search.json"

############################################################
# Pattern-dependent behavior

def get_theme(theme):
    payload = { 'q': theme}
    r = requests.get(NONPROFITS_ROOT_URL, params = payload)
    maybe_ok = r.ok
    charity_info = []
    if maybe_ok:
        json_response = r.json()
        charities = [x['organization'] for x in json_response['filings']]
        einset = set()
        for charity in charities:
            if charity['ein'] not in einset:
                einset.add(charity['ein'])
                charity_info.append({'charity_name': charity['name'],
                                'guidestar_url': charity['guidestar_url'],
                                'nccs_url': charity['nccs_url'],
                                'revenue': charity['revenue_amount'] if charity['revenue_amount'] else 0,
                                'assets': charity['asset_amount'] if charity['asset_amount'] else 0})


    return {'maybe_ok': maybe_ok, 'results': charity_info, 'count': len(charity_info)}


def answer_pattern(pattern, args):
    """
    Returns a `dict` representing the answer to the given
    pattern & pattern args.

    'plaintxt' should always be a returned field

    """

    if pattern not in PATTERNS:
      return None
    if len(args) != 1:
      return None

    args_keys = PATTERN_ARGS_RE.findall(pattern)
    kwargs = dict(zip(args_keys,args))
    maybe_theme = kwargs['theme']

    return get_theme(maybe_theme)

############################################################
# Applicable module-wide
def render_answer_html(answer_data):
    template = loader.get_template('comod_nonprofit/nonprofit.html')
    return template.render(Context(answer_data))

def render_answer_json(answer_data):
    return json.dumps(answer_data)
