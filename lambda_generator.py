import os
import json
from terrascript import *
import terrascript.aws.r as r

from awacs.helpers.trust import make_simple_assume_policy
from awacs.aws import PolicyDocument

application = 'components'

def create_lambda(title, handler):
    ts = Terrascript()

    def titled(name):
        return title + '_' + name

    def env_titled(name):
        return title + '_' + name + '_${terraform.workspace}'


    lambda_trust_policy = make_simple_assume_policy('lambda.amazonaws.com')

    role = ts.add(r.aws_iam_role(titled('role'), name=env_titled('role'), 
        assume_role_policy=lambda_trust_policy.to_json()))

    ts.add(r.aws_lambda_function(f'{title}',
        filename      = "${path.module}/target/" + title + ".zip",
        function_name = application + "_" + title + "_${terraform.workspace}",
        role          = role.arn,
        handler       = f"{title}.{handler}",
        runtime       = "python3.6",

        source_code_hash = "${base64sha256(file(\"${path.module}/target/" + title + ".zip\"))}",
        environment = {
            'variables': {
              "ENVIRONMENT": "${terraform.workspace}"
            }
        },

        tags = {
          'Name': application + '-${terraform.workspace}-' + title + '-lambda',
          'Application': application
        }
    ))

    permissions = {
      "Version": "2012-10-17",
      "Statement": [{"Action": "s3:*", "Resource": "*"}]
    }

    policy = ts.add(r.aws_iam_policy(titled('main_policy'), name=env_titled('main_policy'), 
        policy=json.dumps(permissions)))

    ts.add(r.aws_iam_role_policy_attachment(titled('policy_attachment'), role=role.name, policy_arn=policy.arn))

    tf = ts.dump()
    return tf


tf = create_lambda('test', 'invoke_handler')
print(tf)

with open(os.path.join(os.path.dirname(__file__), 'lambda_generated.tf.json'), 'w') as f:
    f.write(tf)