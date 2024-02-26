import json
import boto3

def handler(event, context):
    user_pool_id = event['userPoolId']
    email = event['request']['userAttributes']['email']

    cognito = boto3.client('cognito-idp')

    response = cognito.list_users(
        UserPoolId=user_pool_id,
        Filter=f'email = "{email}"'
    )

    if len(response['Users']) >  0:
        raise Exception('An account with this email address already exists.')

    return event