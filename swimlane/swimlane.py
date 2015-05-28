from svgwrite import Drawing


CSS = '''
svg {
  padding:50px;
}
'''


class Swimlane(Drawing):
    peer_rect_width = 200
    peer_rect_height = 800
    peer_rect_gap = 100
    message_gap = 100
    message_arrow_text_padding = 5

    def __init__(self, parsed, *args, **kwargs):
        super(Swimlane, self).__init__(*args, **kwargs)
        self.defs.add(self.style(CSS))
        self.peers = dict.fromkeys(parsed['peers'])
        self.messages = parsed['messages']

    def render(self):

        offset = [0, 0]
        for peer in self.peers:
            self.peers[peer] = self.make_peer_rect(offset)
            self.add(self.peers[peer])
            offset[0] += self.peer_rect_width + self.peer_rect_gap

        vertical_offset = self.message_gap
        for message in self.messages:
            self.add(self.make_message_arrow(*message,
                                             vertical_offset=vertical_offset))
            self.add(self.make_message_text(*message,
                                            vertical_offset=vertical_offset))
            vertical_offset += self.message_gap

        return self

    def make_peer_rect(self, offset):
        return self.rect(
            offset,
            (self.peer_rect_width, self.peer_rect_height),
            stroke='black',
            fill='white',
        )

    def make_message_arrow(self, source, target, message, vertical_offset):
        return self.line(
            (get_rect_midline(self.peers[source]), vertical_offset),
            (get_rect_midline(self.peers[target]), vertical_offset),
            stroke='black',
        )

    def make_message_text(self, source, target, message, vertical_offset):
        x = (get_rect_midline(self.peers[source]) +
             get_rect_midline(self.peers[target])) / 2.0

        y = vertical_offset - self.message_arrow_text_padding
        return self.text(message, insert=(x, y))


def get_rect_midline(rect):
    return rect['x'] + rect['width'] / 2.0


if __name__ == '__main__':
    swimlane = {
        'peers': ['client', 'server'],
        'messages': [
            ('client', 'server', "Send request"),
            ('server', 'client', "Send response"),
        ]
    }

    Swimlane(swimlane).render().saveas('swimlane.svg')
