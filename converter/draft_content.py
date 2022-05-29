#!/usr/bin/env python
# coding: utf-8
import json


class CaptionsTracker(object):
    def __init__(self, source_file):
        self.__file = source_file
        self.__content = {}
        self.__tracks = []

    def read(self):
        self.__resolve_caption_tracks()
        return self

    @property
    def caption_source(self):
        return self.__tracks

    def __resolve_caption_tracks(self):
        self.__read_content()
        texts = {t['id']: t['content']
                 for t in self.__content['materials']['texts']
                 if t['type'] == 'subtitle'}

        """[
            'start': (μs),
            'end': (μs),
            'content': (...)
        }]"""
        for t in self.__content['tracks']:
            for s in t['segments']:
                if s['material_id'] in texts.keys():
                    timerange = s['target_timerange']
                    self.__tracks.append({
                        'start': timerange['start'],
                        'end': timerange['start'] + timerange['duration'],
                        'content': texts[s['material_id']]
                    })

    def __read_content(self):
        with open(self.__file, 'r', encoding='utf-8') as f:
            self.__content = json.loads(f.read())

