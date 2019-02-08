from builders.lambda_builder import Project
project = Project('components')

tf = project.lambda_builder('test', 'invoke_handler').add_s3_access().build()

print(tf)

import os

with open(os.path.join(os.path.dirname(__file__), 'lambda_generated.tf.json'), 'w') as f:
    f.write(tf)