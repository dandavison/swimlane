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

    def __init__(self, parsed, *args, **kwargs):
        super(Swimlane, self).__init__(*args, **kwargs)
        self.defs.add(self.style(CSS))
        self.peers = dict.fromkeys(parsed['peers'])
        self.messages = parsed['messages']

    def make_peer_rect(self, origin):
        return self.rect(
            origin,
            (self.peer_rect_width, self.peer_rect_height),
            stroke='black',
            fill='white',
        )

    def render(self):

        origin = [0, 0]
        for peer in self.peers:
            self.peers[peer] = self.make_peer_rect(origin)
            self.add(self.peers[peer])
            origin[0] += self.peer_rect_width + self.peer_rect_gap

        return self


if __name__ == '__main__':
    swimlane = {
        'peers': ['client', 'server'],
        'messages': [
            ('client', 'server', 'request'),
            ('server', 'client', 'response'),
        ]
    }

    Swimlane(swimlane).render().saveas('swimlane.svg')
