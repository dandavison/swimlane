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

    def __init__(self, peers, *args, **kwargs):
        super(Swimlane, self).__init__(*args, **kwargs)
        self.defs.add(self.style(CSS))
        self.peers = peers

    def make_peer(self, origin):
        return self.rect(
            origin,
            (self.peer_rect_width, self.peer_rect_height),
            stroke='black',
            fill='white',
        )

    def render(self):

        origin = [0, 0]
        for peer in self.peers:
            self.add(self.make_peer(origin))
            origin[0] += self.peer_rect_width + self.peer_rect_gap

        return self


if __name__ == '__main__':
    peers = ['client', 'server']
    Swimlane(peers).render().saveas('swimlane.svg')
