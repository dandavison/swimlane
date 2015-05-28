from swimlane import Swimlane


def test_swimlane():
    swimlane = {
        'peers': ['client', 'server'],
        'messages': [
            ('client', 'server', "Send request"),
            ('server', 'client', "Send response"),
        ]
    }
    return Swimlane(swimlane).render().tostring()


if __name__ == '__main__':
    print test_swimlane()
