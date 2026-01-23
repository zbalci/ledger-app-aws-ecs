aws cloudformation create-stack \
  --stack-name BlueGreenStack \
  --template-url https://ledger-app-aws-iac.s3.eu-north-1.amazonaws.com/0-main-stack.yaml \
  --disable-rollback \
  --capabilities CAPABILITY_IAM \
  --capabilities CAPABILITY_NAMED_IAM