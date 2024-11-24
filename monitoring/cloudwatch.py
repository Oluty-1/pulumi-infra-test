from pulumi import ComponentResource, Output
import pulumi_aws as aws
import json

class CloudWatchConfig(ComponentResource):
    def __init__(self, name, cluster_name, rds_instance_id, opts=None):
        super().__init__("custom:monitoring:CloudWatchConfig", name, None, opts)

        # Create Log Group for ECS tasks
        self.log_group = aws.cloudwatch.LogGroup(f"{name}-ecs-logs",
            name=f"/ecs/{name}",
            retention_in_days=30,
            tags={"Name": f"{name}-ecs-logs"}
        )

        # Create CloudWatch Alarms
        self.ecs_cpu_alarm = aws.cloudwatch.MetricAlarm(f"{name}-ecs-cpu-alarm",
            name=f"{name}-ecs-cpu-high",
            comparison_operator="GreaterThanThreshold",
            evaluation_periods=2,
            metric_name="CPUUtilization",
            namespace="AWS/ECS",
            period=300,
            statistic="Average",
            threshold=80.0,
            alarm_description="ECS CPU utilization is too high",
            dimensions={
                "ClusterName": cluster_name
            }
        )

        self.rds_cpu_alarm = aws.cloudwatch.MetricAlarm(f"{name}-rds-cpu-alarm",
            name=f"{name}-rds-cpu-high",
            comparison_operator="GreaterThanThreshold",
            evaluation_periods=2,
            metric_name="CPUUtilization",
            namespace="AWS/RDS",
            period=300,
            statistic="Average",
            threshold=80.0,
            alarm_description="RDS CPU utilization is too high",
            dimensions={
                "DBInstanceIdentifier": rds_instance_id
            }
        )

        # Create Metric Filters for Application Logs
        self.error_metric_filter = aws.cloudwatch.LogMetricFilter(f"{name}-error-filter",
            log_group_name=self.log_group.name,
            metric_transformation={
                "name": f"{name}_error_count",
                "namespace": "CustomMetrics",
                "value": "1"
            },
            pattern="[timestamp, level=ERROR, message]"
        )

        # Create Alarm for Error Logs
        self.error_alarm = aws.cloudwatch.MetricAlarm(f"{name}-error-alarm",
            name=f"{name}-high-error-count",
            comparison_operator="GreaterThanThreshold",
            evaluation_periods=1,
            metric_name=f"{name}_error_count",
            namespace="CustomMetrics",
            period=300,
            statistic="Sum",
            threshold=10.0,
            alarm_description="High number of application errors detected"
        )

        # Create Dashboard using Output.all() to handle Pulumi outputs
        Output.all(cluster_name, rds_instance_id).apply(
            lambda args: self.create_dashboard(name, args[0], args[1])
        )

        self.log_group_name = self.log_group.name
        
        self.register_outputs({})

    def create_dashboard(self, name, cluster_name, rds_instance_id):
        dashboard_config = {
            "widgets": [
                {
                    "type": "metric",
                    "x": 0,
                    "y": 0,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AWS/ECS", "CPUUtilization", "ClusterName", cluster_name],
                            [".", "MemoryUtilization", ".", "."]
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": "us-west-1",
                        "title": "ECS Cluster CPU and Memory Utilization"
                    }
                },
                {
                    "type": "metric",
                    "x": 12,
                    "y": 0,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", rds_instance_id],
                            [".", "FreeStorageSpace", ".", "."],
                            [".", "DatabaseConnections", ".", "."]
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": "us-west-1",
                        "title": "RDS Metrics"
                    }
                }
            ]
        }

        # Create the dashboard with the resolved values
        self.dashboard = aws.cloudwatch.Dashboard(f"{name}-dashboard",
            dashboard_name=f"{name}-monitoring-dashboard",
            dashboard_body=json.dumps(dashboard_config)
        )
        
        return self.dashboard