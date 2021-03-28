import os
from aws_cdk import (
    aws_lambda,
    aws_apigateway as api_gw,
    aws_efs as efs,
    aws_ec2 as ec2,
    core
)


class ServerlessHuggingFaceStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # EFS needs to be setup in a VPC
        vpc = ec2.Vpc(self, 'Vpc', max_azs=2)

        # Create a file system in EFS to store cache models
        fs = efs.FileSystem(self, 'FileSystem',
                            vpc=vpc,
                            removal_policy=core.RemovalPolicy.DESTROY)
        access_point = fs.add_access_point('MLAccessPoint',
                                           create_acl=efs.Acl(
                                               owner_gid='1001', owner_uid='1001', permissions='750'),
                                           path="/export/models",
                                           posix_user=efs.PosixUser(gid="1001", uid="1001"))

        # Lambda Function for summarization
        summarization_image = aws_lambda.EcrImageCode.from_asset_image(
            directory=os.path.join(os.getcwd(), "summarization-image")
        )
        summarization_lambda = aws_lambda.Function(self,
                                                   id="summarizationContainerFunction",
                                                   description="Serverless Summarization Container Function",
                                                   code=summarization_image,
                                                   handler=aws_lambda.Handler.FROM_IMAGE,
                                                   runtime=aws_lambda.Runtime.FROM_IMAGE,
                                                   environment={
                                                       "TRANSFORMERS_CACHE": "/mnt/hf_models_cache"},
                                                   function_name="summarizationContainerFunction",
                                                   memory_size=8096,
                                                   timeout=core.Duration.seconds(
                                                       600),
                                                   vpc=vpc,
                                                   filesystem=aws_lambda.FileSystem.from_efs_access_point(
                                                       access_point, '/mnt/hf_models_cache'),
                                                   )

        # Lambda Function for sentiment analysis
        sentiment_analysis_image = aws_lambda.EcrImageCode.from_asset_image(
            directory=os.path.join(os.getcwd(), "sentiment-analysis-image")
        )
        sentiment_analysis_lambda = aws_lambda.Function(self,
                                                        id="sentimentAnalysisContainerFunction",
                                                        description="Serverless Sentiment Analysis Container Function",
                                                        code=sentiment_analysis_image,
                                                        handler=aws_lambda.Handler.FROM_IMAGE,
                                                        runtime=aws_lambda.Runtime.FROM_IMAGE,
                                                        environment={
                                                            "TRANSFORMERS_CACHE": "/mnt/hf_models_cache"},
                                                        function_name="sentimentAnalysisContainerFunction",
                                                        memory_size=1024,
                                                        timeout=core.Duration.seconds(
                                                            600),
                                                        vpc=vpc,
                                                        filesystem=aws_lambda.FileSystem.from_efs_access_point(
                                                            access_point, '/mnt/hf_models_cache'),
                                                        )

        # defines an API Gateway Http API resource backed by our functions.
        target_api = api_gw.RestApi(self, 'HuggingFaceAPI',
                                    rest_api_name='HuggingFace',
                                    endpoint_types=[
                                        api_gw.EndpointType.REGIONAL],
                                    deploy_options=api_gw.StageOptions(
                                        method_options={
                                            # This special path applies to all resource paths and all HTTP methods
                                            "/*/*": api_gw.MethodDeploymentOptions(
                                                throttling_rate_limit=100,
                                                throttling_burst_limit=200
                                            )
                                        })
                                    )
        sentiment_entity = target_api.root.add_resource('sentiment')
        sentiment_lambda_integration = api_gw.LambdaIntegration(sentiment_analysis_lambda, proxy=False, integration_responses=[
            api_gw.IntegrationResponse(status_code='200',
                                       response_parameters={
                                           'method.response.header.Access-Control-Allow-Origin': "'*'"
                                       })
        ])
        sentiment_entity.add_method('POST', sentiment_lambda_integration,
                          method_responses=[
                              api_gw.MethodResponse(status_code='200',
                                                    response_parameters={
                                                        'method.response.header.Access-Control-Allow-Origin': True
                                                    })
                          ])

        summarization_entity = target_api.root.add_resource('summarization')
        summarization_lambda_integration = api_gw.LambdaIntegration(summarization_lambda, proxy=False, integration_responses=[
            api_gw.IntegrationResponse(status_code='200',
                                       response_parameters={
                                           'method.response.header.Access-Control-Allow-Origin': "'*'"
                                       })
        ])
        summarization_entity.add_method('POST', summarization_lambda_integration,
                          method_responses=[
                              api_gw.MethodResponse(status_code='200',
                                                    response_parameters={
                                                        'method.response.header.Access-Control-Allow-Origin': True
                                                    })
                          ])

        core.CfnOutput(self, 'HTTP API Url', value=target_api.url)


app = core.App()
env = {'region': 'us-east-1'}

ServerlessHuggingFaceStack(app, "ServerlessHuggingFaceStack", env=env)

app.synth()
