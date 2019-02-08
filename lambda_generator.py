from builders.lambda_builder import build_lambda

tf = build_lambda('test', 'invoke_handler')
print(tf)

import os

with open(os.path.join(os.path.dirname(__file__), 'lambda_generated.tf.json'), 'w') as f:
    f.write(tf)