
"""Main Pulumi program with improved organization"""
import pulumi
from networking.network_stack import NetworkStack
from security.security_stack import SecurityStack
from data.data_stack import DataStack
from compute.compute_stack import ComputeStack
from monitoring.monitoring_stack import MonitoringStack
from config.settings import get_config
from naming.tags import get_resource_tags

# Get configuration
config = get_config()
tags = get_resource_tags("main", config["environment"], "infrastructure")

# Create network stack
network = NetworkStack("main",
    tags=tags,
    opts=pulumi.ResourceOptions()
)

# Create security stack
security = SecurityStack("main",
    vpc_id=network.vpc_id,
    tags=tags,
    opts=pulumi.ResourceOptions(depends_on=[network])
)

# Update network with security groups
network.create_endpoints(security.security_groups)

# Create data stack
data = DataStack("main",
    vpc_id=network.vpc_id,
    subnet_ids=network.private_subnet_ids,
    security_group_id=security.rds_sg_id,
    tags=tags,
    opts=pulumi.ResourceOptions(depends_on=[security])
)

# Create compute stack
compute = ComputeStack("main",
    vpc_id=network.vpc_id,
    private_subnet_ids=network.private_subnet_ids,
    public_subnet_ids=network.public_subnet_ids,
    security_groups=security.security_groups,
    iam_roles=security.iam_roles,
    certificate_arn=config["certificate_arn"],
    tags=tags,
    opts=pulumi.ResourceOptions(depends_on=[security])
)

# Create monitoring stack
monitoring = MonitoringStack("main",
    vpc_id=network.vpc_id,
    subnet_ids=network.private_subnet_ids,
    security_group_id=security.ecs_tasks_sg_id,
    cluster_name=compute.cluster_name,
    rds_instance_id=data.instance_id,
    tags=tags,
    opts=pulumi.ResourceOptions(depends_on=[compute, data])
)

# Export important values
pulumi.export("vpc_id", network.vpc_id)
pulumi.export("ecs_cluster_name", compute.cluster_name)
pulumi.export("rds_endpoint", data.endpoint)
# pulumi.export("rds_secret_arn", data.rds.secret_arn)  
pulumi.export("load_balancer_dns", compute.alb_dns_name)