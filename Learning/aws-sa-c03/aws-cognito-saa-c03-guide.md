# AWS Cognito - SAA-C03 Certification Guide

## Table of Contents
1. [Introduction to AWS Cognito](#introduction-to-aws-cognito)
2. [Amazon Cognito User Pools](#amazon-cognito-user-pools)
3. [Amazon Cognito Identity Pools (Federated Identities)](#amazon-cognito-identity-pools-federated-identities)
4. [Authentication vs Authorization](#authentication-vs-authorization)
5. [Cognito Sync](#cognito-sync)
6. [Security Features](#security-features)
7. [Integration Patterns](#integration-patterns)
8. [Pricing and Cost Optimization](#pricing-and-cost-optimization)
9. [Best Practices](#best-practices)
10. [Common Exam Scenarios](#common-exam-scenarios)
11. [Troubleshooting](#troubleshooting)
12. [AWS CLI Commands Reference](#aws-cli-commands-reference)
13. [Hands-on Labs](#hands-on-labs)

---

## Introduction to AWS Cognito

### What is AWS Cognito?
Amazon Cognito is a fully managed identity service that provides user sign-up, sign-in, and access control functionality for web and mobile applications. It handles the complexities of identity management, allowing developers to focus on building their applications.

### Key Components
- **User Pools**: User directory service for authentication
- **Identity Pools (Federated Identities)**: Provide AWS credentials for accessing AWS resources
- **Cognito Sync**: Cross-device data synchronization (deprecated, use AppSync instead)

### Use Cases
- Mobile and web application authentication
- Social identity federation
- Enterprise identity federation (SAML, OpenID Connect)
- Serverless application security
- API Gateway authorization
- Temporary AWS credentials for mobile apps

---

## Amazon Cognito User Pools

### Overview
User Pools are user directories that provide sign-up and sign-in options for application users. They act as your own identity provider.

### Key Features

#### Authentication Methods
- **Username/Email and Password**: Traditional authentication
- **Multi-Factor Authentication (MFA)**: 
  - SMS-based MFA
  - Time-based One-Time Password (TOTP)
  - Software token MFA
- **Social Identity Providers**:
  - Facebook
  - Google
  - Amazon
  - Apple
  - LinkedIn
- **SAML Identity Providers**: Enterprise identity systems
- **OpenID Connect (OIDC) Providers**: Custom identity providers

#### User Management Features
- **User Registration**: Self-service sign-up
- **Email/Phone Verification**: Automatic verification workflows
- **Password Policies**: Customizable password requirements
- **Account Recovery**: Password reset via email/SMS
- **User Attributes**: Standard and custom user properties
- **User Groups**: Organize users for access control

#### Security Features
- **Adaptive Authentication**: Risk-based authentication
- **Device Tracking**: Remember and track user devices
- **Advanced Security Features**:
  - Compromised credential detection
  - Risk-based adaptive authentication
  - User behavior analytics

### Configuration Options

#### User Pool Settings
```json
{
  "PoolName": "MyUserPool",
  "Policies": {
    "PasswordPolicy": {
      "MinimumLength": 8,
      "RequireUppercase": true,
      "RequireLowercase": true,
      "RequireNumbers": true,
      "RequireSymbols": true
    }
  },
  "MfaConfiguration": "OPTIONAL",
  "AccountRecoverySetting": {
    "RecoveryMechanisms": [
      {
        "Priority": 1,
        "Name": "verified_email"
      }
    ]
  }
}
```

#### App Client Configuration
- **App Client Settings**: Configure OAuth flows and scopes
- **Callback URLs**: Where to redirect after authentication
- **Logout URLs**: Where to redirect after logout
- **OAuth Scopes**: Define permission levels
- **Refresh Token Expiration**: Token lifecycle management

### Tokens and JWT
User Pools issue three types of tokens:

#### ID Token
- Contains user identity information
- Used by client applications
- Contains claims about the authenticated user
- JWT format with user attributes

#### Access Token
- Used to access User Pool resources
- Contains scopes and groups
- Used with API Gateway for authorization
- Short-lived (1 hour by default)

#### Refresh Token
- Used to obtain new ID and Access tokens
- Longer-lived (30 days by default, configurable up to 10 years)
- Can be revoked for security

### Custom Attributes
- Define application-specific user properties
- Mutable vs Immutable attributes
- Required vs Optional attributes
- String, Number, Boolean, and DateTime types

### Lambda Triggers
Customize User Pool workflows with Lambda functions:

#### Authentication Flow Triggers
- **Pre Authentication**: Validate user before authentication
- **Post Authentication**: Custom logic after successful authentication
- **Pre Token Generation**: Modify token claims before issuance
- **Post Confirmation**: Actions after user confirms account

#### Message Triggers
- **Custom Message**: Customize verification and MFA messages
- **Custom SMS Sender**: Use custom SMS provider
- **Custom Email Sender**: Use custom email provider

#### User Migration
- **User Migration**: Import users from existing systems during sign-in

---

## Amazon Cognito Identity Pools (Federated Identities)

### Overview
Identity Pools provide temporary AWS credentials to users so they can access AWS services directly. They support both authenticated and unauthenticated (guest) users.

### Key Concepts

#### Identity Providers
- **Cognito User Pools**: Your own user directory
- **Social Identity Providers**: Facebook, Google, Amazon, Apple
- **OpenID Connect Providers**: Custom OIDC providers
- **SAML Identity Providers**: Enterprise identity systems
- **Developer Authenticated Identities**: Custom authentication backend

#### Identity Types
- **Authenticated Identities**: Users who have signed in through an identity provider
- **Unauthenticated Identities**: Guest users with limited permissions

### How It Works

#### Authentication Flow
1. User authenticates with an identity provider
2. Identity provider returns a token
3. Token is exchanged with Identity Pool
4. Identity Pool assumes an IAM role
5. Temporary AWS credentials are returned
6. User can access AWS services with these credentials

#### Role Selection
- **Authenticated Role**: For signed-in users
- **Unauthenticated Role**: For guest users
- **Role Resolution**: Rules-based or claims-based role selection
- **Enhanced Flow**: More granular role selection based on user attributes

### IAM Roles and Policies

#### Example Authenticated Role Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket/${cognito-identity.amazonaws.com:sub}/*"
      ]
    }
  ]
}
```

#### Policy Variables
- `${cognito-identity.amazonaws.com:sub}`: Unique user identifier
- `${cognito-identity.amazonaws.com:aud}`: Identity Pool ID
- `${saml:name}`: SAML attribute
- `${graph.facebook.com:id}`: Facebook user ID

### Enhanced (Simplified) Flow vs Classic Flow

#### Enhanced Flow (Recommended)
- More secure token validation
- Better performance
- Support for external identity providers
- Granular role selection

#### Classic Flow
- Legacy flow for backward compatibility
- Less secure token validation
- Limited role selection options

---

## Authentication vs Authorization

### Authentication (Who are you?)
- **User Pools**: Handle user authentication
- Verify user identity through credentials
- Issue tokens (ID, Access, Refresh)
- Support multiple authentication methods

### Authorization (What can you do?)
- **Identity Pools**: Provide access to AWS resources
- Issue temporary AWS credentials
- Control access through IAM roles and policies
- Support fine-grained permissions

### Common Patterns

#### Web/Mobile App + API Gateway
1. User authenticates with User Pool
2. Receives JWT tokens
3. Uses Access Token to call API Gateway
4. API Gateway validates token with User Pool

#### Direct AWS Service Access
1. User authenticates with User Pool
2. Exchanges token with Identity Pool
3. Receives temporary AWS credentials
4. Directly accesses AWS services (S3, DynamoDB, etc.)

#### Hybrid Approach
- Use User Pools for user management and authentication
- Use Identity Pools for AWS service access
- Combine both for comprehensive identity solution

---

## Cognito Sync

### Overview
**Note**: Cognito Sync is deprecated. Use AWS AppSync for new applications.

Cognito Sync was a service that synchronized user data across devices and platforms. It stored user data in datasets and synchronized them when the user came online.

### Key Features (Legacy)
- Cross-device data synchronization
- Offline data access
- Conflict resolution
- Push notifications for data changes

### Migration to AppSync
- **AWS AppSync**: GraphQL-based data synchronization
- Real-time capabilities
- Better offline support
- More flexible data modeling

---

## Security Features

### Multi-Factor Authentication (MFA)

#### SMS MFA
- Send verification codes via SMS
- Requires phone number verification
- Subject to SMS delivery limitations

#### TOTP MFA
- Time-based one-time passwords
- Works with authenticator apps (Google Authenticator, Authy)
- More secure than SMS
- No dependency on SMS delivery

#### Software Token MFA
- AWS managed software tokens
- Built into AWS applications
- Enhanced security features

### Advanced Security Features

#### Adaptive Authentication
- Risk-based authentication decisions
- Unusual sign-in detection
- Device and location analysis
- Automatic risk assessment

#### Compromised Credentials Detection
- Check against known compromised password databases
- Prevent use of leaked credentials
- Proactive security measures

#### Device Management
- Device tracking and remembering
- Device-based security policies
- Trusted device management

### Encryption and Data Protection
- **Data at Rest**: All user data encrypted
- **Data in Transit**: TLS encryption for all communications
- **Token Security**: JWT tokens with cryptographic signatures
- **Key Management**: AWS managed encryption keys

---

## Integration Patterns

### API Gateway Integration

#### JWT Authorizer
```yaml
# API Gateway Cognito Authorizer
CognitoAuthorizer:
  Type: AWS::ApiGateway::Authorizer
  Properties:
    Name: CognitoAuthorizer
    Type: COGNITO_USER_POOLS
    IdentitySource: method.request.header.Authorization
    RestApiId: !Ref MyApi
    ProviderARNs:
      - !GetAtt UserPool.Arn
```

#### Lambda Authorizer (Custom)
- Validate Cognito tokens in Lambda
- Implement custom authorization logic
- Return IAM policy for API access

### Application Load Balancer (ALB) Integration
- Native Cognito authentication support
- Authenticate users before reaching application
- Pass user information in headers

### Lambda Integration
- Use Cognito events to trigger Lambda functions
- Process user data and implement custom workflows
- Integrate with other AWS services

### S3 Integration
- Direct access to S3 with Identity Pool credentials
- User-specific S3 prefixes using policy variables
- Secure file uploads and downloads

### DynamoDB Integration
- Fine-grained access control with policy variables
- User-specific data isolation
- Attribute-level permissions

---

## Pricing and Cost Optimization

### User Pool Pricing

#### Monthly Active Users (MAU) Pricing
- **Free Tier**: 50,000 MAUs per month
- **Paid Tier**: $0.0055 per MAU after free tier
- MAU = Unique users who perform authentication operations

#### Advanced Security Features
- Additional cost for advanced security features
- Risk-based adaptive authentication
- Compromised credential detection

### Identity Pool Pricing
- **Free**: Identity Pool usage is free
- **AWS Service Costs**: Pay for underlying AWS services accessed
- **STS Costs**: Minimal costs for temporary credential generation

### Cost Optimization Strategies
- **Efficient Token Management**: Proper refresh token usage
- **User Pool Consolidation**: Single pool for multiple applications
- **Monitoring MAU**: Track active users to optimize costs
- **Cleanup Inactive Users**: Remove unused accounts

---

## Best Practices

### Security Best Practices

#### Authentication
- **Strong Password Policies**: Enforce complexity requirements
- **MFA Implementation**: Enable MFA for sensitive applications
- **Token Management**: Proper token storage and handling
- **Session Management**: Implement proper session timeouts

#### Authorization
- **Principle of Least Privilege**: Grant minimum required permissions
- **Regular Policy Reviews**: Audit IAM roles and policies
- **Resource Isolation**: Use policy variables for user-specific access
- **Monitoring and Logging**: Track authentication and authorization events

### Performance Best Practices

#### Token Caching
- Cache valid tokens to reduce API calls
- Implement proper token refresh logic
- Use SDK built-in token management

#### Connection Management
- Reuse connections where possible
- Implement proper retry logic
- Handle rate limiting gracefully

### Operational Best Practices

#### Monitoring and Alerting
- Monitor authentication failures
- Track unusual user behavior
- Set up CloudWatch alarms for key metrics

#### Backup and Recovery
- User Pool configuration backup
- Lambda function versioning
- Disaster recovery planning

#### Testing and Validation
- Test all authentication flows
- Validate MFA implementation
- Security penetration testing

---

## Common Exam Scenarios

### Scenario 1: Mobile App Authentication
**Question**: A mobile application needs user authentication with social sign-in support and the ability to access S3 buckets securely.

**Solution**:
- Use Cognito User Pool for authentication with social identity providers
- Use Cognito Identity Pool to provide temporary AWS credentials
- Configure IAM roles with S3 permissions using policy variables
- Implement proper token refresh in mobile app

### Scenario 2: Web Application with API Gateway
**Question**: A web application needs to authenticate users and authorize API calls through API Gateway.

**Solution**:
- Create Cognito User Pool for user authentication
- Configure API Gateway with Cognito Authorizer
- Use JWT Access Tokens for API authorization
- Implement proper error handling for expired tokens

### Scenario 3: Enterprise SSO Integration
**Question**: An organization wants to integrate their existing SAML identity provider with AWS resources.

**Solution**:
- Configure SAML identity provider in Cognito Identity Pool
- Set up appropriate IAM roles for different user types
- Use claims-based role selection for fine-grained access
- Implement proper attribute mapping

### Scenario 4: Guest User Access
**Question**: An application needs to provide limited access to unauthenticated users while offering full features to authenticated users.

**Solution**:
- Configure Identity Pool with both authenticated and unauthenticated roles
- Create separate IAM roles with different permissions
- Implement graceful upgrade path from guest to authenticated user
- Use policy conditions to restrict guest access

### Scenario 5: Multi-Tenant Application
**Question**: A SaaS application needs to isolate user data by tenant while using shared AWS resources.

**Solution**:
- Use custom user attributes to store tenant information
- Implement tenant-aware IAM policies using policy variables
- Use Lambda triggers to validate tenant access
- Configure resource naming conventions for tenant isolation

---

## Troubleshooting

### Common Issues and Solutions

#### Authentication Failures
**Issue**: Users cannot sign in
**Troubleshooting**:
- Check User Pool configuration
- Verify user account status (confirmed, enabled)
- Review password policy compliance
- Check MFA configuration
- Examine CloudWatch logs for detailed errors

#### Token Issues
**Issue**: Invalid or expired tokens
**Troubleshooting**:
- Verify token expiration settings
- Check token signature validation
- Ensure proper token refresh implementation
- Validate App Client configuration

#### Authorization Problems
**Issue**: Users cannot access AWS resources
**Troubleshooting**:
- Review IAM role trust relationships
- Check policy permissions and conditions
- Verify Identity Pool role mappings
- Test with AWS CLI using temporary credentials

#### Federation Issues
**Issue**: External identity provider integration problems
**Troubleshooting**:
- Verify identity provider configuration
- Check attribute mappings
- Review SAML assertions or OIDC claims
- Test identity provider connectivity

### Debugging Tools

#### CloudWatch Logs
- Enable detailed logging for User Pools
- Monitor authentication events
- Track API Gateway integration logs
- Analyze Lambda trigger execution

#### AWS CloudTrail
- Track Cognito API calls
- Monitor administrative changes
- Audit security events
- Compliance reporting

#### X-Ray Tracing
- Trace request flows through services
- Identify performance bottlenecks
- Debug integration issues
- Analyze service dependencies

---

## Hands-on Labs

### Lab 1: Basic User Pool Setup

#### Objective
Create a User Pool with email authentication and basic security features.

#### Steps
1. **Create User Pool**
   ```bash
   aws cognito-idp create-user-pool \
     --pool-name "MyFirstUserPool" \
     --policies '{
       "PasswordPolicy": {
         "MinimumLength": 8,
         "RequireUppercase": true,
         "RequireLowercase": true,
         "RequireNumbers": true,
         "RequireSymbols": false
       }
     }' \
     --auto-verified-attributes email
   ```

2. **Create App Client**
   ```bash
   aws cognito-idp create-user-pool-client \
     --user-pool-id <pool-id> \
     --client-name "WebAppClient" \
     --no-generate-secret \
     --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH
   ```

3. **Test User Registration**
   ```bash
   aws cognito-idp admin-create-user \
     --user-pool-id <pool-id> \
     --username testuser \
     --user-attributes Name=email,Value=test@example.com \
     --temporary-password TempPass123! \
     --message-action SUPPRESS
   ```

### Lab 2: Identity Pool with S3 Access

#### Objective
Set up an Identity Pool that provides access to user-specific S3 prefixes.

#### Steps
1. **Create Identity Pool**
   ```bash
   aws cognito-identity create-identity-pool \
     --identity-pool-name "MyIdentityPool" \
     --allow-unauthenticated-identities \
     --cognito-identity-providers \
       ProviderName=<user-pool-id>,ClientId=<app-client-id>,ServerSideTokenCheck=false
   ```

2. **Create IAM Role for Authenticated Users**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:GetObject",
           "s3:PutObject",
           "s3:DeleteObject"
         ],
         "Resource": [
           "arn:aws:s3:::my-user-bucket/${cognito-identity.amazonaws.com:sub}/*"
         ]
       }
     ]
   }
   ```

3. **Attach Roles to Identity Pool**
   ```bash
   aws cognito-identity set-identity-pool-roles \
     --identity-pool-id <identity-pool-id> \
     --roles authenticated=<authenticated-role-arn>,unauthenticated=<unauthenticated-role-arn>
   ```

### Lab 3: API Gateway Integration

#### Objective
Secure API Gateway endpoints using Cognito User Pool authorization.

#### Steps
1. **Create API Gateway REST API**
   ```bash
   aws apigateway create-rest-api \
     --name "SecureAPI" \
     --description "API secured with Cognito"
   ```

2. **Create Cognito Authorizer**
   ```bash
   aws apigateway create-authorizer \
     --rest-api-id <api-id> \
     --name "CognitoAuthorizer" \
     --type COGNITO_USER_POOLS \
     --provider-arns <user-pool-arn> \
     --identity-source method.request.header.Authorization
   ```

3. **Secure API Method**
   ```bash
   aws apigateway put-method \
     --rest-api-id <api-id> \
     --resource-id <resource-id> \
     --http-method GET \
     --authorization-type COGNITO_USER_POOLS \
     --authorizer-id <authorizer-id>
   ```

---

## AWS CLI Commands Reference

### User Pool Management

#### Create User Pool

```bash
# Create basic user pool
aws cognito-idp create-user-pool \
  --pool-name MyUserPool \
  --policies "PasswordPolicy={MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true,RequireSymbols=true}" \
  --auto-verified-attributes email \
  --username-attributes email \
  --region us-east-1

# Create user pool with advanced configuration
aws cognito-idp create-user-pool \
  --pool-name ProductionUserPool \
  --policies file://password-policy.json \
  --mfa-configuration OPTIONAL \
  --email-configuration SourceArn=arn:aws:ses:us-east-1:123456789012:identity/noreply@example.com,ReplyToEmailAddress=support@example.com \
  --sms-configuration SnsCallerArn=arn:aws:iam::123456789012:role/SNSRole \
  --user-attribute-update-settings AttributesRequireVerificationBeforeUpdate=email \
  --account-recovery-setting file://recovery-config.json \
  --tags Environment=Production,Application=MyApp \
  --region us-east-1

# Example password-policy.json
cat > password-policy.json <<'EOF'
{
  "PasswordPolicy": {
    "MinimumLength": 12,
    "RequireUppercase": true,
    "RequireLowercase": true,
    "RequireNumbers": true,
    "RequireSymbols": true,
    "TemporaryPasswordValidityDays": 7
  }
}
EOF

# Example recovery-config.json
cat > recovery-config.json <<'EOF'
{
  "RecoveryMechanisms": [
    {
      "Priority": 1,
      "Name": "verified_email"
    },
    {
      "Priority": 2,
      "Name": "verified_phone_number"
    }
  ]
}
EOF
```

#### Describe User Pool

```bash
# Get user pool details
aws cognito-idp describe-user-pool \
  --user-pool-id us-east-1_ABC123DEF \
  --region us-east-1

# Get user pool details with specific fields
aws cognito-idp describe-user-pool \
  --user-pool-id us-east-1_ABC123DEF \
  --query 'UserPool.[Name,Status,EstimatedNumberOfUsers,MfaConfiguration]' \
  --output table \
  --region us-east-1
```

#### Update User Pool

```bash
# Enable MFA
aws cognito-idp set-user-pool-mfa-config \
  --user-pool-id us-east-1_ABC123DEF \
  --mfa-configuration ON \
  --software-token-mfa-configuration Enabled=true \
  --region us-east-1

# Update user pool configuration
aws cognito-idp update-user-pool \
  --user-pool-id us-east-1_ABC123DEF \
  --policies "PasswordPolicy={MinimumLength=10,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true,RequireSymbols=false}" \
  --auto-verified-attributes email phone_number \
  --region us-east-1

# Enable advanced security features
aws cognito-idp update-user-pool \
  --user-pool-id us-east-1_ABC123DEF \
  --user-pool-add-ons AdvancedSecurityMode=ENFORCED \
  --region us-east-1
```

#### List User Pools

```bash
# List all user pools
aws cognito-idp list-user-pools \
  --max-results 60 \
  --region us-east-1

# List user pools with formatted output
aws cognito-idp list-user-pools \
  --max-results 60 \
  --query 'UserPools[*].[Name,Id,Status,CreationDate]' \
  --output table \
  --region us-east-1
```

#### Delete User Pool

```bash
# Delete user pool
aws cognito-idp delete-user-pool \
  --user-pool-id us-east-1_ABC123DEF \
  --region us-east-1
```

### User Pool Client Management

#### Create User Pool Client

```bash
# Create app client for web application
aws cognito-idp create-user-pool-client \
  --user-pool-id us-east-1_ABC123DEF \
  --client-name WebAppClient \
  --generate-secret \
  --allowed-o-auth-flows code implicit \
  --allowed-o-auth-scopes openid email profile \
  --allowed-o-auth-flows-user-pool-client \
  --callback-urls https://example.com/callback \
  --logout-urls https://example.com/logout \
  --supported-identity-providers COGNITO Google Facebook \
  --region us-east-1

# Create app client for mobile application
aws cognito-idp create-user-pool-client \
  --user-pool-id us-east-1_ABC123DEF \
  --client-name MobileAppClient \
  --no-generate-secret \
  --refresh-token-validity 30 \
  --access-token-validity 60 \
  --id-token-validity 60 \
  --token-validity-units AccessToken=minutes,IdToken=minutes,RefreshToken=days \
  --read-attributes email name phone_number \
  --write-attributes email name \
  --region us-east-1

# Create app client with custom authentication flow
aws cognito-idp create-user-pool-client \
  --user-pool-id us-east-1_ABC123DEF \
  --client-name CustomAuthClient \
  --explicit-auth-flows ALLOW_CUSTOM_AUTH ALLOW_REFRESH_TOKEN_AUTH ALLOW_USER_SRP_AUTH \
  --prevent-user-existence-errors ENABLED \
  --region us-east-1
```

#### Describe User Pool Client

```bash
# Get app client details
aws cognito-idp describe-user-pool-client \
  --user-pool-id us-east-1_ABC123DEF \
  --client-id 1234567890abcdef \
  --region us-east-1
```

#### Update User Pool Client

```bash
# Update app client configuration
aws cognito-idp update-user-pool-client \
  --user-pool-id us-east-1_ABC123DEF \
  --client-id 1234567890abcdef \
  --client-name UpdatedWebAppClient \
  --refresh-token-validity 60 \
  --region us-east-1
```

#### List User Pool Clients

```bash
# List all app clients
aws cognito-idp list-user-pool-clients \
  --user-pool-id us-east-1_ABC123DEF \
  --max-results 60 \
  --region us-east-1
```

### User Management

#### Create User

```bash
# Create user (admin)
aws cognito-idp admin-create-user \
  --user-pool-id us-east-1_ABC123DEF \
  --username john.doe@example.com \
  --user-attributes Name=email,Value=john.doe@example.com Name=name,Value="John Doe" Name=phone_number,Value="+1234567890" \
  --temporary-password TempPass123! \
  --message-action SUPPRESS \
  --region us-east-1

# Create user with auto-verification
aws cognito-idp admin-create-user \
  --user-pool-id us-east-1_ABC123DEF \
  --username jane.smith@example.com \
  --user-attributes Name=email,Value=jane.smith@example.com Name=email_verified,Value=true \
  --desired-delivery-mediums EMAIL \
  --region us-east-1
```

#### Confirm User Signup

```bash
# Admin confirm user
aws cognito-idp admin-confirm-sign-up \
  --user-pool-id us-east-1_ABC123DEF \
  --username john.doe@example.com \
  --region us-east-1
```

#### Set User Password

```bash
# Set permanent password (admin)
aws cognito-idp admin-set-user-password \
  --user-pool-id us-east-1_ABC123DEF \
  --username john.doe@example.com \
  --password NewPassword123! \
  --permanent \
  --region us-east-1
```

#### Get User Details

```bash
# Get user (admin)
aws cognito-idp admin-get-user \
  --user-pool-id us-east-1_ABC123DEF \
  --username john.doe@example.com \
  --region us-east-1

# List users
aws cognito-idp list-users \
  --user-pool-id us-east-1_ABC123DEF \
  --region us-east-1

# List users with filter
aws cognito-idp list-users \
  --user-pool-id us-east-1_ABC123DEF \
  --filter "email ^= \"john\"" \
  --region us-east-1

# List users with attributes
aws cognito-idp list-users \
  --user-pool-id us-east-1_ABC123DEF \
  --attributes-to-get email name phone_number \
  --region us-east-1
```

#### Update User Attributes

```bash
# Update user attributes (admin)
aws cognito-idp admin-update-user-attributes \
  --user-pool-id us-east-1_ABC123DEF \
  --username john.doe@example.com \
  --user-attributes Name=name,Value="John Updated" Name=phone_number,Value="+9876543210" \
  --region us-east-1
```

#### Delete User

```bash
# Delete user (admin)
aws cognito-idp admin-delete-user \
  --user-pool-id us-east-1_ABC123DEF \
  --username john.doe@example.com \
  --region us-east-1
```

#### Enable/Disable User

```bash
# Disable user
aws cognito-idp admin-disable-user \
  --user-pool-id us-east-1_ABC123DEF \
  --username john.doe@example.com \
  --region us-east-1

# Enable user
aws cognito-idp admin-enable-user \
  --user-pool-id us-east-1_ABC123DEF \
  --username john.doe@example.com \
  --region us-east-1
```

### Group Management

#### Create Group

```bash
# Create user group
aws cognito-idp create-group \
  --group-name Administrators \
  --user-pool-id us-east-1_ABC123DEF \
  --description "Administrator users with full access" \
  --role-arn arn:aws:iam::123456789012:role/CognitoAdminRole \
  --precedence 1 \
  --region us-east-1

# Create group without IAM role
aws cognito-idp create-group \
  --group-name Users \
  --user-pool-id us-east-1_ABC123DEF \
  --description "Standard users" \
  --precedence 10 \
  --region us-east-1
```

#### List Groups

```bash
# List all groups
aws cognito-idp list-groups \
  --user-pool-id us-east-1_ABC123DEF \
  --region us-east-1
```

#### Add User to Group

```bash
# Add user to group
aws cognito-idp admin-add-user-to-group \
  --user-pool-id us-east-1_ABC123DEF \
  --username john.doe@example.com \
  --group-name Administrators \
  --region us-east-1
```

#### Remove User from Group

```bash
# Remove user from group
aws cognito-idp admin-remove-user-from-group \
  --user-pool-id us-east-1_ABC123DEF \
  --username john.doe@example.com \
  --group-name Administrators \
  --region us-east-1
```

#### List Users in Group

```bash
# List group members
aws cognito-idp list-users-in-group \
  --user-pool-id us-east-1_ABC123DEF \
  --group-name Administrators \
  --region us-east-1
```

#### Delete Group

```bash
# Delete group
aws cognito-idp delete-group \
  --group-name Users \
  --user-pool-id us-east-1_ABC123DEF \
  --region us-east-1
```

### Identity Pool Management

#### Create Identity Pool

```bash
# Create identity pool with Cognito User Pool
aws cognito-identity create-identity-pool \
  --identity-pool-name MyIdentityPool \
  --allow-unauthenticated-identities \
  --cognito-identity-providers ProviderName=cognito-idp.us-east-1.amazonaws.com/us-east-1_ABC123DEF,ClientId=1234567890abcdef,ServerSideTokenCheck=false \
  --region us-east-1

# Create identity pool with multiple providers
aws cognito-identity create-identity-pool \
  --identity-pool-name ProductionIdentityPool \
  --no-allow-unauthenticated-identities \
  --cognito-identity-providers file://cognito-providers.json \
  --supported-login-providers "accounts.google.com"="YOUR_GOOGLE_CLIENT_ID" "graph.facebook.com"="YOUR_FACEBOOK_APP_ID" \
  --region us-east-1

# Example cognito-providers.json
cat > cognito-providers.json <<'EOF'
[
  {
    "ProviderName": "cognito-idp.us-east-1.amazonaws.com/us-east-1_ABC123DEF",
    "ClientId": "1234567890abcdef",
    "ServerSideTokenCheck": false
  }
]
EOF
```

#### Describe Identity Pool

```bash
# Get identity pool details
aws cognito-identity describe-identity-pool \
  --identity-pool-id us-east-1:12345678-1234-1234-1234-123456789012 \
  --region us-east-1
```

#### Update Identity Pool

```bash
# Update identity pool
aws cognito-identity update-identity-pool \
  --identity-pool-id us-east-1:12345678-1234-1234-1234-123456789012 \
  --identity-pool-name UpdatedIdentityPool \
  --allow-unauthenticated-identities \
  --region us-east-1
```

#### List Identity Pools

```bash
# List all identity pools
aws cognito-identity list-identity-pools \
  --max-results 60 \
  --region us-east-1
```

#### Set Identity Pool Roles

```bash
# Set IAM roles for identity pool
aws cognito-identity set-identity-pool-roles \
  --identity-pool-id us-east-1:12345678-1234-1234-1234-123456789012 \
  --roles authenticated=arn:aws:iam::123456789012:role/Cognito_AuthRole,unauthenticated=arn:aws:iam::123456789012:role/Cognito_UnauthRole \
  --region us-east-1

# Set roles with role mappings
aws cognito-identity set-identity-pool-roles \
  --identity-pool-id us-east-1:12345678-1234-1234-1234-123456789012 \
  --roles authenticated=arn:aws:iam::123456789012:role/Cognito_AuthRole,unauthenticated=arn:aws:iam::123456789012:role/Cognito_UnauthRole \
  --role-mappings file://role-mappings.json \
  --region us-east-1

# Example role-mappings.json
cat > role-mappings.json <<'EOF'
{
  "cognito-idp.us-east-1.amazonaws.com/us-east-1_ABC123DEF:1234567890abcdef": {
    "Type": "Token",
    "AmbiguousRoleResolution": "AuthenticatedRole"
  }
}
EOF
```

#### Get Identity Pool Roles

```bash
# Get IAM roles associated with identity pool
aws cognito-identity get-identity-pool-roles \
  --identity-pool-id us-east-1:12345678-1234-1234-1234-123456789012 \
  --region us-east-1
```

#### Delete Identity Pool

```bash
# Delete identity pool
aws cognito-identity delete-identity-pool \
  --identity-pool-id us-east-1:12345678-1234-1234-1234-123456789012 \
  --region us-east-1
```

### Identity Provider Configuration

#### Create SAML Provider

```bash
# Create SAML identity provider
aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_ABC123DEF \
  --provider-name MyCorpSAML \
  --provider-type SAML \
  --provider-details file://saml-provider-details.json \
  --attribute-mapping email=http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress,name=http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name \
  --region us-east-1

# Example saml-provider-details.json
cat > saml-provider-details.json <<'EOF'
{
  "MetadataURL": "https://idp.example.com/metadata"
}
EOF

# Or with metadata file
cat > saml-provider-details-file.json <<'EOF'
{
  "MetadataFile": "<?xml version=\"1.0\"?>..."
}
EOF
```

#### Create OIDC Provider

```bash
# Create OIDC identity provider
aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_ABC123DEF \
  --provider-name MyOIDCProvider \
  --provider-type OIDC \
  --provider-details client_id=YOUR_CLIENT_ID,client_secret=YOUR_CLIENT_SECRET,authorize_scopes="openid email profile",oidc_issuer=https://accounts.example.com \
  --attribute-mapping email=email,name=name,username=sub \
  --region us-east-1
```

#### Create Social Identity Provider

```bash
# Create Google identity provider
aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_ABC123DEF \
  --provider-name Google \
  --provider-type Google \
  --provider-details client_id=YOUR_GOOGLE_CLIENT_ID,client_secret=YOUR_GOOGLE_CLIENT_SECRET,authorize_scopes="openid email profile" \
  --attribute-mapping email=email,name=name,username=sub \
  --region us-east-1

# Create Facebook identity provider
aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_ABC123DEF \
  --provider-name Facebook \
  --provider-type Facebook \
  --provider-details client_id=YOUR_FACEBOOK_APP_ID,client_secret=YOUR_FACEBOOK_APP_SECRET,authorize_scopes="public_profile,email" \
  --attribute-mapping email=email,name=name,username=id \
  --region us-east-1
```

#### List Identity Providers

```bash
# List all identity providers
aws cognito-idp list-identity-providers \
  --user-pool-id us-east-1_ABC123DEF \
  --region us-east-1
```

#### Delete Identity Provider

```bash
# Delete identity provider
aws cognito-idp delete-identity-provider \
  --user-pool-id us-east-1_ABC123DEF \
  --provider-name MyCorpSAML \
  --region us-east-1
```

### Lambda Triggers

#### Set User Pool Lambda Triggers

```bash
# Configure Lambda triggers
aws cognito-idp update-user-pool \
  --user-pool-id us-east-1_ABC123DEF \
  --lambda-config file://lambda-config.json \
  --region us-east-1

# Example lambda-config.json
cat > lambda-config.json <<'EOF'
{
  "PreSignUp": "arn:aws:lambda:us-east-1:123456789012:function:PreSignUpTrigger",
  "PostConfirmation": "arn:aws:lambda:us-east-1:123456789012:function:PostConfirmationTrigger",
  "PreAuthentication": "arn:aws:lambda:us-east-1:123456789012:function:PreAuthenticationTrigger",
  "PostAuthentication": "arn:aws:lambda:us-east-1:123456789012:function:PostAuthenticationTrigger",
  "PreTokenGeneration": "arn:aws:lambda:us-east-1:123456789012:function:PreTokenGenerationTrigger",
  "CustomMessage": "arn:aws:lambda:us-east-1:123456789012:function:CustomMessageTrigger",
  "DefineAuthChallenge": "arn:aws:lambda:us-east-1:123456789012:function:DefineAuthChallengeTrigger",
  "CreateAuthChallenge": "arn:aws:lambda:us-east-1:123456789012:function:CreateAuthChallengeTrigger",
  "VerifyAuthChallengeResponse": "arn:aws:lambda:us-east-1:123456789012:function:VerifyAuthChallengeTrigger",
  "UserMigration": "arn:aws:lambda:us-east-1:123456789012:function:UserMigrationTrigger"
}
EOF
```

### MFA Configuration

#### Configure Software Token MFA

```bash
# Enable software token MFA
aws cognito-idp set-user-pool-mfa-config \
  --user-pool-id us-east-1_ABC123DEF \
  --software-token-mfa-configuration Enabled=true \
  --mfa-configuration OPTIONAL \
  --region us-east-1

# Enable SMS MFA
aws cognito-idp set-user-pool-mfa-config \
  --user-pool-id us-east-1_ABC123DEF \
  --sms-mfa-configuration SmsConfiguration={SmsAuthenticationMessage="Your authentication code is {####}",SnsCallerArn=arn:aws:iam::123456789012:role/SNSRole} \
  --mfa-configuration ON \
  --region us-east-1

# Enable both SMS and Software Token MFA
aws cognito-idp set-user-pool-mfa-config \
  --user-pool-id us-east-1_ABC123DEF \
  --software-token-mfa-configuration Enabled=true \
  --sms-mfa-configuration SmsConfiguration={SmsAuthenticationMessage="Your authentication code is {####}",SnsCallerArn=arn:aws:iam::123456789012:role/SNSRole} \
  --mfa-configuration OPTIONAL \
  --region us-east-1
```

#### Get MFA Configuration

```bash
# Get user pool MFA configuration
aws cognito-idp get-user-pool-mfa-config \
  --user-pool-id us-east-1_ABC123DEF \
  --region us-east-1
```

#### Set User MFA Preference

```bash
# Set MFA preference for user (admin)
aws cognito-idp admin-set-user-mfa-preference \
  --user-pool-id us-east-1_ABC123DEF \
  --username john.doe@example.com \
  --software-token-mfa-settings Enabled=true,PreferredMfa=true \
  --region us-east-1
```

### Password Policies

#### Update Password Policy

```bash
# Update password policy
aws cognito-idp update-user-pool \
  --user-pool-id us-east-1_ABC123DEF \
  --policies file://password-policy-update.json \
  --region us-east-1

# Example password-policy-update.json
cat > password-policy-update.json <<'EOF'
{
  "PasswordPolicy": {
    "MinimumLength": 14,
    "RequireUppercase": true,
    "RequireLowercase": true,
    "RequireNumbers": true,
    "RequireSymbols": true,
    "TemporaryPasswordValidityDays": 3
  }
}
EOF
```

### Authentication and Token Operations

#### Initiate Authentication

```bash
# Initiate auth with USER_SRP_AUTH flow
aws cognito-idp initiate-auth \
  --auth-flow USER_SRP_AUTH \
  --client-id 1234567890abcdef \
  --auth-parameters USERNAME=john.doe@example.com,SRP_A=<SRP_A_VALUE> \
  --region us-east-1

# Admin initiate auth
aws cognito-idp admin-initiate-auth \
  --user-pool-id us-east-1_ABC123DEF \
  --client-id 1234567890abcdef \
  --auth-flow ADMIN_NO_SRP_AUTH \
  --auth-parameters USERNAME=john.doe@example.com,PASSWORD=Password123! \
  --region us-east-1
```

#### Sign Out User

```bash
# Global sign out (admin)
aws cognito-idp admin-user-global-sign-out \
  --user-pool-id us-east-1_ABC123DEF \
  --username john.doe@example.com \
  --region us-east-1
```

### Domain Configuration

#### Create User Pool Domain

```bash
# Create Cognito domain
aws cognito-idp create-user-pool-domain \
  --user-pool-id us-east-1_ABC123DEF \
  --domain my-app-auth \
  --region us-east-1

# Create custom domain
aws cognito-idp create-user-pool-domain \
  --user-pool-id us-east-1_ABC123DEF \
  --domain auth.example.com \
  --custom-domain-config CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012 \
  --region us-east-1
```

#### Describe User Pool Domain

```bash
# Get domain details
aws cognito-idp describe-user-pool-domain \
  --domain my-app-auth \
  --region us-east-1
```

#### Delete User Pool Domain

```bash
# Delete domain
aws cognito-idp delete-user-pool-domain \
  --user-pool-id us-east-1_ABC123DEF \
  --domain my-app-auth \
  --region us-east-1
```

### Resource Tags

#### Tag User Pool

```bash
# Add tags to user pool
aws cognito-idp tag-resource \
  --resource-arn arn:aws:cognito-idp:us-east-1:123456789012:userpool/us-east-1_ABC123DEF \
  --tags Environment=Production,CostCenter=Engineering,Application=MyApp \
  --region us-east-1
```

#### List Tags

```bash
# List tags for user pool
aws cognito-idp list-tags-for-resource \
  --resource-arn arn:aws:cognito-idp:us-east-1:123456789012:userpool/us-east-1_ABC123DEF \
  --region us-east-1
```

#### Untag Resource

```bash
# Remove tags
aws cognito-idp untag-resource \
  --resource-arn arn:aws:cognito-idp:us-east-1:123456789012:userpool/us-east-1_ABC123DEF \
  --tag-keys Environment CostCenter \
  --region us-east-1
```

---

### Lab 4: Lambda Triggers

#### Objective
Implement custom authentication logic using Lambda triggers.

#### Lambda Function Example
```python
import json

def lambda_handler(event, context):
    # Pre Authentication Trigger
    if event['triggerSource'] == 'PreAuthentication_Authentication':
        # Custom validation logic
        username = event['userName']
        
        # Example: Block specific users
        if username in ['blocked_user1', 'blocked_user2']:
            raise Exception('User is blocked')
    
    # Post Authentication Trigger  
    elif event['triggerSource'] == 'PostAuthentication_Authentication':
        # Log successful authentication
        print(f"User {event['userName']} authenticated successfully")
        
        # Could trigger other actions like:
        # - Send welcome email
        # - Update user analytics
        # - Sync with external systems
    
    return event
```

---

## Key Takeaways for SAA-C03 Exam

### Critical Concepts to Remember

1. **User Pools vs Identity Pools**
   - User Pools: Authentication (who you are)
   - Identity Pools: Authorization (what you can access)
   - Often used together for complete solution

2. **Token Types and Usage**
   - ID Token: User identity information
   - Access Token: API access authorization
   - Refresh Token: Obtain new tokens

3. **Security Features**
   - MFA options and implementations
   - Adaptive authentication capabilities
   - Advanced security features

4. **Integration Patterns**
   - API Gateway authorization
   - Direct AWS service access
   - ALB authentication integration

5. **Cost Optimization**
   - MAU pricing model understanding
   - Free tier limitations
   - Cost-effective architecture patterns

### Exam Tips

1. **Read Questions Carefully**
   - Distinguish between authentication and authorization requirements
   - Look for keywords indicating specific Cognito features

2. **Understand Use Cases**
   - Mobile app scenarios often need Identity Pools
   - Web API scenarios typically use User Pools
   - Enterprise scenarios may involve SAML federation

3. **Security Best Practices**
   - Always choose most secure option when available
   - Consider MFA requirements
   - Understand principle of least privilege

4. **Integration Knowledge**
   - Know which AWS services integrate natively with Cognito
   - Understand token flow patterns
   - Be familiar with common architecture patterns

---

## Additional Resources

### AWS Documentation
- [Amazon Cognito Developer Guide](https://docs.aws.amazon.com/cognito/)
- [Cognito User Pools API Reference](https://docs.aws.amazon.com/cognito-user-identity-pools/)
- [Cognito Identity Pools API Reference](https://docs.aws.amazon.com/cognitoidentity/)

### AWS Training and Certification
- AWS Solutions Architect Associate exam guide
- AWS digital training courses
- AWS Skill Builder learning paths

### Best Practice Guides
- [Security Best Practices for Amazon Cognito User Pools](https://docs.aws.amazon.com/cognito/latest/developerguide/security.html)
- [Cognito Integration Patterns](https://aws.amazon.com/blogs/mobile/building-fine-grained-authorization-using-amazon-cognito-user-pools-groups/)

---

This comprehensive guide covers all the essential AWS Cognito concepts needed for the SAA-C03 certification exam. Focus on understanding the differences between User Pools and Identity Pools, security features, and common integration patterns. Practice with hands-on labs to reinforce your understanding of these concepts.