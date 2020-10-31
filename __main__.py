"""
__main__.py
"""
from os import environ
import json
import boto3

AWS_ACCESS_KEY_ID = environ['aws_access_key_id']
AWS_SECRET_ACCESS_KEY = environ['aws_secret_access_key']
AWS_REGION_NAME = 'us-east-1'
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/..."
QUEUE_VISIBILITY_TIMEOUT_SECONDS = 30

COMMON_SQS_AND_ELASTIC_KEY = "SomeId"


class SqsMessage:
    """
    AWS SQS Message class
    """
    def __init__(self):
        self.session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                     region_name=AWS_REGION_NAME)
        self.sqs = self.session.client('sqs')

    def receive_message(self):
        """
        Receive single message from SQS queue
        :return:
        """
        response = self.sqs.receive_message(
            QueueUrl=QUEUE_URL,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=QUEUE_VISIBILITY_TIMEOUT_SECONDS,
            WaitTimeSeconds=0
        )

        try:
            _message = response['Messages'][0]
        except KeyError:
            return None

        return _message

    def receive_all_messages(self):
        """
        Receive all available messages from SQS queue
        :return:
        """
        all_messages = []
        while True:
            _message_resp = self.receive_message()
            if not _message_resp:
                break
            all_messages.append(_message_resp)

        return all_messages


def parse_attribute_from_message(message, attribute_name):
    """
    function parsing the attribute name from the SQS message body
    :param message:
    :param attribute_name:
    :return:
    """
    message_body_dict = json.loads(message["Body"])
    message_dict = json.loads(message_body_dict["Message"])
    message_resource_dict = message_dict.get("resource")
    try:
        return message_resource_dict[attribute_name]
    except KeyError as key_err:
        raise key_err


def get_dsl_query_filter_base():
    """
    function returning the base DSL query definition
    :return:
    """
    return {
        "bool": {
            "should": None,
        }
    }


def add_item_to_dsl_query_filter_should(filter_item):
    """
    function returning the DSL should filter single item
    :param filter_item:
    :return:
    """
    elastic_dsl_should = {
        "term": {
            COMMON_SQS_AND_ELASTIC_KEY: str(filter_item)
        }
    }
    return elastic_dsl_should


if __name__ == "__main__":
    MESSAGE = SqsMessage()
    RECEIVED_MESSAGES_LIST = MESSAGE.receive_all_messages()
    print('Received %s messages' % len(RECEIVED_MESSAGES_LIST))

    ATTRIBUTE_FOUND_ITEMS_LIST = []
    for received_message in RECEIVED_MESSAGES_LIST:
        ATTRIBUTE_FOUND_ITEMS_LIST.append(parse_attribute_from_message(received_message,
                                                                       COMMON_SQS_AND_ELASTIC_KEY))

    SHOULD_ITEMS_LIST = []
    for item in ATTRIBUTE_FOUND_ITEMS_LIST:
        SHOULD_ITEMS_LIST.append(add_item_to_dsl_query_filter_should(item))

    ELASTIC_DSL_BASE_QUERY = get_dsl_query_filter_base()
    ELASTIC_DSL_BASE_QUERY["bool"]["should"] = SHOULD_ITEMS_LIST

    print('Add this JSON to DSL query filter in your Kibana search:')
    print('--------------------------------------------------------')
    print(json.dumps(ELASTIC_DSL_BASE_QUERY))
