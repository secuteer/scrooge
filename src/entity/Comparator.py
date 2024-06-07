import difflib
import os
from io import StringIO
from typing import Callable

from src.entity.Change import  JaccardStructureChange, ParamChange, AsyncRequestsChange, \
    DHashStructureChange, AsyncRequestParamChange, AsyncResponseChange,NewRequestChange, MissingRequestChange
from src.entity.Request import StaticRequest
from src.entity.Snapshot import Snapshot
from src.schema.json_schema import create_request_json_schema
from src.shared.helpers import find_by_identifier, parse_multipart_formdata, sequence_matcher_to_txt, \
    remove_numbers_in_string
from bs4 import BeautifulSoup
from html2image import Html2Image
import dhash
from PIL import Image
from src.schema.json_schema import json_compare
from slugify import slugify
import shutil
import re



class Comparator:
    """
    Comparator class

    This class provides methods to compare requests of two snapshots and calculate the similarity between them.

    Attributes:
        snap1 (Snapshot): The first snapshot for comparison.
        snap2 (Snapshot): The second snapshot for comparison.

    Methods:
        check_similarity(identifier: str) -> float:
            Calculates the similarity between the requests of the two snapshots based on the given identifier.

        check_similarity_global():
            Calculates the global (for all requests) similarity between the two snapshots.
    """
    def __init__(self, snap1: Snapshot, snap2: Snapshot):
        self.snap1 = snap1
        self.snap2 = snap2

    def check_similarity(self, identifier: str) -> float:
        return 1

    def check_similarity_global(self):
        return


class SequenceComparator(Comparator):

    def __str__(self):
        return 'SequenceComparator'

    def check_similarity(self, identifier: str) -> float:
        r1 = find_by_identifier(self.snap1.static_requests, identifier)
        r2 = find_by_identifier(self.snap2.static_requests, identifier)
        if r1 and r2 is None:
            #r1.changes.append(PageMissingChange(1))
            return

        diff = difflib.SequenceMatcher(None, self.get_previous_requests_keys(r1),
                                        self.get_previous_requests_keys(r2))
        ratio = diff.ratio()
        #r1.changes.append(SequenceChange(1 - ratio))
        print(f'ratio {ratio}')

    @staticmethod
    def get_previous_requests_keys(request: StaticRequest) -> [str]:
        return sorted(map(lambda r: r.identifier, request.previous_requests))


class PagePresenceComparator(Comparator):

    def __str__(self):
        return 'Page Presence Comparator'

    def check_similarity_global(self):
        for static_request in self.snap1.static_requests:
            r2: StaticRequest = find_by_identifier(self.snap2.static_requests, static_request.identifier)
            if r2 is None:
                static_request.changes.append(MissingRequestChange(1))
            else:
                for async_request in static_request.async_requests:
                    r2_async_request = find_by_identifier(r2.async_requests, async_request.identifier)
                    if r2_async_request is None:
                        async_request.changes.append(MissingRequestChange(1))

        for static_request in self.snap2.static_requests:
            r1: StaticRequest = find_by_identifier(self.snap1.static_requests, static_request.identifier)
            if r1 is None:
                static_request.changes.append(NewRequestChange(1))
            else:
                for async_request in static_request.async_requests:
                    r1_async_request = find_by_identifier(r1.async_requests, async_request.identifier)
                    if r1_async_request is None:
                        async_request.changes.append(NewRequestChange(1))



class AsyncRequestsComparator(Comparator):

    def __str__(self):
        return 'Async Requests Comparator'

    def check_similarity(self, identifier: str) -> float:
        r1 = find_by_identifier(self.snap1.static_requests, identifier)
        r2 = find_by_identifier(self.snap2.static_requests, identifier)
        if r1 and r2 is None:
            return

        diff = difflib.SequenceMatcher(None, self.get_async_request_keys(r1), self.get_async_request_keys(r2))
        ratio = diff.ratio()
        if ratio < 1:
            r1.changes.append(AsyncRequestsChange(1 - ratio, sequence_matcher_to_txt(diff)))
            print(f'ratio {ratio}')

    @staticmethod
    def get_async_request_keys(request: StaticRequest) -> [str]:
        return sorted(map(lambda r: r.identifier, request.async_requests))




class ParamComperator(Comparator):

    def __str__(self):
        return 'ParamComperator'

    def check_similarity(self, identifier: str) -> float:
        r1 = find_by_identifier(self.snap1.static_requests, identifier)
        r2 = find_by_identifier(self.snap2.static_requests, identifier)
        if r1 and r2 is None:
            return

        if 'postData' in r1.har['request']:
            if 'params' in r1.har['request']['postData'] and r1.har['request']['postData']['params']:
                r1_param_names = sorted(map(lambda e: e['name'], r1.har['request']['postData']['params']))
                r2_param_names = sorted(map(lambda e: e['name'], r2.har['request']['postData']['params']))
            elif 'multipart/form-data' in r1.har['request']['postData']['mimeType']:
                r1_parsed_data = parse_multipart_formdata(r1.har['request']['postData']['text'],
                                                          r1.har['request']['postData']['mimeType'].split('=')[1])
                r1_param_names = sorted(list(r1_parsed_data.keys()))

                r2_parsed_data = parse_multipart_formdata(r2.har['request']['postData']['text'],
                                                          r2.har['request']['postData']['mimeType'].split('=')[1])
                r2_param_names = sorted(list(r2_parsed_data.keys()))
            else:
                r1_param_names = []
                r2_param_names = []

            diff = difflib.SequenceMatcher(None, r1_param_names, r2_param_names)
            ratio = diff.ratio()
            if ratio < 1:
                r1.changes.append(ParamChange(1 - ratio, sequence_matcher_to_txt(diff)))


