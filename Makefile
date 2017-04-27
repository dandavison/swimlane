examples/example.svg: swimlane/*
	swimlane examples/example.yaml > examples/example.svg

test:
	python tests/test_swimlane.py > /dev/null
