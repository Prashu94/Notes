### Create Security Group
aws ec2 create-security-group --group-name "demosecgroup" --description "launch-wizard-1 created 2025-10-12T10:48:08.684Z" --vpc-id "vpc-05581ef371ea62a91" 

### Authorize Security Group Ingress
aws ec2 authorize-security-group-ingress --group-id "sg-preview-1" --ip-permissions '{"IpProtocol":"tcp","FromPort":22,"ToPort":22,"IpRanges":[{"CidrIp":"0.0.0.0/0"}]}' 
### Run Instances

aws ec2 run-instances --image-id "ami-052064a798f08f0d3" --instance-type "t3.micro" --key-name "videodemokp" --user-data "Iy9iaW4vYmFzaAp5dW0gdXBkYXRlIC15Cnl1bSBpbnN0YWxsIC15IGh0dHBkCnN5c3RlbWN0bCBzdGFydCBodHRwZApzeXN0ZW1jdGwgZW5hYmxlIGh0dHBk" --block-device-mappings '{"DeviceName":"/dev/sdb","Ebs":{"Encrypted":false,"DeleteOnTermination":false,"Iops":8000,"VolumeSize":8,"VolumeType":"io2"}}' --network-interfaces '{"AssociatePublicIpAddress":true,"DeviceIndex":0,"Groups":["sg-preview-1"]}' --credit-specification '{"CpuCredits":"unlimited"}' --tag-specifications '{"ResourceType":"instance","Tags":[{"Key":"Name","Value":"videodemoinstance"}]}' --metadata-options '{"HttpEndpoint":"enabled","HttpPutResponseHopLimit":2,"HttpTokens":"required"}' --private-dns-name-options '{"HostnameType":"ip-name","EnableResourceNameDnsARecord":true,"EnableResourceNameDnsAAAARecord":false}' --count "1" 

### Create VPC
aws ec2 create-vpc --instance-tenancy "default" --cidr-block "10.0.0.0/16" --tag-specifications '{"resourceType":"vpc","tags":[{"key":"Name","value":"Lab VPC 55467747"}]}' 