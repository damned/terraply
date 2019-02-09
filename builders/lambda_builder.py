import json
from terrascript import *
import terrascript.aws.r as r

from awacs.helpers.trust import make_simple_assume_policy
from awacs.aws import PolicyDocument

from ostruct import OpenStruct

class Project:
  def __init__(self, name):
    self.name = name

  def lambda_builder(self, title, handler):
    return LambdaBuilder(self.name, title, handler)


def snaked(*parts):
  return '_'.join(parts)


def roped(*parts):
  return '-'.join(parts).replace('_', '-')


def joined(*parts):
  return ''.join(parts)

refs = OpenStruct({
  'env': '${terraform.workspace}'
})


class StatementBuilder:
  def __init__(self):
    self.statement = {}

  def add_s3_access(self, what = 's3:*', which = '*'):
    self.statement['Action'] = what
    self.statement['Resource'] = which
    return self

  def build(self):
    return self.statement


class LambdaBuilder:
  def __init__(self, project, title, handler):
    self.project = project
    self.ts = Terrascript()
    self.title = title
    self.handler = handler
    self.role = self._default_lambda_role()


  def titled(self, name):
    return snaked(self.title, name)

  def env_titled(self, name):
    return snaked(self.title, name, refs.env)


  def _default_lambda_role(self):
    lambda_trust_policy = make_simple_assume_policy('lambda.amazonaws.com')

    return self._add(r.aws_iam_role(self.titled('role'), 
      name=self.env_titled('role'),
      assume_role_policy=lambda_trust_policy.to_json()
    ))
    

  def add_s3_access(self):
    self.add_permission(StatementBuilder().add_s3_access().build())
    return self


  def add_permission(self, statement):
    permissions = {
      "Version": "2012-10-17",
      "Statement": [statement]
    }

    policy = self._add(r.aws_iam_policy(self.titled('main_policy'), 
        name=self.env_titled('main_policy'),
        policy=json.dumps(permissions)))

    self._add(r.aws_iam_role_policy_attachment(self.titled('policy_attachment'), 
        role=self.role.name,
        policy_arn=policy.arn))


  def build(self):
    ts = self.ts
    title = self.title

    titled = self.titled
    env_titled = self.env_titled


    params = {
      'environment': {
        'variables': {
          "ENVIRONMENT": refs.env
        }
      },
      'tags': {
        'Name': roped(self.project, refs.env, title, 'lambda'),
        'Application': self.project
      }

    }


    ts.add(r.aws_lambda_function(f'{title}',
      filename      = joined("${path.module}/target/", title, ".zip"),
      function_name = snaked(self.project, title, refs.env),
      role          = self.role.arn,
      handler       = f"{title}.{self.handler}",
      runtime       = "python3.6",

      source_code_hash = "${base64sha256(file(\"${path.module}/target/" + title + ".zip\"))}",

      **params
    ))
    return ts.dump()


  def _add(self, resource):
    return self.ts.add(resource)
