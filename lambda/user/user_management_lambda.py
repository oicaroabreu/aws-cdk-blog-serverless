import json
import os
import boto3
import datetime
from botocore.exceptions import ClientError
from ulid import ulid


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)


def create_user(user_pool_id, username, fullname, email, password, profile_picture):
    client = boto3.client("cognito-idp")
    try:

        attributes = [
            {"Name": "name", "Value": fullname},
            {"Name": "email", "Value": email},
        ]
        if profile_picture:
            attributes.append(
                {"Name": "custom:profile_picture", "Value": profile_picture}
            )

        response = client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
            TemporaryPassword=password,
            UserAttributes=attributes,
        )
        return 200, "User saved succesfully"
    except ClientError as e:
        print(f"Error creating user: {e.response}")
        return 400, e.response["message"]


def get_user(user_pool_id, username):
    client = boto3.client("cognito-idp")
    try:
        response = client.admin_get_user(UserPoolId=user_pool_id, Username=username)
        return 200, response
    except ClientError as e:
        print(f"Error creating user: {e.response}")
        return 400, e.response["message"]

    return response


def list_users(user_pool_id):
    client = boto3.client("cognito-idp")
    response = client.list_users(UserPoolId=user_pool_id)
    return response["Users"]


def transform_users_data(users_data):
    transformed_data = []
    for user in users_data:
        transformed_user = transform_single_user(user, "Attributes")
        transformed_data.append(transformed_user)
    return transformed_data


def transform_single_user(user_data, attr_field):
    transformed_user = {"id": user_data["Username"]}
    for attribute in user_data[attr_field]:
        if attribute["Name"] == "name":
            transformed_user["name"] = attribute["Value"]
        elif attribute["Name"] == "email":
            transformed_user["email"] = attribute["Value"]
        elif attribute["Name"].startswith("custom:"):
            transformed_user[
                attribute["Name"].replace("custom:profile_picture", "photo")
            ] = attribute["Value"]
    return transformed_user


def delete_user(user_pool_id, username):
    client = boto3.client("cognito-idp")
    try:
        response = client.admin_delete_user(UserPoolId=user_pool_id, Username=username)
        return 200, f"User {username} has been deleted succesfully"
    except ClientError as e:
        print(f"Error creating user: {e.response}")
        return 400, e.response["message"]


def update_user_attributes(user_pool_id, username, fullname, email, profile_picture):
    client = boto3.client("cognito-idp")
    try:

        attributes = [
            {"Name": "name", "Value": fullname},
            {"Name": "email", "Value": email},
        ]
        if profile_picture:
            attributes.append({"Name": "custom:profile_picture", "Value": profile_picture})

        response = client.admin_update_user_attributes(
            UserPoolId=user_pool_id,
            Username=username,
            UserAttributes=attributes,
        )
        print(response)
        return 200, f"User {username} updated succesfully"
    except ClientError as e:
        print(f"Error creating user: {e.response}")
        return 400, e.response["message"]


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

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent",
    }

    default_password = os.environ["DEFAULT_PASSWORD"]

    if http_method == "POST":
        if body:
            code, response = create_user(
                user_pool_id,
                username=ulid(),
                fullname=body["name"],
                email=body["email"],
                password=default_password,
                profile_picture=body.get("photo", None),
            )
            print(response)

            return {
                "statusCode": code,
                "headers": headers,
                "body": json.dumps(
                    {
                        "message": response,
                    }
                ),
            }
        else:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps(
                    {
                        "message": "Bad Request",
                    }
                ),
            }
    elif http_method == "GET":
        if user_id:
            code, response = get_user(user_pool_id, user_id)
            print(response)
            if "UserAttributes" in response:
                return {
                    "statusCode": 200,
                    "headers": headers,
                    "body": json.dumps(
                        transform_single_user(response, "UserAttributes"),
                        cls=CustomJSONEncoder,
                    ),
                }
            return {
                "statusCode": code,
                "headers": headers,
                "body": json.dumps(
                    {
                        "message": response,
                    }
                ),
            }
        else:
            response = list_users(user_pool_id)
            print(response)
            # if "Items" in response:
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps(
                    transform_users_data(response), cls=CustomJSONEncoder
                ),
            }

    elif http_method == "PUT":

        if body:

            code, response = update_user_attributes(
                user_pool_id,
                username=user_id,
                fullname=body["name"],
                email=body["email"],
                profile_picture=body.get("photo", None),
            )

            return {
                "statusCode": code,
                "headers": headers,
                "body": json.dumps(
                    {
                        "message": response,
                    }
                ),
            }
        else:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps(
                    {
                        "message": "Bad Request",
                    }
                ),
            }

    elif http_method == "DELETE":
        code, response = delete_user(user_pool_id, user_id)
        print(response)

        return {
            "statusCode": code,
            "headers": headers,
            "body": json.dumps(
                {"message": response}
            ),
        }

    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps({"message": "Success"}),
    }
