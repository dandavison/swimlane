from collections import OrderedDict
from contextlib import contextmanager
from itertools import chain

from svgwrite import Drawing


CSS = '''
svg {
  padding: 50px;
}
text.peer-label {
  font-weight: bold;
  font-size: x-large;
}
'''


class Swimlane(Drawing):
    peer_rect_width = 200
    peer_rect_gap = 100
    message_gap = 50
    peer_text_padding = 15
    message_text_padding = 8
    text_background_width = 3

    def __init__(self, parsed, *args, **kwargs):
        super(Swimlane, self).__init__(*args, **kwargs)
        self.defs.add(self.style(CSS))
        self._add_markers()
        self.peer_titles = OrderedDict(parsed['peers'])
        self.peers = OrderedDict.fromkeys(self.peer_titles)
        self.messages = parsed['messages']
        self.have_peer_text = False
        self.cursor = None

    def render(self):
        self.cursor = [0, 0]
        for message_sequence in self.messages:

            peer_names = flatten([
                [source, target]
                for (source, target, message) in message_sequence
            ])
            with self.save_excursion():
                self._draw_peer_rects(
                    self.message_gap * (len(message_sequence) + 1), peer_names)

            self.cursor[1] += self.message_gap
            self._draw_message_sequence(message_sequence)
            self.cursor[1] += self.message_gap / 2.0
        return self

    def _draw_peer_rects(self, height, peer_names):
        for peer_name in self.peers:
            peer = self.make_peer_rect(height)
            self.peers[peer_name] = peer

            if peer_name in peer_names:
                self.add(peer)

            if not self.have_peer_text:
                self.add(self.make_peer_text(peer, peer_name))

            self.cursor[0] += self.peer_rect_width + self.peer_rect_gap

        if not self.have_peer_text:
            self.have_peer_text = True

        return self

    def _draw_message_sequence(self, messages):
        for source, target, message in messages:
            arrow = self.make_message_arrow(source, target)
            self.add(arrow)
            self.add_message_text(message, arrow)
            self.cursor[1] += self.message_gap
        return self

    def make_peer_rect(self, height):
        return self.rect(
            self.cursor,
            (self.peer_rect_width, height),
            stroke='black',
            fill='white',
            rx=8,
            ry=8,
            class_='peer',
        )

    def make_peer_text(self, peer, peer_name):
        x = peer['x']
        y = peer['y'] - self.peer_text_padding
        text = self.text(
            peer_name,
            insert=(x, y),
            class_='peer-label',
        )
        text.set_desc(self.peer_titles[peer_name])
        return text

    def add_message_text(self, message, arrow):
        w = self.text_background_width
        for dx in range(-w, w + 1):
            for dy in range(-w, w + 1):
                self.add(self.make_message_text(
                    message,
                    arrow,
                    dx=[dx],
                    dy=[dy],
                    fill='white',
                ))
        self.add(self.make_message_text(
            message,
            arrow,
        ))

    def make_message_text(self, message, arrow, **kwargs):
        x1, x2 = sorted([arrow['x1'], arrow['x2']])
        x = x1 * 0.75 + x2 * 0.25
        y = self.cursor[1] - self.message_text_padding
        return self.text(
            message,
            insert=(x, y),
            class_='message-label',
            **kwargs
        )

    def make_message_arrow(self, source, target):
        source_x = get_rect_midline(self.peers[source])
        target_x = get_rect_midline(self.peers[target])
        line = self.line(
            (source_x, self.cursor[1]),
            (target_x, self.cursor[1]),
            stroke='black',
            class_='message',
        )
        line.set_markers(
            (self.empty_marker, self.empty_marker, self.arrowhead),
        )
        return line

    def _add_markers(self):
        self.arrowhead = self.make_arrowhead_marker()
        self.empty_marker = self.make_empty_marker()

        for marker in [self.arrowhead,
                       self.empty_marker]:
            self.defs.add(marker)
        return self

    def make_arrowhead_marker(self):
        marker = self.marker(
            insert=(-2, 0),
            size=(15, 15),
            viewBox="-6 -6 12 12",
            orient='auto',
            markerUnits='strokeWidth',
        )
        marker.add(self.polygon([(-2, 0), (-5, 5), (5, 0), (-5, -5)]))
        return marker

    def make_empty_marker(self):
        return self.marker()

    @contextmanager
    def save_excursion(self):
        initial_cursor = self.cursor[:]
        yield
        self.cursor = initial_cursor


def get_rect_midline(rect):
    return rect['x'] + rect['width'] / 2.0


def flatten(iterable):
    return list(chain.from_iterable(iterable))


if __name__ == '__main__':
    import json
    import sys

    (path,) = sys.argv[1:]

    with open(path) as fp:
        print Swimlane(json.load(fp)).render().tostring()
