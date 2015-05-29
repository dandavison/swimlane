from collections import OrderedDict
from svgwrite import Drawing


CSS = '''
svg {
  padding:50px;
}
'''


class Swimlane(Drawing):
    peer_rect_width = 200
    peer_rect_height = 600
    peer_rect_gap = 100
    message_gap = 50
    text_padding = 5

    def __init__(self, parsed, *args, **kwargs):
        super(Swimlane, self).__init__(*args, **kwargs)
        self.defs.add(self.style(CSS))
        self._add_markers()
        self.peers = OrderedDict.fromkeys(parsed['peers'])
        self.messages = parsed['messages']
        self.have_peer_text = False

    def render(self):
        vertical_offset = 0
        for message_sequence in self.messages:
            self._draw_peer_rects([0, vertical_offset],
                                  self.message_gap * (len(message_sequence) + 1))
            vertical_offset += self.message_gap
            vertical_offset = self._draw_message_sequence(message_sequence,
                                                          vertical_offset)
            vertical_offset += self.message_gap
        return self

    def _draw_peer_rects(self, offset, height):
        for peer_name in self.peers:
            peer = self.make_peer_rect(offset, height)
            self.peers[peer_name] = peer
            self.add(peer)

            if not self.have_peer_text:
                self.add(self.make_peer_text(peer, peer_name))

            offset[0] += self.peer_rect_width + self.peer_rect_gap

        if not self.have_peer_text:
            self.have_peer_text = True

        return self

    def _draw_message_sequence(self, messages, vertical_offset):
        for message in messages:
            self.add(self.make_message_arrow(*message,
                                             vertical_offset=vertical_offset))
            self.add(self.make_message_text(*message,
                                            vertical_offset=vertical_offset))
            vertical_offset += self.message_gap

        return vertical_offset

    def make_peer_rect(self, offset, height):
        return self.rect(
            offset,
            (self.peer_rect_width, height),
            stroke='black',
            fill='white',
        )

    def make_peer_text(self, peer, peer_name):
        x = get_rect_midline(peer)
        y = peer['y'] - self.text_padding
        return self.text(peer_name, insert=(x, y))

    def make_message_text(self, source, target, message, vertical_offset):
        x = (get_rect_midline(self.peers[source]) +
             get_rect_midline(self.peers[target])) / 2.0

        y = vertical_offset - self.text_padding
        return self.text(message, insert=(x, y))

    def make_message_arrow(self, source, target, message, vertical_offset):
        source_x = get_rect_midline(self.peers[source])
        target_x = get_rect_midline(self.peers[target])
        line = self.line(
            (source_x, vertical_offset),
            (target_x, vertical_offset),
            stroke='black',
        )
        arrowhead = self.right_arrowhead if target_x > source_x else self.left_arrowhead
        line.set_markers((self.empty_marker, self.empty_marker, arrowhead))
        return line

    def _add_markers(self):
        self.left_arrowhead = self.make_left_arrowhead_marker()
        self.right_arrowhead = self.make_right_arrowhead_marker()
        self.empty_marker = self.make_empty_marker()

        for marker in [self.left_arrowhead,
                       self.right_arrowhead,
                       self.empty_marker]:
            self.defs.add(marker)
        return self

    def make_left_arrowhead_marker(self):
        marker = self.marker(insert=(5,5), size=(10,10))
        marker.add(self.path('M10,2 L10,11 L2,6 L10,2'))
        return marker

    def make_right_arrowhead_marker(self):
        marker = self.marker(insert=(5,5), size=(10,10))
        marker.add(self.path('M2,2 L2,11 L10,6 L2,2'))
        return marker

    def make_empty_marker(self):
        return self.marker()


def get_rect_midline(rect):
    return rect['x'] + rect['width'] / 2.0


if __name__ == '__main__':
    import json
    import sys

    (path,) = sys.argv[1:]

    with open(path) as fp:
        print Swimlane(json.load(fp)).render().tostring()
