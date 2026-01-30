aws cloudformation create-stack \
  --stack-name ledger-prod-foundation \
  --template-url https://ledger-app-aws-iac.s3.eu-north-1.amazonaws.com/foundation/root.yaml \
  --disable-rollback \
  --capabilities CAPABILITY_IAM \
  --capabilities CAPABILITY_NAMED_IAM

aws cloudformation create-stack \
  --stack-name ledger-prod-root \
  --template-url https://ledger-app-aws-iac.s3.eu-north-1.amazonaws.com/root.yaml \
  --disable-rollback \
  --capabilities CAPABILITY_IAM \
  --capabilities CAPABILITY_NAMED_IAM

aws cloudformation create-stack --stack-name db-init-lambda-build --template-body file://infrastructure/cloudformation/pipeline/db-init.yaml --capabilities CAPABILITY_IAM --capabilities CAPABILITY_NAMED_IAM

aws cloudformation create-stack --stack-name db-init-lambda-runtime --template-body file://infrastructure/cloudformation/database/db-init-runtime.yaml --capabilities CAPABILITY_IAM --capabilities CAPABILITY_NAMED_IAM