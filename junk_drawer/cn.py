"""
Content Negotiation stuff.
"""

from django.utils.http import parse_header_parameters


def get_accepts(scope: dict):
    for header, value in scope['headers']:
        if header.lower() == b'accept':
            yield from parse_accept(value.decode('utf-8'))


def parse_accept(txt: str):
    for bit in txt.split(','):
        yield parse_header_parameters(bit.strip())
