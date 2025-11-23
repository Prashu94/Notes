# AWS Certificate Manager (ACM) - SAA-C03 Certification Guide

## Table of Contents
1. [Introduction](#introduction)
2. [SSL/TLS Fundamentals](#ssltls-fundamentals)
3. [Certificate Types](#certificate-types)
4. [AWS Certificate Manager Overview](#aws-certificate-manager-overview)
5. [Certificate Lifecycle Management](#certificate-lifecycle-management)
6. [Integration with AWS Services](#integration-with-aws-services)
7. [Security and Compliance](#security-and-compliance)
8. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
9. [Best Practices for SAA-C03](#best-practices-for-saa-c03)
10. [Exam Tips](#exam-tips)
11. [Hands-on Labs](#hands-on-labs)

---

## Introduction

AWS Certificate Manager (ACM) is a service that lets you provision, manage, and renew SSL/TLS certificates for your AWS-based websites and applications. ACM integrates with many AWS services, making it easy to secure your applications and encrypt data in transit.

### Key Benefits for SAA-C03
- **Free SSL/TLS certificates** for AWS services
- **Automatic certificate renewal** (no manual intervention)
- **Seamless integration** with AWS services
- **Centralized certificate management**
- **Enhanced security** with AWS services integration

---

## SSL/TLS Fundamentals

### What is SSL/TLS?
- **SSL (Secure Sockets Layer)**: Original protocol for securing communications
- **TLS (Transport Layer Security)**: Modern replacement for SSL
- **Purpose**: Encrypt data in transit between client and server

### How SSL/TLS Works
1. **Handshake Process**
   - Client connects to server
   - Server presents certificate
   - Client verifies certificate authenticity
   - Secure connection established

2. **Certificate Components**
   - **Public Key**: Used for encryption
   - **Private Key**: Used for decryption (kept secret)
   - **Digital Signature**: Proves certificate authenticity
   - **Certificate Authority (CA)**: Issues and validates certificates

### Certificate Validation Levels
1. **Domain Validation (DV)**
   - Validates domain ownership only
   - Fastest to obtain
   - Basic encryption

2. **Organization Validation (OV)**
   - Validates domain and organization
   - More thorough verification
   - Higher trust level

3. **Extended Validation (EV)**
   - Highest level of validation
   - Extensive verification process
   - Green address bar in browsers

---

## Certificate Types

### 1. Single Domain Certificates
- Secures one specific domain
- Example: `www.example.com`
- **Use Case**: Single website or application

### 2. Wildcard Certificates
- Secures main domain and all subdomains
- Example: `*.example.com` covers:
  - `api.example.com`
  - `blog.example.com`
  - `shop.example.com`
- **Use Case**: Multiple subdomains under same domain

### 3. Multi-Domain (SAN) Certificates
- Secures multiple different domains
- Subject Alternative Name (SAN) extension
- Example: `example.com`, `example.org`, `test.com`
- **Use Case**: Multiple domains under same organization

### Certificate Formats
- **PEM**: Privacy-Enhanced Mail format (most common)
- **DER**: Distinguished Encoding Rules (binary format)
- **PKCS#12**: Public Key Cryptography Standards (includes private key)

---

## AWS Certificate Manager Overview

### What ACM Provides
- **Free SSL/TLS certificates** for AWS resources
- **Automatic certificate provisioning**
- **Automatic renewal** (before expiration)
- **Integration with AWS services**
- **Certificate lifecycle management**

### ACM Certificate Types
1. **ACM-Issued Certificates**
   - Free certificates issued by Amazon
   - Automatically renewed
   - Can only be used with AWS services

2. **Imported Certificates**
   - Third-party certificates
   - You manage renewal
   - Can be used with AWS and non-AWS resources

### Regional Service
- ACM is a **regional service**
- Certificates are bound to specific regions
- For global services (CloudFront), use certificates from **us-east-1**

### Supported AWS Services
- **Application Load Balancer (ALB)**
- **Network Load Balancer (NLB)**
- **CloudFront**
- **API Gateway**
- **Elastic Beanstalk**
- **CloudFormation**

---

## Certificate Lifecycle Management

### 1. Certificate Provisioning

#### Requesting an ACM Certificate
```bash
# AWS CLI example
aws acm request-certificate \
    --domain-name example.com \
    --subject-alternative-names www.example.com \
    --validation-method DNS \
    --region us-east-1
```

#### Certificate Request Process
1. **Specify Domain Names**
   - Primary domain
   - Subject Alternative Names (SANs)

2. **Choose Validation Method**
   - DNS validation (recommended)
   - Email validation

3. **Complete Validation**
   - Prove domain ownership
   - Certificate issued upon successful validation

### 2. Domain Validation Methods

#### DNS Validation (Recommended)
- **Process**:
  1. ACM provides CNAME record
  2. Add CNAME to DNS configuration
  3. ACM validates domain ownership
  4. Certificate issued automatically

- **Advantages**:
  - Automated renewal possible
  - No email dependencies
  - More secure and reliable

#### Email Validation
- **Process**:
  1. ACM sends validation emails
  2. Click validation link in email
  3. Certificate issued upon validation

- **Email Addresses Used**:
  - `admin@domain.com`
  - `administrator@domain.com`
  - `hostmaster@domain.com`
  - `postmaster@domain.com`
  - `webmaster@domain.com`

### 3. Certificate Deployment

#### Automatic Deployment
- Select certificate during resource configuration
- ACM handles certificate installation
- No manual certificate file handling

#### Supported Deployment Scenarios
1. **Load Balancer SSL Termination**
2. **CloudFront Distribution**
3. **API Gateway Custom Domain**
4. **Elastic Beanstalk Environment**

### 4. Certificate Renewal

#### Automatic Renewal
- **ACM-issued certificates**: Automatically renewed
- **Validation**: Must remain valid for auto-renewal
- **Timeline**: Renewed ~60 days before expiration
- **Notification**: CloudWatch events for renewal status

#### Manual Renewal Requirements
- **Imported certificates**: Manual renewal required
- **Process**: Import new certificate before expiration
- **Monitoring**: Set up CloudWatch alarms for expiration

### 5. Certificate Deletion
- **Prerequisites**: Remove from all AWS resources
- **Impact**: Immediate termination of SSL/TLS functionality
- **Irreversible**: Cannot recover deleted certificates

---

## Integration with AWS Services

### 1. Application Load Balancer (ALB)

#### SSL Termination at ALB
```yaml
# CloudFormation example
Resources:
  MyLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Scheme: internet-facing
      Type: application
      
  MyListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref MyLoadBalancer
      Port: 443
      Protocol: HTTPS
      Certificates:
        - CertificateArn: !Ref MyCertificate
```

#### Benefits
- **Offload SSL processing** from backend instances
- **Centralized certificate management**
- **Multiple certificates** per load balancer
- **SNI (Server Name Indication)** support

### 2. CloudFront Distribution

#### Global SSL/TLS with CloudFront
- **Requirements**: Certificate must be in **us-east-1**
- **Benefits**: Global edge location SSL termination
- **Custom domains**: Attach ACM certificate to distribution

```json
{
  "ViewerCertificate": {
    "AcmCertificateArn": "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012",
    "SslSupportMethod": "sni-only",
    "MinimumProtocolVersion": "TLSv1.2_2021"
  }
}
```

### 3. API Gateway

#### Custom Domain Configuration
1. **Create custom domain** in API Gateway
2. **Associate ACM certificate**
3. **Map API stages** to custom domain
4. **Update DNS** to point to API Gateway

#### Regional vs Edge-Optimized
- **Regional**: Certificate in same region as API
- **Edge-Optimized**: Certificate must be in us-east-1

### 4. Elastic Beanstalk

#### SSL Configuration
- **Single instance**: Terminate SSL at instance level
- **Load balanced**: Terminate SSL at load balancer
- **Configuration**: Through Beanstalk environment settings

### 5. Network Load Balancer (NLB)

#### TLS Termination
- **Layer 4** load balancing with TLS termination
- **High performance** SSL/TLS processing
- **Preserve source IP** addresses

---

## Security and Compliance

### 1. Certificate Security

#### Private Key Security
- **ACM-managed**: Private keys never exposed
- **AWS KMS integration**: Keys encrypted at rest
- **Access control**: IAM policies control certificate access

#### Certificate Authority Trust
- **Amazon Trust Services**: ACM's certificate authority
- **Root CA**: Trusted by major browsers and operating systems
- **Cross-signed**: By well-known CAs for compatibility

### 2. Access Control

#### IAM Permissions for ACM
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "acm:RequestCertificate",
        "acm:ListCertificates",
        "acm:DescribeCertificate"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "acm:AddTagsToCertificate",
        "acm:RemoveTagsFromCertificate"
      ],
      "Resource": "arn:aws:acm:region:account:certificate/*"
    }
  ]
}
```

#### Resource-Based Policies
- **Certificate ARNs**: Reference specific certificates
- **Service permissions**: Allow AWS services to use certificates
- **Cross-account access**: Share certificates across accounts

### 3. Compliance Standards

#### Supported Compliance Frameworks
- **SOC 1, 2, 3**
- **PCI DSS Level 1**
- **ISO 27001**
- **FedRAMP**
- **HIPAA eligible**

#### Encryption Standards
- **TLS 1.2 and 1.3** support
- **Strong cipher suites**
- **Perfect Forward Secrecy (PFS)**
- **ECDSA and RSA** key algorithms

---

## Monitoring and Troubleshooting

### 1. CloudWatch Integration

#### Certificate Metrics
- **DaysToExpiry**: Days until certificate expires
- **Certificate validation status**
- **Renewal success/failure events**

#### CloudWatch Events
```json
{
  "source": ["aws.acm"],
  "detail-type": ["ACM Certificate Approaching Expiration"],
  "detail": {
    "DaysToExpiry": [45]
  }
}
```

### 2. Certificate Status Monitoring

#### Certificate States
- **PENDING_VALIDATION**: Awaiting domain validation
- **ISSUED**: Certificate successfully issued
- **INACTIVE**: Certificate not in use
- **EXPIRED**: Certificate has expired
- **VALIDATION_TIMED_OUT**: Validation failed
- **REVOKED**: Certificate has been revoked
- **FAILED**: Certificate request failed

#### Monitoring Best Practices
1. **Set up CloudWatch alarms** for expiration
2. **Monitor certificate status** regularly
3. **Track certificate usage** across services
4. **Automate certificate deployment**

### 3. Common Issues and Solutions

#### Validation Problems
- **DNS validation**: Check CNAME record propagation
- **Email validation**: Verify email delivery
- **Domain ownership**: Ensure proper DNS configuration

#### Certificate Deployment Issues
- **Region mismatch**: Ensure certificate is in correct region
- **Service compatibility**: Verify service supports ACM
- **Permission errors**: Check IAM policies

#### Renewal Failures
- **Validation requirements**: Maintain DNS/email validation
- **Resource association**: Keep certificate attached to resources
- **Domain changes**: Update certificate if domains change

---

## Best Practices for SAA-C03

### 1. Certificate Management Strategy

#### Planning Considerations
1. **Domain naming strategy**
   - Use wildcard certificates for subdomains
   - Plan for future domain requirements
   - Consider certificate sharing across services

2. **Regional deployment**
   - Request certificates in appropriate regions
   - Use us-east-1 for CloudFront
   - Plan for multi-region applications

3. **Validation method selection**
   - Prefer DNS validation for automation
   - Use email validation only when necessary
   - Maintain validation requirements for renewal

### 2. Architecture Patterns

#### Multi-Tier Application Security
```
Internet → CloudFront (ACM) → ALB (ACM) → Backend Instances
```

#### Microservices Architecture
- **API Gateway**: Custom domain with ACM certificate
- **Service mesh**: Individual service certificates
- **Load balancers**: SSL termination at multiple layers

#### Hybrid Architectures
- **ACM for AWS resources**
- **Imported certificates** for on-premises integration
- **Certificate synchronization** strategies

### 3. Cost Optimization

#### ACM vs Third-Party Certificates
- **ACM advantages**:
  - Free for AWS services
  - Automatic renewal
  - AWS service integration

- **Third-party considerations**:
  - Non-AWS resource usage
  - Specific CA requirements
  - Advanced certificate features

### 4. High Availability and Disaster Recovery

#### Multi-Region Certificate Strategy
1. **Replicate certificates** across regions
2. **Automate certificate provisioning**
3. **Monitor certificate status** globally
4. **Plan for certificate recovery**

#### Failover Scenarios
- **Primary region failure**: Certificates available in backup region
- **Certificate expiration**: Automatic renewal prevents outages
- **Validation failures**: Multiple validation methods as backup

---

## Exam Tips

### 1. Key Concepts for SAA-C03

#### Must-Know Facts
- **ACM certificates are free** for AWS services
- **Automatic renewal** only for ACM-issued certificates
- **Regional service** except for CloudFront (us-east-1)
- **DNS validation preferred** over email validation
- **Cannot export private keys** from ACM-issued certificates

#### Common Exam Scenarios
1. **SSL termination** at different layers
2. **Certificate validation** methods and troubleshooting
3. **Multi-region** certificate deployment
4. **Cost optimization** with ACM vs third-party certificates
5. **Integration patterns** with AWS services

### 2. Frequently Tested Topics

#### Certificate Lifecycle
- **Provisioning process** and requirements
- **Validation methods** and use cases
- **Renewal automation** and requirements
- **Certificate states** and troubleshooting

#### Service Integration
- **CloudFront**: Global distribution with us-east-1 certificate
- **ALB/NLB**: SSL termination and SNI support
- **API Gateway**: Custom domains and certificate association
- **Cross-service** certificate sharing limitations

### 3. Common Mistakes to Avoid

#### Regional Issues
- ❌ Using wrong region for CloudFront certificates
- ✅ Always use us-east-1 for CloudFront

#### Validation Problems
- ❌ Deleting DNS validation records
- ✅ Maintain validation records for auto-renewal

#### Certificate Management
- ❌ Manual certificate management for scalable applications
- ✅ Use ACM automation features

---

## Hands-on Labs

### Lab 1: Create and Deploy ACM Certificate with ALB

#### Objective
Deploy a secure web application using ACM certificate with Application Load Balancer.

#### Steps
1. **Request ACM Certificate**
   ```bash
   aws acm request-certificate \
       --domain-name myapp.example.com \
       --validation-method DNS \
       --region us-west-2
   ```

2. **Validate Domain Ownership**
   - Add CNAME record to DNS
   - Wait for validation completion

3. **Create Application Load Balancer**
   ```bash
   aws elbv2 create-load-balancer \
       --name my-secure-alb \
       --subnets subnet-12345 subnet-67890 \
       --security-groups sg-12345
   ```

4. **Configure HTTPS Listener**
   ```bash
   aws elbv2 create-listener \
       --load-balancer-arn arn:aws:elasticloadbalancing:... \
       --protocol HTTPS \
       --port 443 \
       --certificates CertificateArn=arn:aws:acm:...
   ```

### Lab 2: CloudFront Distribution with Custom Domain

#### Objective
Set up CloudFront distribution with custom domain and ACM certificate.

#### Prerequisites
- Domain registered and managed in Route 53
- Certificate requested in us-east-1

#### Implementation
1. **Request Certificate in us-east-1**
2. **Create CloudFront Distribution**
3. **Configure Custom Domain**
4. **Update Route 53 Records**

### Lab 3: API Gateway Custom Domain

#### Objective
Configure API Gateway with custom domain using ACM certificate.

#### Components
- REST API in API Gateway
- Custom domain configuration
- Route 53 alias record
- ACM certificate

---

## Conclusion

AWS Certificate Manager is a critical service for securing applications in AWS. For the SAA-C03 certification, focus on:

1. **Understanding certificate types** and validation methods
2. **Service integration patterns** and regional requirements
3. **Automation capabilities** and best practices
4. **Cost optimization** strategies
5. **Troubleshooting common issues**

### Key Takeaways
- **Free SSL/TLS certificates** for AWS services reduce costs
- **Automatic renewal** improves operational efficiency
- **DNS validation** enables automation and reliability
- **Regional considerations** are crucial for global applications
- **Integration patterns** vary by AWS service requirements

### Next Steps
1. Practice certificate provisioning and deployment
2. Implement monitoring and alerting
3. Design multi-region certificate strategies
4. Explore advanced integration patterns
5. Review exam objectives regularly

---

*This guide covers the essential ACM concepts and practices needed for the AWS Solutions Architect Associate (SAA-C03) certification. Regular hands-on practice and staying updated with AWS service changes will enhance your preparation.*