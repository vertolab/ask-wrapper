from unittest import TestCase

from ask_wrapper.ask import Ask
from ask_wrapper.backend import AWSLambdaBackend, CLIBackend


class TestCLIBackend(TestCase):
    def test_send_command(self):
        ask_api = Ask(backend=CLIBackend())
        skills = ask_api.list_skills()
        self.assertGreater(len(skills), 2)


class TestAWSLambdaBackend(TestCase):
    def test_send_command(self):
        backend = AWSLambdaBackend()
        ask_api = Ask(backend=backend)
        skills = ask_api.list_skills()
        self.assertGreater(len(skills), 2)
