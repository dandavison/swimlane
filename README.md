##### Example

```
python swimlane/swimlane.py < examples/example.yaml > examples/example.svg
```

```yaml
messages:
- - [Loader, Server, 'Items for processing']
  - [Server, Redis, 'Create processing task']
  - [Server, Redis, 'Create processing task']
  - [Server, Redis, '...']
  - [Server, Loader, 'ACK']

- - [Worker, Redis, 'Request task']
  - [Redis, Worker, 'Task']
  - [Worker, DB, 'Save completed task', class: 'write']

- - [UI, Server, 'Request processing for item', class: 'human-initiated']
  - [Server, DB, 'Request processing for item', class: 'write']
  - [DB, Server, '']
  - [Server, UI, '']

peers:
- [UI, {}]
- [Loader, {}]
- [Server, {}]
- [Redis, {}]
- [Worker, {}]
- [DB, {}]

css:
- '.peer { stroke-width: 4px; stroke: #0ba00b; }'
- '.peer-label { stroke: blue; }'
- '.message-label { font-weight: bold; }'
- '.human-initiated { stroke: blue; }'
- '.write { stroke: red; }'
```

![](examples/example.png)
