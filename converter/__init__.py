#!/usr/bin/env python
# coding: utf-8
import copy
import os
import re
import xml.etree.ElementTree as XmlParser

from opencc import OpenCC

from converter import utils

cc = OpenCC(conversion='t2s')


def srt_to_fcpxml(file_in, file_out):
    if not file_in:
        raise Exception('Unsupported Input File: %s' % file_in)
    if file_out.endswith('.srt'):
        if file_in.endswith('.srt'):
            return
        else:
            FcpxmlToSrtConverter(file_in, file_out).parse()
    elif file_out.endswith('.fcpxml'):
        if file_in.endswith('.fcpxml'):
            return
        else:
            SrtToFcpxmlConverter(file_in, file_out).parse()
    else:
        raise Exception('Unsupported Output File Type: %s' % file_out)


class SrtToFcpxmlConverter(object):
    def __init__(self, file_in, file_out, template='template.xml'):
        self.input = file_in
        self.output = file_out
        self.template = template
        self.framerate = 30
        self.framerate_tuple = (1000, 30000)
        self.data = None
        self.processed = False

    def parse(self):
        self._process()
        if self.processed:
            os.remove(self.input)
            self.template = TemplateEngine().check(self.template)
            self._write_to_file()

    def _process(self):
        with open(self.input, 'r', encoding='utf-8-sig') as f:
            lines = f.read().splitlines()
            f.close()

        lines = list(filter(lambda l: l != '', lines))
        data = []
        while len(lines) > 0:
            _seq, _duration, _text = lines[0], lines[1], lines[2]
            m = re.match('(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', _duration)
            start = self._wrap_time(m.groups()[0:4])
            end = self._wrap_time(m.groups()[4:8])
            data.append((start, end, _text))
            lines = lines[3:]
        self.data = data
        self.processed = True

    def _wrap_time(self, arr):
        return float(arr[0]) * 3600. + float(arr[1]) * 60. + float(arr[2]) + float(arr[3]) / 1000.

    def _write_to_file(self):
        if not self.data:
            return
        xml = XmlParser.parse(self.template)
        root = xml.getroot()
        library = root[1]
        event = library[0]
        event.set('uid', utils.gen_uuid())
        project = event[0]
        project.set('uid', utils.gen_uuid())
        project.set('modDate', utils.current_time())
        sequence = project[0]
        spine = sequence[0]
        gap = spine[0]
        title_template = gap.find('title')
        gap.remove(title_template)

        counter = 1
        for line in self.data:
            t_start, t_end, text = line
            # Init gap if not starting from 0s
            # if counter == 1 and t_start > 0:
            if counter == 1:
                gap.set('name', 'Gap')
                gap.set('offset', '0s')
                if t_start > 0:
                    gap.set('duration', self._wrap_xml_time(t_start))
                else:
                    gap.set('duration', "15000/30000s")
                gap.set('start', '0s')
            offset = self._wrap_xml_time(t_start)
            duration = self._wrap_xml_time(t_end - t_start)
            caption = cc.convert(text) if cc else text
            # Set title
            title = copy.deepcopy(title_template)
            title.set('name', '%s' % caption)
            title.set('offset', offset)
            title.set('duration', duration)
            title.set('start', offset)

            # Set caption xOy
            caption_xOy = title.findall('param')
            for cap_xOy in caption_xOy:
                if cap_xOy.get('name') == 'Position':
                    cap_xOy.set('value', '0 -175')

            # Set text
            text = title.find('text')
            text_style = text[0]
            text_style.set('ref', 'ts%d' % counter)
            text_style.text = caption

            # Set caption font style
            text_style_def = title.find('text-style-def')
            text_style_def.set('id', 'ts%d' % counter)

            # Append title element to spine
            gap.append(title)
            counter += 1

        with open(self.output, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<!DOCTYPE fcpxml>\n')
            f.write(XmlParser.tostring(root, encoding='UTF-8', xml_declaration=False).decode('utf-8'))
            f.write('\n')
            f.close()

    def _wrap_framerate_time(self, s, return_tuple=False):
        if '/' not in s:
            return float(s[:-1])
        components = s.split('/')
        x = float(components[0])
        y = float(components[1][:-1])
        # convert to int
        if return_tuple:
            return (int(components[0]), int(components[1][:-1]))
        return (x / y)

    def _wrap_xml_time(self, t):
        multiplier, denominator = self.framerate_tuple
        x = int(int(int(t * denominator) / multiplier)) * multiplier
        if x % denominator == 0:
            # whole number
            return '%ds' % (x / denominator)
        return f'{x}/{denominator}s'


class FcpxmlToSrtConverter(object):
    def __init__(self, file_in, file_out):
        self.input = file_in
        self.output = file_out
        self.data = None

    def parse(self):
        pass

    def _process(self):
        pass


class TemplateEngine(object):
    def __init__(self, template='template.xml'):
        """
        covert relative path to abspath
        :param template:
        """
        self.template = template
        self._init()

    def check(self, template):
        self.template = template
        self._init()
        return self.template

    def _init(self):
        self._process()

    def _process(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_abspath = '%s/%s' % (current_dir, self.template)
        if os.path.exists(template_abspath):
            self.template = template_abspath

