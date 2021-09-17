### Test suite for scenario tools

In order to test the heat demand curve generation and upload, I added a test suite.
Please install both `pytest` and `requests-mock` to use it. Simply run `pytest` in the terminal
to execute all tests. You can also just run a single test file with `pytest tests/path_to_file`. If one of you wants to extend the tools and make use of this new
testing environment, please feel free to do so! You can put global test settings in the `conftest`; files and methods that start with 'test' will automaitically be picked up and run.

Love, NS
