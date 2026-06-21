# Practice Test 03 — Deployment (DVA-C02)

**15 questions** · Domain 3 (24%) · Recommended time: 25 minutes

---

## Questions

### 1
Which tool is designed specifically for defining serverless applications as Infrastructure as Code?

A) AWS CloudFormation Designer only  
B) AWS SAM (Serverless Application Model)  
C) AWS Config  
D) AWS Service Catalog  

### 2
A developer runs `sam deploy` but API changes are not visible. What step was likely missed?

A) `sam build`  
B) Create a deployment and assign it to a stage in API Gateway  
C) `sam local invoke`  
D) Enable X-Ray tracing  

### 3
Which CodeDeploy deployment configuration gradually shifts 10% of traffic every minute to a new Lambda version?

A) AllAtOnce  
B) Canary10Percent5Minutes  
C) Linear10PercentEvery1Minute  
D) In-place deployment  

### 4
What does the SAM CLI command `sam local invoke` do?

A) Deploys the function to AWS  
B) Runs the Lambda function locally in a Docker container with a test event  
C) Creates a CloudFormation stack  
D) Runs integration tests in CodeBuild  

### 5
A CI/CD pipeline should automatically build and deploy when code is pushed to GitHub. Which AWS services are needed? (Select TWO.)

A) AWS CodePipeline  
B) Amazon Macie  
C) AWS CodeBuild  
D) Amazon GuardDuty  

### 6
A Lambda deployment package exceeds 50 MB zipped. What should the developer do?

A) Split into multiple Lambda functions only  
B) Upload the zip to S3 and reference it in the deployment, or use container images  
C) Reduce memory allocation  
D) Use Provisioned Concurrency  

### 7
Which file defines the build steps for AWS CodeBuild?

A) template.yaml  
B) buildspec.yml  
C) samconfig.toml  
D) package.json  

### 8
A developer needs different configuration values for dev and prod environments without changing code. Which approach is BEST?

A) Hardcode values in the Lambda handler  
B) Use CloudFormation parameters or SSM Parameter Store with environment-specific values  
C) Use the same configuration for all environments  
D) Store config in CloudWatch Logs  

### 9
What is the purpose of Lambda aliases?

A) Rename functions  
B) Point to specific function versions for deployment routing (dev, prod, canary)  
C) Increase memory  
D) Enable VPC access  

### 10
AWS AppConfig is used to:

A) Deploy Lambda functions  
B) Manage application configuration separately from code with validation and gradual deployment  
C) Store Docker images  
D) Create API Gateway stages  

### 11
A developer wants to preview CloudFormation stack changes before applying them. Which feature should be used?

A) Change set  
B) Stack drift detection  
C) Nested stack  
D) SAM local start-api  

### 12
Which deployment strategy deploys to an entirely new set of instances before switching traffic?

A) In-place rolling  
B) Blue/green  
C) All-at-once in-place  
D) Recreate  

### 13
In a SAM template, what does `Transform: AWS::Serverless-2016-10-31` enable?

A) CDK synthesis  
B) SAM-specific resource types like AWS::Serverless::Function  
C) Cross-region deployment  
D) Automatic testing  

### 14
A CodePipeline source stage can pull from which providers? (Select THREE.)

A) GitHub (via CodeStar Connections)  
B) AWS CodeCommit  
C) Amazon S3  
D) Amazon RDS  

### 15
After a failed CodeDeploy canary deployment, how should a developer roll back?

A) Delete the Lambda function  
B) Route the alias back to the previous version or let automatic rollback trigger via CloudWatch alarm  
C) Disable API Gateway  
D) Increase Lambda timeout  

---

See [answers.md](answers.md)
