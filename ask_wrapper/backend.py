import json
import os
from io import StringIO
from json import JSONDecodeError
from subprocess import check_output
from typing import Optional

from ask_wrapper.cli_config_store import BaseCLIConfigStore, LocalASKDirectoryStorage
from ask_wrapper.log import debug


def _is_windows():
    return os.name == 'nt'


class BaseBackend:
    def send_command(self, command):
        raise NotImplementedError()

    def cmd_and_parse(self, command, is_json):
        debug('Sending command', cmd=' '.join(command))
        output = self.send_command(command)
        if type(output) is not str:
            output = output.decode('utf-8').strip()
        debug('Command returned', output=output[:100])
        if is_json:
            try:
                return json.loads(output)
            except JSONDecodeError:
                debug('Could not parse json', output=output)
                raise
        return output


class CLIBackend(BaseBackend):
    def __init__(self):
        self._shell_flag = _is_windows()

    def send_command(self, command):
        return check_output(command, shell=self._shell_flag)


class AWSLambdaBackend(BaseBackend):
    def __init__(self, cli_config_store: Optional[BaseCLIConfigStore] = None):
        import boto3
        self._client = boto3.client('lambda')
        if cli_config_store is None:
            cli_config_store = LocalASKDirectoryStorage()
        self._cli_config_store: BaseCLIConfigStore = cli_config_store

    @staticmethod
    def _extract_file_arg(args: list):
        for file_term in ('-f', '--file'):
            if file_term in args:
                i = args.index(file_term)
                args.pop(i)
                return args.pop(i)

    def send_command(self, command):
        args = command[1:]
        request_payload = {
            'args': args,
            'cliConfig': self._cli_config_store.load()
        }
        file_arg = self._extract_file_arg(args)
        if file_arg:
            request_payload['fileContentObj'] = json.load(open(file_arg, 'r'))

        lambda_result = self._client.invoke(
            FunctionName='ask-cli-1',
            Payload=json.dumps(request_payload)
        )

        response_payload = lambda_result['Payload'].read().decode('utf8')
        response_obj = json.loads(response_payload)

        if 'cliConfig' not in response_obj:
            raise SystemError(response_payload)

        self._cli_config_store.save(response_obj['cliConfig'])

        if response_obj['stderr'] and not response_obj['stderr'].startswith('ETag: '):
            raise SystemError(response_obj['stderr'])

        return response_obj['stdout']
