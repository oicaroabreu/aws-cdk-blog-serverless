from aws_cdk import (
    aws_lambda,
    aws_dynamodb,
    aws_events,
    aws_events_targets,
    aws_cognito,
    aws_apigateway,
    aws_iam,
    Duration,
    Stack,
)
import aws_cdk as cdk
import aws_cdk.aws_lambda_python_alpha as lambda_python
from constructs import Construct


class AwsCdkBlogServerlessStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        user_pool = aws_cognito.UserPool(
            self,
            "UserPool",
            user_pool_name="blog-user-pool",
            self_sign_up_enabled=True,
            sign_in_aliases=aws_cognito.SignInAliases(username=True),
            auto_verify=aws_cognito.AutoVerifiedAttrs(email=True),
            password_policy=aws_cognito.PasswordPolicy(
                min_length=8,
                require_digits=True,
                require_lowercase=True,
                require_uppercase=True,
            ),
            standard_attributes=aws_cognito.StandardAttributes(
                fullname=aws_cognito.StandardAttribute(required=True, mutable=True),
                email=aws_cognito.StandardAttribute(required=True, mutable=True),
            ),
            custom_attributes={
                "profile_picture": aws_cognito.StringAttribute(
                    min_len=0, max_len=2048, mutable=True
                )
            },
            account_recovery=aws_cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        posts_table = aws_dynamodb.Table(
            self,
            "blog-posts",
            partition_key=aws_dynamodb.Attribute(
                name="id", type=aws_dynamodb.AttributeType.STRING
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        themes_table = aws_dynamodb.Table(
            self,
            "blog-themes",
            partition_key=aws_dynamodb.Attribute(
                name="id", type=aws_dynamodb.AttributeType.STRING
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        lambda_layer = lambda_python.PythonLayerVersion(
            self,
            "blog_python_layer",
            entry="lambda/.dependencies",
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_8],
            description="Python layer for blog application",
        )

        user_management_lambda = lambda_python.PythonFunction(
            self,
            "UserManagerFunction",
            entry="lambda/user",
            index="user_management_lambda.py",
            handler="handler",
            layers=[lambda_layer],
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            environment={"USERPOOLID": user_pool.user_pool_id, "DEFAULT_PASSWORD": "g8CCfF249#io3qdw!"},
        )

        user_management_lambda.add_to_role_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "cognito-idp:AdminCreateUser",
                    "cognito-idp:AdminDeleteUser",
                    "cognito-idp:AdminUpdateUserAttributes",
                    "cognito-idp:ListUsers",
                    "cognito-idp:AdminGetUser",
                ],
                resources=[user_pool.user_pool_arn],
            )
        )

        email_filter_lambda = lambda_python.PythonFunction(
            self, "EmailFilterFunction",
            entry="lambda/user",
            index="email_filter_lambda.py",
            handler="handler",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
        )

        email_filter_lambda.add_to_role_policy(
            aws_iam.PolicyStatement(
                actions=["cognito-idp:ListUsers"],
                resources=[user_pool.user_pool_arn]
            )
        )

        user_pool.add_trigger(aws_cognito.UserPoolOperation.PRE_SIGN_UP, email_filter_lambda)

        themes_lambda_function = lambda_python.PythonFunction(
            self,
            "ThemesLambdaFunction",
            entry="lambda/theme",
            index="themes_lambda_function.py",
            handler="handler",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            layers=[lambda_layer],
            environment={
                "THEMES_TABLE_NAME": themes_table.table_name,
            },
        )

        themes_table.grant_read_write_data(themes_lambda_function)

        posts_lambda_function = lambda_python.PythonFunction(
            self,
            "PostsLambdaFunction",
            entry="lambda/post",
            index="posts_lambda_function.py",
            handler="handler",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            layers=[lambda_layer],
            environment={
                "POSTS_TABLE_NAME": posts_table.table_name,
            },
        )

        posts_table.grant_read_write_data(posts_lambda_function)

        api = aws_apigateway.RestApi(
            self,
            "blog-api",
            default_cors_preflight_options=aws_apigateway.CorsOptions(
                allow_origins=aws_apigateway.Cors.ALL_ORIGINS,
                allow_methods=aws_apigateway.Cors.ALL_METHODS,
                allow_headers=aws_apigateway.Cors.DEFAULT_HEADERS,
            ),
        )

        users = api.root.add_resource("users")
        users.add_method(
            http_method="GET",
            integration=aws_apigateway.LambdaIntegration(
                user_management_lambda, proxy=True
            ),
        )
        users.add_method(
            "POST",
            integration=aws_apigateway.LambdaIntegration(
                user_management_lambda, proxy=True
            ),
        )
        single_user = users.add_resource("{id}")
        single_user.add_method(
            "GET",
            integration=aws_apigateway.LambdaIntegration(
                user_management_lambda, proxy=True
            ),
        )
        single_user.add_method(
            "PUT",
            integration=aws_apigateway.LambdaIntegration(
                user_management_lambda, proxy=True
            ),
        )
        single_user.add_method(
            "DELETE",
            integration=aws_apigateway.LambdaIntegration(
                user_management_lambda, proxy=True
            ),
        )

        themes = api.root.add_resource("themes")
        themes.add_method(
            http_method="GET",
            integration=aws_apigateway.LambdaIntegration(
                themes_lambda_function, proxy=True
            ),
        )
        themes.add_method(
            "POST",
            integration=aws_apigateway.LambdaIntegration(
                themes_lambda_function, proxy=True
            ),
        )
        single_theme = themes.add_resource("{id}")
        single_theme.add_method(
            "GET",
            integration=aws_apigateway.LambdaIntegration(
                themes_lambda_function, proxy=True
            ),
        )
        single_theme.add_method(
            "PUT",
            integration=aws_apigateway.LambdaIntegration(
                themes_lambda_function, proxy=True
            ),
        )
        single_theme.add_method(
            "DELETE",
            integration=aws_apigateway.LambdaIntegration(
                themes_lambda_function, proxy=True
            ),
        )

        posts = api.root.add_resource("posts")
        posts.add_method(
            http_method="GET",
            integration=aws_apigateway.LambdaIntegration(
                posts_lambda_function, proxy=True
            ),
        )
        posts.add_method(
            "POST",
            integration=aws_apigateway.LambdaIntegration(
                posts_lambda_function, proxy=True
            ),
        )
        single_post = posts.add_resource("{id}")
        single_post.add_method(
            "GET",
            integration=aws_apigateway.LambdaIntegration(
                posts_lambda_function, proxy=True
            ),
        )
        single_post.add_method(
            "PUT",
            integration=aws_apigateway.LambdaIntegration(
                posts_lambda_function, proxy=True
            ),
        )
        single_post.add_method(
            "DELETE",
            integration=aws_apigateway.LambdaIntegration(
                posts_lambda_function, proxy=True
            ),
        )

        user_management_lambda.add_permission(
            "UserManagementLambdaInvoke",
            principal=aws_iam.ServicePrincipal("apigateway.amazonaws.com"),
            source_arn=api.arn_for_execute_api(),
        )

        themes_lambda_function.add_permission(
            "ThemesLambdaInvoke",
            principal=aws_iam.ServicePrincipal("apigateway.amazonaws.com"),
            source_arn=api.arn_for_execute_api(),
        )

        posts_lambda_function.add_permission(
            "PostsLambdaInvoke",
            principal=aws_iam.ServicePrincipal("apigateway.amazonaws.com"),
            source_arn=api.arn_for_execute_api(),
        )
