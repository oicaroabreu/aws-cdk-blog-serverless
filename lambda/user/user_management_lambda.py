import json
import os
import boto3
import datetime
from ulid import ulid


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)


def create_user(user_pool_id, username, fullname, email, password, profile_picture):
    client = boto3.client("cognito-idp")
    response = client.admin_create_user(
        UserPoolId=user_pool_id,
        Username=username,
        TemporaryPassword=password,
        UserAttributes=[
            {"Name": "name", "Value": fullname},
            {"Name": "email", "Value": email},
            {"Name": "custom:profile_picture", "Value": profile_picture},
        ],
    )
    return response


def get_user(user_pool_id, username):
    client = boto3.client("cognito-idp")
    response = client.admin_get_user(UserPoolId=user_pool_id, Username=username)

    return response


def list_users(user_pool_id):
    client = boto3.client("cognito-idp")
    response = client.list_users(UserPoolId=user_pool_id)
    return response["Users"]


def transform_users_data(users_data):
    transformed_data = []
    for user in users_data:
        transformed_user = {"id": user["Username"]}
        for attribute in user["Attributes"]:
            if attribute["Name"] == "name":
                transformed_user["name"] = attribute["Value"]
            elif attribute["Name"] == "email":
                transformed_user["email"] = attribute["Value"]
            elif attribute["Name"].startswith("custom:"):
                transformed_user[attribute["Name"].replace("custom:", "")] = attribute[
                    "Value"
                ]
        transformed_data.append(transformed_user)
    return transformed_data


def delete_user(user_pool_id, username):
    client = boto3.client("cognito-idp")
    response = client.admin_delete_user(UserPoolId=user_pool_id, Username=username)
    return response


def update_user_attributes(user_pool_id, username, fullname, email, profile_picture):
    client = boto3.client("cognito-idp")
    response = client.admin_update_user_attributes(
        UserPoolId=user_pool_id,
        Username=username,
        UserAttributes=[
            {"Name": "name", "Value": fullname},
            {"Name": "email", "Value": email},
            {"Name": "custom:profile_picture", "Value": profile_picture},
        ],
    )
    return response


def handler(event, context):
    print(json.dumps(event))
    user_pool_id = os.environ["USERPOOLID"]

    event["userPoolArn"] = user_pool_id

    http_method = event["httpMethod"]
    path_params = event["pathParameters"]

    user_id = None
    if path_params and "id" in path_params:
        user_id = path_params["id"]

    body = None
    if "body" in event and event["body"] is not None:
        body = json.loads(event["body"])

    default_password = os.environ["DEFAULT_PASSWORD"]

    if http_method == "POST":
        if body:
            response = create_user(
                user_pool_id,
                username=ulid(),
                fullname=body["name"],
                email=body["email"],
                password=default_password,
                profile_picture=body["profile_picture"],
            )
            print(response)

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "message": "User Saved Successfully",
                    }
                ),
            }
        else:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "message": "Bad Request",
                    }
                ),
            }
    elif http_method == "GET":
        if user_id:
            response = get_user(user_pool_id, user_id)
            print(response)
            # if "Item" in response:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(response),
            }
        else:
            response = list_users(user_pool_id)
            print(response)
            # if "Items" in response:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    transform_users_data(response), cls=CustomJSONEncoder
                ),
            }

    elif http_method == "PUT":

        if body:

            response = update_user_attributes(
                user_pool_id,
                username=user_id,
                fullname=body["name"],
                email=body["email"],
                profile_picture=body["profile_picture"],
            )
            print(response)

            # if "Attributes" in response:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {"message": f"User {user_id} has been updated succesfully"}
                ),
            }
        else:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "message": "Bad Request",
                    }
                ),
            }

    elif http_method == "DELETE":
        response = delete_user(user_pool_id, user_id)
        print(response)

        # if "ResponseMetadata" in response:
        #     if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"message": f"User {user_id} has been deleted succesfully"}
            ),
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Success"}),
    }
