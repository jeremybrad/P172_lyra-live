.PHONY: verify

verify:
	python3 -m pytest 60_tests/unit -q
