from datetime import timedelta
from datetime import datetime


def us_to_string(microseconds):
    return (datetime(1, 1, 1) + timedelta(microseconds=microseconds)).strftime('%H:%M:%S') + ',' + str((microseconds % 10**6) // 10**3).zfill(3)


class SrcFormatBuilder(object):
    def __init__(self, tracks):
        self.tracks = tracks

    def build(self):
        return self.__tracks_to_srt_string()

    def __tracks_to_srt_string(self):
        return '\n\n'.join(self.__tracks_to_srt_list())

    def __tracks_to_srt_list(self):
        self.tracks.sort(key=lambda x: x['start'])
        tracks_in_string = []

        for i, t in enumerate(self.tracks):
            tracks_in_string.append(
                '\n'.join([str(i + 1),
                           us_to_string(t['start']) + ' --> ' +
                           us_to_string(t['end']),
                           t['content']])
            )

        return tracks_in_string
