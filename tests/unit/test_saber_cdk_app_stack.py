import aws_cdk as core
import aws_cdk.assertions as assertions

from saber_cdk_app.saber_cdk_app_stack import SaberCdkAppStack

# example tests. To run these tests, uncomment this file along with the example
# resource in saber_cdk_app/saber_cdk_app_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SaberCdkAppStack(app, "saber-cdk-app")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
