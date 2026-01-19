aws cloudformation create-stack \
  --stack-name FullStackRolling \
  --template-url https://ledger-app-aws-ecs-iac.s3.eu-central-1.amazonaws.com/0-main-stack.yaml \
  --disable-rollback \
  --capabilities CAPABILITY_IAM \
  --capabilities CAPABILITY_NAMED_IAM