
Three Pillars Of Observability:
1. Metrics
	- Represents measured value which provides a specific point of data about the performance of the systems.
	- Helps in identifying specific thresholds and operations critical to observability.
2. Logs 
	- Helps in documenting and collecting information gathered while monitoring.
3. Traces
	- Records events, like HTTP request from a client, and follows the journey of this request through the system.
Amazon EC2 Events
- An event indicates a change in an environment, which are signals sent out when certain conditions are met.
- AWS can schedule events for your instances, such as reboot, start or stop, or retirement. These events do not occur frequently. If one of your instances will be affected by a scheduled event, AWS sends an email associated with the AWS account prior to the scheduled event.
- Health event, which can be used to monitor and manage Amazon CloudWatch events. 
- Examples of events:
	- Amazon EC2 generates events when the state of an instance changes from pending to running.
	- Amazon EC2 Auto Scaling generates events when it launches or terminates instances.
	- AWS CloudTrail publishes events when you make api calls.
Amazon EC2 Console: Observability Features
- Performs automated checks on each running EC2 instance to identify hardware and software issues. The results of these status checks display in the console to detect problems in the instance.
- 2 different types of instance status checks: 
	=> System status: monitor the AWS system and hardware on which instance runs.
		- Loss of n/w connectivity
		- Loss of system power
		- S/W issues on the physical host
		- H/W issues on the physical host that impact n/w reachability.
	=> Instance status: monitor the s/w and n/w configuration of individual instance.
		- Checks the health of the instance by sending an ARP (Address Resolution Protocol) request to NIC (Network Interface Card).
		- When an instance status check fails, which must address the problem.
		- Examples:
			- Failed system status checks
			- Incorrect networking or startup configuration
			- Exhausted memory
			- Corrupted file system.
			- Incompatible kernel.
- Status checks from the AWS CLI
```
	 aws ec2 describe-instance-status
```
	- When a status check fails, there is a corresponding CloudWatch metric for status checks that is incremented.

Amazon EC2 Metrics
- Metric for memory utilization, disk swap utilization, disk space utilization, page file utilization, and log collection are available when the CloudWatch agent is installed in the instance.
- Each data point in an EC2 instance covers a 5 minute period. Detailed monitoring can be activated by choosing Manage detailed monitoring.
- All of the EC2 metrics are stored in CloudWatch and can be viewed, searched, and visualized from CloudWatch dashboard.

Amazon CloudWatch
- Monitoring and observability service that you can use to monitor your applications.
- Collects monitoring and operational data in the form of logs, metrics and traces.
- Can create alarms from CloudWatch metrics, allowing to receive notifications when thresholds are breached.
- In addition you can create alarms that initiate Amazon EC2 Auto Scaling and Amazon SNS actions.
CloudWatch Elements
- Metrics
	- Exist only in the Region in which they are created.
	- Cannot be automatically deleted, but they automatically expire after 15 months if not new data is published to them.
	- Data points older than 15 months expire on a rolling basis; as new data points come in, data older than 15 months is dropped.
		
- Dimensions
- Dashboards
- Alarms
- Statistics
- Access
Data Retention 5 min interval free, for 1 min interval charges there.
Default namespace for metrics collected by CloudWatch is CWAgent.

Amazon EventBridge
- serverless service that uses events to connect application components together.
- provides way to ingest, filter, transform and deliver activities in their environment.