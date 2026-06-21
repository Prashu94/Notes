# Practice Test 03 — Answers

1. **B** — SAM extends CloudFormation for serverless resources.
2. **B** — API Gateway requires deployment to stage; SAM handles this during deploy but manual API changes need explicit deployment.
3. **C** — Linear10PercentEvery1Minute shifts 10% traffic every minute.
4. **B** — `sam local invoke` runs functions locally in Docker with test events.
5. **A and C** — CodePipeline orchestrates; CodeBuild compiles/tests/builds.
6. **B** — Upload to S3 for packages up to 250 MB unzipped, or use container images up to 10 GB.
7. **B** — buildspec.yml defines CodeBuild phases and commands.
8. **B** — CFN parameters, SSM Parameter Store, or AppConfig for environment-specific config.
9. **B** — Aliases are mutable pointers to versions for environment routing and canary.
10. **B** — AppConfig manages dynamic configuration with validation and gradual rollout.
11. **A** — Change sets preview additions/modifications/deletions before execution.
12. **B** — Blue/green creates new environment, switches traffic, keeps old for rollback.
13. **B** — Transform enables SAM resource types processed into CloudFormation.
14. **A, B, C** — CodePipeline supports GitHub, CodeCommit, S3, ECR as sources (not RDS).
15. **B** — Revert alias to previous version; CodeDeploy auto-rollback if alarm configured.
