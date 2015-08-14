run-tests:
	tox -- py.test --pep8 tests

run-tests-continuously:
	tox -- py.test --pep8 --looponfail tests
