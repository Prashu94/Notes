# Command index

The commands the labs and the service chapters actually use. Flags change. When one fails, run `aws <service> <operation> help` before you invent a replacement.

Profile for everything below: `AWS_PROFILE=sandbox` and a Region you mean to use.

## Identity

```bash
aws sts get-caller-identity
aws configure list
aws sts assume-role --role-arn arn:aws:iam::ACCOUNT:role/ROLE --role-session-name lab
aws sts get-session-token --serial-number arn:aws:iam::ACCOUNT:mfa/USER --token-code 123456
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::ACCOUNT:role/ROLE \
  --action-names s3:ListAllMyBuckets s3:CreateBucket
aws iam create-role --role-name ROLE --assume-role-policy-document file://trust.json
aws iam attach-role-policy --role-name ROLE --policy-arn arn:aws:iam::aws:policy/NAME
aws iam put-role-policy --role-name ROLE --policy-name inline --policy-document file://pol.json
```

## Organizations

```bash
aws organizations describe-organization
aws organizations list-roots
aws organizations create-policy --name NAME --type SERVICE_CONTROL_POLICY --content file://scp.json
aws organizations attach-policy --policy-id p-xxxx --target-id ou-xxxx
aws organizations detach-policy --policy-id p-xxxx --target-id ou-xxxx
aws organizations delete-policy --policy-id p-xxxx
```

## Network

```bash
aws ec2 create-vpc --cidr-block 10.40.0.0/16
aws ec2 modify-vpc-attribute --vpc-id vpc-xxxx --enable-dns-hostnames
aws ec2 create-subnet --vpc-id vpc-xxxx --cidr-block 10.40.1.0/24 --availability-zone us-east-1a
aws ec2 create-route-table --vpc-id vpc-xxxx
aws ec2 associate-route-table --route-table-id rtb-xxxx --subnet-id subnet-xxxx
aws ec2 create-vpc-endpoint --vpc-id vpc-xxxx \
  --service-name com.amazonaws.us-east-1.s3 --vpc-endpoint-type Gateway \
  --route-table-ids rtb-xxxx
aws ec2 describe-route-tables --route-table-ids rtb-xxxx
aws ec2 modify-instance-metadata-options --instance-id i-xxxx \
  --http-tokens required --http-put-response-hop-limit 2
```

## S3 and KMS

```bash
aws s3api create-bucket --bucket BUCKET --region us-east-1
aws s3api put-public-access-block --bucket BUCKET --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api put-bucket-versioning --bucket BUCKET --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket BUCKET --server-side-encryption-configuration file://enc.json
aws s3api put-bucket-lifecycle-configuration --bucket BUCKET --lifecycle-configuration file://life.json
aws s3api list-object-versions --bucket BUCKET
aws s3api head-object --bucket BUCKET --key KEY
aws kms create-key --description lab
aws kms enable-key-rotation --key-id KEY_ID
```

## DynamoDB

```bash
aws dynamodb create-table --table-name T --billing-mode PAY_PER_REQUEST \
  --attribute-definitions AttributeName=pk,AttributeType=S AttributeName=sk,AttributeType=S \
  --key-schema AttributeName=pk,KeyType=HASH AttributeName=sk,KeyType=RANGE
aws dynamodb put-item --table-name T --item file://item.json \
  --condition-expression "attribute_not_exists(pk)"
aws dynamodb query --table-name T \
  --key-condition-expression "pk = :p" \
  --expression-attribute-values '{":p":{"S":"CUST#ada"}}' \
  --return-consumed-capacity TOTAL
aws dynamodb scan --table-name T --filter-expression "status = :s" \
  --expression-attribute-values '{":s":{"S":"OPEN"}}' \
  --return-consumed-capacity TOTAL
aws dynamodb delete-table --table-name T
```

## SQS, EventBridge, Lambda

```bash
aws sqs create-queue --queue-name Q
aws sqs send-message --queue-url URL --message-body '{}'
aws sqs get-queue-attributes --queue-url URL --attribute-names All
aws events put-rule --name R --event-pattern file://pattern.json
aws events put-targets --rule R --targets Id=q,Arn=QUEUE_ARN
aws events put-events --entries file://entries.json
aws lambda create-function --function-name F --runtime python3.12 \
  --role ROLE_ARN --handler handler.handler --zip-file fileb://function.zip --timeout 10
aws lambda create-event-source-mapping --function-name F --event-source-arn QUEUE_ARN \
  --batch-size 5 --function-response-types ReportBatchItemFailures
aws lambda publish-version --function-name F
aws lambda create-alias --function-name F --name live --function-version 1
aws lambda update-function-configuration --function-name F --tracing-config Mode=Active
aws lambda invoke --function-name F --payload '{}' --cli-binary-format raw-in-base64-out out.json
```

## API Gateway and Cognito

```bash
aws cognito-idp create-user-pool --pool-name P --username-attributes email
aws cognito-idp create-user-pool-client --user-pool-id POOL --client-name C --no-generate-secret \
  --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH
aws cognito-idp admin-set-user-password --user-pool-id POOL --username USER --password '...' --permanent
aws cognito-idp initiate-auth --auth-flow USER_PASSWORD_AUTH --client-id CLIENT \
  --auth-parameters USERNAME=USER,PASSWORD='...'
aws apigatewayv2 create-api --name A --protocol-type HTTP
aws apigatewayv2 create-authorizer --api-id API --authorizer-type JWT \
  --identity-source '$request.header.Authorization' --name cognito \
  --jwt-configuration Issuer=https://cognito-idp.REGION.amazonaws.com/POOL,Audience=CLIENT
aws apigatewayv2 create-stage --api-id API --stage-name '$default' --auto-deploy
```

## Deploy and observe

```bash
sam build
sam local invoke HelloWorldFunction --event events/event.json
sam deploy --guided
sam delete --stack-name STACK --no-prompts
aws cloudformation deploy --template-file template.yaml --stack-name STACK --capabilities CAPABILITY_IAM
aws cloudformation create-change-set --stack-name STACK --change-set-name review --template-body file://template.yaml
aws cloudformation describe-stack-events --stack-name STACK
aws logs tail /aws/lambda/F --since 30m
aws cloudwatch put-metric-alarm --alarm-name A --namespace AWS/Lambda --metric-name Errors \
  --dimensions Name=FunctionName,Value=F --statistic Sum --period 60 --evaluation-periods 1 \
  --threshold 1 --comparison-operator GreaterThanOrEqualToThreshold
aws xray get-trace-summaries --start-time START_EPOCH --end-time END_EPOCH
```

## Route 53

```bash
aws route53 create-health-check --caller-reference lab --health-check-config file://hc.json
aws route53 delete-health-check --health-check-id HC_ID
```

## Deletes people forget

NAT gateways, Elastic IPs, unattached EBS volumes, interface endpoints, Transit Gateway attachments, Global Accelerator, and noncurrent S3 versions. A budget email will not remove them.

```bash
aws ec2 describe-nat-gateways --filter Name=state,Values=available
aws ec2 describe-addresses --query 'Addresses[?AssociationId==null]'
aws ec2 describe-volumes --filters Name=status,Values=available
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE
```