class JaccardComparator(Comparator):

    def __str__(self):
        return 'JaccardComparator'

    def check_similarity(self, identifier: str) -> float:
        r1 = find_by_identifier(self.snap1.static_requests, identifier)
        r2 = find_by_identifier(self.snap2.static_requests, identifier)
        if r1 and r2 is None:
            # r1.changes.append(PageMissingChange(1))
            return

        (ratio, diff1, diff2) = self.compare_html_structures(html1=r1.content, html2=r2.content)
        if ratio < 1:
            r1.changes.append(JaccardStructureChange(1 - ratio, f"\nmissing: {', '.join(list(diff1))}\nnew: {', '.join(list(diff2))}"))
            print(f'ratio {ratio}')

    def compare_html_structures(self, html1, html2):

        struct1 = self.html_to_set(html1)
        struct2 = self.html_to_set(html2)

        diff1 = struct1.difference(struct2)
        diff2 = struct2.difference(struct1)

        # Calculate Jaccard similarity
        return (self.jaccard_similarity(struct1, struct2), diff1, diff2)

    def html_to_set(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        struct = []
        for tag in soup.find_all():
            #struct.append(tag.name)
            if tag.has_attr('class'):
                for c in tag['class']:
                    struct.append('.' + remove_numbers_in_string(c))
            if tag.has_attr('id'):
                struct.append('#'+remove_numbers_in_string(tag['id']))
            if tag.has_attr('name'):
                struct.append('name/'+tag['name'])
        return set(struct)




    @staticmethod
    def jaccard_similarity(set1, set2):
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        print(intersection, union)
        return intersection / union if union != 0 else 0


class DHashComparator(Comparator):
    def __init__(self, snap1, snap2, screenshot_dir):
        super().__init__(snap1, snap2)
        self.screenshot_dir = screenshot_dir
        shutil.rmtree(self.screenshot_dir, ignore_errors=True)
        os.mkdir(self.screenshot_dir)

    def __str__(self):
        return 'DHashComparator'

    def check_similarity(self, identifier: str) -> float:
        r1 = find_by_identifier(self.snap1.static_requests, identifier)
        r2 = find_by_identifier(self.snap2.static_requests, identifier)
        if r1 and r2 is None:
            return

        screenshot_path = './tmp/'
        hti = Html2Image(output_path=screenshot_path, custom_flags=['--disable-web-security --disable-xss-auditor --timeout=5 --disable-javascript'])
        hti.screenshot(html_str=r1.content, save_as='page1.png')
        hti.screenshot(html_str=r2.content, save_as='page2.png')
        hash1 = self.calculate_dhash(screenshot_path + 'page1.png')
        hash2 = self.calculate_dhash(screenshot_path + 'page2.png')

        similarity = self.calculate_similarity(hash1, hash2)
        if similarity < 0.99:
            snap1_save_png_path = self.screenshot_dir + 'snap1_' + slugify(identifier) + '.png'
            snap2_save_png_path = self.screenshot_dir + 'snap2_' + slugify(identifier) + '.png'
            os.rename(screenshot_path + 'page1.png', snap1_save_png_path)
            os.rename(screenshot_path + 'page2.png', snap2_save_png_path)
            r1.changes.append(DHashStructureChange(1 - similarity, f'\nsnap 1 screenshot: {snap1_save_png_path}\nsnap 2 screenshot: {snap2_save_png_path}'))

    @staticmethod
    def calculate_dhash(image_path):
        image = Image.open(image_path)
        row, col = dhash.dhash_row_col(image)
        return dhash.format_hex(row, col)

    @staticmethod
    def calculate_similarity(hash1, hash2):
        difference = (int(hash1, 16)) ^ (int(hash2, 16))
        return 1 - (bin(difference).count('1') / 128)


class AsyncStructureComparator(Comparator):

    def __str__(self):
        return 'AsyncStructureComparator'

    def check_similarity(self, identifier: str) -> float:
        r1: StaticRequest = find_by_identifier(self.snap1.static_requests, identifier)
        r2: StaticRequest = find_by_identifier(self.snap2.static_requests, identifier)

        if r2 is not None:
            for req in r1.async_requests:
                req2 = find_by_identifier(r2.async_requests, req.identifier)
                if req2 is None:
                    print("Req not existent in second snapshot")
                else:

                    if req.paramSchema and req2.paramSchema:
                        diff = json_compare(req.paramSchema, req2.paramSchema)
                        if diff:
                            req.changes.append(AsyncRequestParamChange(1, notice=diff))
                            # req2.changes.append(AsyncRequestParamChange(1, notice=diff))

                    if req.responseSchema and req2.responseSchema:
                        diff = json_compare(req.responseSchema, req2.responseSchema)
                        if diff:
                            req.changes.append(AsyncResponseChange(1, notice=diff))
                            # req2.changes.append(AsyncResponseChange(1, notice=diff))

        return 1
