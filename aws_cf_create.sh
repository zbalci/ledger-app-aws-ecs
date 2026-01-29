aws cloudformation create-stack \
  --stack-name RollingStack \
  --template-url https://ledger-app-aws-iac.s3.eu-north-1.amazonaws.com/root.yaml \
  --disable-rollback \
  --capabilities CAPABILITY_IAM \
  --capabilities CAPABILITY_NAMED_IAM

aws cloudformation create-stack --stack-name RollingStack --capabilities CAPABILITY_IAM --capabilities CAPABILITY_NAMED_IAM --template-url https://ledger-app-aws-iac.s3.eu-north-1.amazonaws.com/root.yaml --disable-rollback