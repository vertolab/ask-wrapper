import boto3
import json
import os


class BaseCLIConfigStore:
    def load(self) -> dict:
        raise NotImplementedError

    def save(self, cli_config: dict):
        raise NotImplementedError


class LocalASKDirectoryStorage(BaseCLIConfigStore):
    def __init__(self):
        self._cli_config_path = os.path.expanduser('~/.ask/cli_config')

    def load(self) -> dict:
        return json.load(open(self._cli_config_path, 'r'))

    def save(self, cli_config: dict):
        json.dump(cli_config, open(self._cli_config_path, 'w'), indent=2)


class DynamoDBStorage(LocalASKDirectoryStorage):
    def __init__(self, table_name: str, key_name: str, key_value: str='ask_cli_config'):
        super().__init__()
        self._table_name = table_name
        self._key_name = key_name
        self._key_value = key_value
        self._client = boto3.client('dynamodb')

    def load(self) -> dict:
        dynamodb_item = self._client.get_item(
            TableName=self._table_name,
            Key={
                self._key_name: {
                    'S': self._key_value
                }
            }
        )
        data = dynamodb_item.get('Item', {}).get('data')
        if data:
            return json.loads(data['S'])
        return super().load()

    def save(self, cli_config: dict):
        data = json.dumps(cli_config)
        self._client.put_item(
            TableName=self._table_name,
            Item={
                self._key_name: {
                    'S': self._key_value
                },
                'data': {
                    'S': data
                }
            }
        )
