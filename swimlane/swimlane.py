from collections import defaultdict
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
    peer_rect_rx = 8
    peer_rect_ry = 8
    message_gap = 40
    peer_text_padding = 15
    message_text_padding = 8
    text_background_width = 3

    def __init__(self, parsed, *args, **kwargs):
        super(Swimlane, self).__init__(*args, **kwargs)
        user_css = '\n'.join(parsed.pop('css', []))
        self.defs.add(self.style(CSS + user_css))
        self._add_markers()
        self.peers = OrderedDict(parsed['peers'])
        self.messages = parsed['messages']
        self.have_peer_text = False
        self.cursor = None

    def render(self):
        self.cursor = [0, 0]
        for message_sequence in self.messages:
            with self.save_excursion():
                self._draw_peer_rects(message_sequence)
            self.cursor[1] += self.message_gap
            self._draw_message_sequence(message_sequence)
            self.cursor[1] += self.message_gap / 2.0
        return self

    def _draw_peer_rects(self, message_sequence):
        height = self.message_gap * (len(message_sequence) + 1)

        attrs = {}
        peer_names = set()

        for source, target, text, _attrs in iter_messages(message_sequence):
            if _attrs:
                if source in attrs:
                    raise AssertionError(
                        "Multiple attributes present for source %r. "
                        "Within a single message sequence, a single peer "
                        "may have attributes specified no more than once.")
                attrs[source] = _attrs
            peer_names.add(source)
            peer_names.add(target)

        for name in self.peers:
            rect = self.make_peer_rect(height, attrs.get(name, {}))
            self.peers[name]['rect'] = rect

            if name in peer_names:
                self.add(rect)

            if not self.have_peer_text:
                self.add(self.make_peer_text(name))

            self.cursor[0] += self.peer_rect_width + self.peer_rect_gap

        if not self.have_peer_text:
            self.have_peer_text = True

        return self

    def _draw_message_sequence(self, messages):
        initiating = True
        for source, target, text, attrs in iter_messages(messages):
            if source != target:
                arrowtail = self.initiating_arrowtail if initiating else None
                arrow = self.make_message_arrow(source, target, arrowtail)
                self.add(arrow)
                initiating = False
                x1, x2 = sorted([arrow['x1'], arrow['x2']])
                x = x1 * 0.75 + x2 * 0.25
            else:
                x = get_rect_left_midline(self.peers[source]['rect'])
            self.add_message_text(text, x)
            self.cursor[1] += self.message_gap
        return self

    def make_peer_rect(self, height, attrs):
        classes = ['peer']
        try:
            classes.append(attrs.pop('class'))
        except KeyError:
            pass

        kwargs = {
            'stroke': 'black',
            'fill': 'white',
            'rx': self.peer_rect_rx,
            'ry': self.peer_rect_ry,
            'class_': ' '.join(classes),
        }
        kwargs.update(attrs)

        return self.rect(
            self.cursor,
            (self.peer_rect_width, height),
            **kwargs
        )

    def make_peer_text(self, peer_name):
        peer = self.peers[peer_name]
        x = peer['rect']['x']
        y = peer['rect']['y'] - self.peer_text_padding
        text = self.text(
            peer.get('label', peer_name),
            insert=(x, y),
            class_='peer-label',
        )
        text.set_desc(peer.get('description', ''))
        return text

    def add_message_text(self, message, x):
        w = self.text_background_width
        for dx in range(-w, w + 1):
            for dy in range(-w, w + 1):
                self.add(self.make_message_text(
                    message,
                    x,
                    dx=[dx],
                    dy=[dy],
                    fill='white',
                ))
        self.add(self.make_message_text(
            message,
            x,
        ))

    def make_message_text(self, message, x, **kwargs):
        y = self.cursor[1] - self.message_text_padding
        return self.text(
            message,
            insert=(x, y),
            class_='message-label',
            **kwargs
        )

    def make_message_arrow(self, source, target, arrowtail=None):
        source_x = get_rect_midline(self.peers[source]['rect'])
        target_x = get_rect_midline(self.peers[target]['rect'])
        line = self.line(
            (source_x, self.cursor[1]),
            (target_x, self.cursor[1]),
            stroke='black',
            class_='message',
        )
        line.set_markers((
            arrowtail or self.empty_marker,
            self.empty_marker,
            self.arrowhead,
        ))
        return line

    def _add_markers(self):
        self.arrowhead = self.make_arrowhead_marker()
        self.initiating_arrowtail = self.make_square_marker()
        self.empty_marker = self.make_empty_marker()

        for marker in [self.initiating_arrowtail,
                       self.arrowhead,
                       self.empty_marker]:
            self.defs.add(marker)
        return self

    def make_arrowhead_marker(self):
        return self._make_marker(self.polygon(
            [(-2, 0), (-5, 5), (5, 0), (-5, -5)]
        ))

    def make_square_marker(self):
        return self._make_marker(self.polygon(
            [(-4, -4), (-4, 4), (4, 4), (4, -4)]
        ))

    def _make_marker(self, polygon):
        marker = self.marker(
            insert=(-2, 0),
            size=(15, 15),
            viewBox="-6 -6 12 12",
            orient='auto',
            markerUnits='strokeWidth',
        )
        marker.add(polygon)
        return marker

    def make_empty_marker(self):
        return self.marker()

    @contextmanager
    def save_excursion(self):
        initial_cursor = self.cursor[:]
        yield
        self.cursor = initial_cursor


def iter_messages(messages):
    """
    Yield 4-tuples; append empty attrs dict if missing.
    """
    for message in messages:
        if len(message) == 3:
            source, target, text = message
            yield source, target, text, {}
        elif len(message) == 4:
            yield tuple(message)
        else:
            raise ValueError("Invalid message: %r" % message)


def get_rect_midline(rect):
    return rect['x'] + rect['width'] * 0.5


def get_rect_left_midline(rect):
    return rect['x'] + rect['width'] * 0.1


def flatten(iterable):
    return list(chain.from_iterable(iterable))


def main():
    import yaml
    from sys import argv, stdin, stdout
    load = yaml.load

    if argv[1:]:
        (path,) = argv[1:]
        with open(path) as fp:
            data = load(fp)
    else:
        data = load(stdin.read())

    svg = Swimlane(data).render().tostring()
    stdout.write(svg)


if __name__ == '__main__':
    main()
