#!/usr/bin/env python

"""
Cron jobs
"""

import app_config
import json
import logging
import os
import requests

from fabric.api import local, require, task
from pyquery import PyQuery as pq

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

WEBHOOK = 'https://hooks.slack.com/services/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'

@task
def post_message():
    message = check_page()
    if message:
        r = requests.post(WEBHOOK, data=json.dumps(message))
        logger.info(r.text)


def check_page():
    attachments = []
    last_title = get_last_title()

    d = pq(url='https://www.whitehouse.gov/briefing-room/presidential-actions')
    items = d('.views-row')

    for i, item in enumerate(items):
        item_query = items.eq(i)
        a = item_query.find('.field-content a')
        dateline = item_query.find('div').eq(0).text()
        
        if last_title == a.text():
            break

        data = build_attachment(a, dateline)

        attachments.append(data)

    if len(attachments) > 0:
        write_last_title(attachments)

        return {
            'text': '{0} new executive orders!'.format(len(attachments)),
            'attachments': attachments
        }
    else:
        return None


def get_last_title():
    if os.path.exists('data/last-title'):
        with open('data/last-title', 'r') as readfile:
            last_title = readfile.read()
    else:
        last_title = None

    return last_title


def write_last_title(attachments):
    with open('data/last-title', 'w') as writefile:
        writefile.write(attachments[0]['title'])


def build_attachment(a, dateline):
    return {
        'title': a.text(),
        'title_link': 'https://whitehouse.gov{0}'.format(a.attr('href')),
        'author_name': dateline.split(' on ')[1],
        'fields': [
            {
                'title': 'Type',
                'value': dateline.split(' on ')[0],
            }
        ],
        'fallback': a.text()
    }