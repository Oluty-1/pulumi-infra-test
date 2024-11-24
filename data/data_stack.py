from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws
from .rds import RDSInstance
from .backup import BackupConfig

class DataStack(ComponentResource):
    def __init__(self, name: str, vpc_id: str, subnet_ids: list, 
                 security_group_id: str, tags: dict = None, 
                 opts: ResourceOptions = None):
        super().__init__("custom:data:DataStack", name, None, opts)

        # Create DB Parameter Group with proper parenting
        self.parameter_group = aws.rds.ParameterGroup(f"{name}-pg",
            family="postgres14",
            description="Custom parameter group for PostgreSQL 14",
            parameters=[
                {"name": "max_connections", "value": "100"},
                {"name": "shared_buffers", "value": "4096MB"}
            ],
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        # Create DB Subnet Group with proper parenting
        self.subnet_group = aws.rds.SubnetGroup(f"{name}-subnet-group",
            subnet_ids=subnet_ids,
            tags=dict(tags or {}, Name=f"{name}-subnet-group"),
            opts=ResourceOptions(parent=self)
        )

        # Create CloudWatch Metric Alarms with proper parenting
        self.rds_cpu_alarm = aws.cloudwatch.MetricAlarm(f"{name}-rds-cpu-alarm",
            comparison_operator="GreaterThanThreshold",
            evaluation_periods=2,
            metric_name="CPUUtilization",
            namespace="AWS/RDS",
            period=300,
            statistic="Average",
            threshold=80,
            alarm_description="Alert when database CPU exceeds 80%",
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        # Create RDS Instance with proper parenting
        self.rds = RDSInstance(f"{name}",
            vpc_id=vpc_id,
            subnet_group_name=self.subnet_group.name,
            parameter_group_name=self.parameter_group.name,
            security_group_id=security_group_id,
            tags=tags,
            opts=ResourceOptions(
                parent=self,
                depends_on=[self.parameter_group, self.subnet_group]
            )
        )

        # Create Backup Configuration with proper parenting
        self.backup = BackupConfig(f"{name}",
            vault_name=f"{name}-backup-vault",
            resource_id=self.rds.instance_id,
            rds_instance_arn=self.rds.instance.arn,
            tags=tags,
            opts=ResourceOptions(
                parent=self,
                depends_on=[self.rds]
            )
        )

        # Register outputs
        self.instance_id = self.rds.instance_id
        self.endpoint = self.rds.endpoint

        self.register_outputs({
            "instance_id": self.instance_id,
            "endpoint": self.endpoint,
            "parameter_group_name": self.parameter_group.name,
            "subnet_group_name": self.subnet_group.name,
            # "db_secret_arn": self.rds.secret_arn
        })