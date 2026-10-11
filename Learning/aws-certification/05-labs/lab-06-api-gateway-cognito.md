# Lab 06 — HTTP API and a Cognito JWT

DVA skills 2.1. The client proves who it is with a user-pool token. The API rejects a missing token and rejects a token whose signature was not checked by API Gateway. The function reads the claim. It does not trust a tenant id from the body.

```bash
export AWS_PROFILE=sandbox
export AWS_DEFAULT_REGION=us-east-1
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
```

## 1. User pool and one user

```bash
POOL=$(aws cognito-idp create-user-pool \
  --pool-name lab06 \
  --username-attributes email \
  --auto-verified-attributes email \
  --policies 'PasswordPolicy={MinimumLength=12,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true,RequireSymbols=true}' \
  --query UserPool.Id --output text)

CLIENT=$(aws cognito-idp create-user-pool-client \
  --user-pool-id "$POOL" \
  --client-name lab06 \
  --no-generate-secret \
  --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH \
  --prevent-user-existence-errors ENABLED \
  --query UserPoolClient.ClientId --output text)

aws cognito-idp admin-create-user --user-pool-id "$POOL" \
  --username ada@example.com \
  --message-action SUPPRESS \
  --user-attributes Name=email,Value=ada@example.com Name=email_verified,Value=true

aws cognito-idp admin-set-user-password --user-pool-id "$POOL" \
  --username ada@example.com \
  --password 'Lab06-Correct-Horse!' \
  --permanent
```

`SUPPRESS` skips the invitation email. The address is fake. Do not point this pool at a real mailbox.

## 2. Function that reads the claim

```bash
mkdir -p /tmp/lab06
cat > /tmp/lab06/handler.py <<'PY'
def handler(event, context):
    claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
    tenant = claims.get("email", "unknown")
    return {"statusCode": 200, "body": '{"tenant":"%s"}' % tenant}
PY
cd /tmp/lab06 && zip -q function.zip handler.py

cat > /tmp/lab06-trust.json <<'EOF'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}
EOF
aws iam create-role --role-name Lab06Role --assume-role-policy-document file:///tmp/lab06-trust.json
aws iam attach-role-policy --role-name Lab06Role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
sleep 10

aws lambda create-function --function-name lab06-whoami \
  --runtime python3.12 \
  --role "arn:aws:iam::${ACCOUNT}:role/Lab06Role" \
  --handler handler.handler \
  --zip-file fileb:///tmp/lab06/function.zip --timeout 5
```

## 3. HTTP API, JWT authorizer, route

```bash
API=$(aws apigatewayv2 create-api --name lab06 --protocol-type HTTP --query ApiId --output text)
ISSUER="https://cognito-idp.${AWS_DEFAULT_REGION}.amazonaws.com/${POOL}"

AUTH=$(aws apigatewayv2 create-authorizer --api-id "$API" --authorizer-type JWT \
  --identity-source '$request.header.Authorization' --name cognito \
  --jwt-configuration "Issuer=${ISSUER},Audience=${CLIENT}" \
  --query AuthorizerId --output text)

INT=$(aws apigatewayv2 create-integration --api-id "$API" \
  --integration-type AWS_PROXY \
  --integration-uri "arn:aws:lambda:${AWS_DEFAULT_REGION}:${ACCOUNT}:function:lab06-whoami" \
  --payload-format-version 2.0 \
  --query IntegrationId --output text)

aws apigatewayv2 create-route --api-id "$API" --route-key 'GET /whoami' \
  --authorization-type JWT --authorizer-id "$AUTH" --target "integrations/${INT}"

aws lambda add-permission --function-name lab06-whoami --statement-id apigw \
  --action lambda:InvokeFunction --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:${AWS_DEFAULT_REGION}:${ACCOUNT}:${API}/*"

aws apigatewayv2 create-stage --api-id "$API" --stage-name '$default' --auto-deploy
URL=$(aws apigatewayv2 get-api --api-id "$API" --query ApiEndpoint --output text)
```

## 4. Call it wrong, then right

```bash
curl -sS -D- "$URL/whoami" -o /tmp/lab06-body.txt
# Expect 401. No token.

TOKEN=$(aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id "$CLIENT" \
  --auth-parameters USERNAME=ada@example.com,PASSWORD='Lab06-Correct-Horse!' \
  --query 'AuthenticationResult.IdToken' --output text)

curl -sS -H "Authorization: Bearer $TOKEN" "$URL/whoami"
```

The body contains the email from the token. Change the function so it prefers `event["body"]` for the tenant and you have built the bug the domain chapter describes. Put the tenant back on the claim before you delete the stack.

IAM auth (`authorization-type AWS_IAM`) is the other Associate answer, used when the caller is an AWS principal and you want SigV4. A Lambda authorizer is the answer when the token is not a Cognito JWT. Identity pools are the answer when the browser itself must call S3 or DynamoDB with temporary AWS credentials. This lab did not create an identity pool.

## Cleanup

```bash
aws apigatewayv2 delete-api --api-id "$API"
aws lambda delete-function --function-name lab06-whoami
aws cognito-idp delete-user-pool-client --user-pool-id "$POOL" --client-id "$CLIENT"
aws cognito-idp delete-user-pool --user-pool-id "$POOL"
aws iam detach-role-policy --role-name Lab06Role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name Lab06Role
rm -rf /tmp/lab06 /tmp/lab06-trust.json /tmp/lab06-body.txt
unset TOKEN
```

Deleting the pool deletes the user. The password was only in your shell history. Clear the history line if this laptop is shared.
