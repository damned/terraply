import pytest

from pathlib import *
from subprocess import call

def test_lambda_unchanged():
  expected_tf = Path('expected_lambda.tf.json').read_text()

  if call('python3 lambda_generator.py', shell=True) != 0:
    raise Exception('generation failed')

  actual_tf = Path('lambda_generated.tf.json').read_text()
  assert expected_tf == actual_tf