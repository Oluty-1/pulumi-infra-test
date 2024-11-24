from pulumi import ComponentResource
import pulumi_aws as aws

class AlertingConfig(ComponentResource):
    def __init__(self, name, cluster_name, service_name, db_instance_id, opts=None):
        super().__init__("custom:monitoring:AlertingConfig", name, None, opts)

        # Create SNS Topic for alerts
        self.alert_topic = aws.sns.Topic(f"{name}-alerts",
            name=f"{name}-infrastructure-alerts"
        )

        # ECS Service CPU Alert
        self.ecs_cpu_alarm = aws.cloudwatch.MetricAlarm(f"{name}-ecs-cpu",
            comparison_operator="GreaterThanThreshold",
            evaluation_periods=2,
            metric_name="CPUUtilization",
            namespace="AWS/ECS",
            period=300,
            statistic="Average",
            threshold=85.0,
            alarm_description="ECS CPU utilization is too high",
            alarm_actions=[self.alert_topic.arn],
            dimensions={
                "ClusterName": cluster_name,
                "ServiceName": service_name
            }
        )

        # RDS CPU Alert
        self.rds_cpu_alarm = aws.cloudwatch.MetricAlarm(f"{name}-rds-cpu",
            comparison_operator="GreaterThanThreshold",
            evaluation_periods=2,
            metric_name="CPUUtilization",
            namespace="AWS/RDS",
            period=300,
            statistic="Average",
            threshold=80.0,
            alarm_description="RDS CPU utilization is too high",
            alarm_actions=[self.alert_topic.arn],
            dimensions={
                "DBInstanceIdentifier": db_instance_id
            }
        )

        # RDS Storage Alert
        self.rds_storage_alarm = aws.cloudwatch.MetricAlarm(f"{name}-rds-storage",
            comparison_operator="LessThanThreshold",
            evaluation_periods=1,
            metric_name="FreeStorageSpace",
            namespace="AWS/RDS",
            period=300,
            statistic="Average",
            threshold=20_000_000_000,  # 20GB
            alarm_description="RDS free storage space is low",
            alarm_actions=[self.alert_topic.arn],
            dimensions={
                "DBInstanceIdentifier": db_instance_id
            }
        )

        self.register_outputs({})
