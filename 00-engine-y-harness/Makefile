.PHONY: demo-primitives demo-loop trace compare-harnesses test all

demo-primitives:
	python3 src/mini_agent.py --demo-primitives

demo-loop:
	python3 src/mini_agent.py --demo-loop

trace:
	python3 src/http_trace_inspector.py

compare-harnesses:
	python3 src/harness_trace_compare.py

test:
	python3 -m pytest -v tests/test_mini_agent.py sandbox_app/test_catalog_filter.py

all: demo-primitives demo-loop trace compare-harnesses test
