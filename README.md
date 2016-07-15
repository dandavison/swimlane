
```
python swimlane/swimlane.py my_swimlane.json > my_swimlane.svg
```

##### Example

```json
{
  "peers": [
    ["Loader", "After loading data into the relational database, new items are sent to the processor server for processing."],
    ["UI", "The UI requests processings via AJAX."],
    ["Processor Server", "The Processor Server is responsible for causing N different processing tasks to be done to each item."],
    ["Redis", "Redis acts as the celery message broker: the web server sends tasks to redis, and celery worker processes take tasks from redis."],
    ["Processor Worker", "A celery worker consuming tasks for a single Processor."],
    ["DB", "Relational database accessed by both the server and celery worker processes."]
  ],
  "messages": [

    [["Loader", "Processor Server", "items for processing"],
     ["Processor Server", "Redis", "create processing task"],
     ["Processor Server", "Redis", "create processing task"],
     ["Processor Server", "Redis", "..."],
     ["Processor Server", "Loader", "ACK"]],

    [["Processor Worker", "Redis", "request task"],
     ["Redis", "Processor Worker", "task"],
     ["Processor Worker", "DB", "save completed task"]],

    [["UI", "Processor Server", "request processing for item"],
     ["Processor Server", "DB", "request processing for item"],
     ["DB", "Processor Server", "processing for item"],
     ["Processor Server", "UI", "processing for item"]
    ]
  ]
}
```

![](png/processing.png)
