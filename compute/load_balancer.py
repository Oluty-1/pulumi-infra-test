from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws

class LoadBalancer(ComponentResource):
    def __init__(self, name, vpc_id, public_subnet_ids, security_group_id, certificate_arn, tags=None, opts=None):
        super().__init__("custom:compute:LoadBalancer", name, None, opts)

        # Create Application Load Balancer using provided security group ID
        self.alb = aws.lb.LoadBalancer(f"{name}-alb",
            internal=False,
            load_balancer_type="application",
            security_groups=[security_group_id],  # Use the single security group ID
            subnets=public_subnet_ids,
            enable_deletion_protection=True,
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        # Create Target Group
        self.target_group = aws.lb.TargetGroup(f"{name}-tg",
            port=8080,
            protocol="HTTP",
            target_type="ip",
            vpc_id=vpc_id,
            health_check={
                "enabled": True,
                "path": "/health",
                "healthy_threshold": 2,
                "unhealthy_threshold": 10,
            },
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        # Create HTTPS Listener
        self.https_listener = aws.lb.Listener(f"{name}-https",
            load_balancer_arn=self.alb.arn,
            port=443,
            protocol="HTTPS",
            ssl_policy="ELBSecurityPolicy-2016-08",
            certificate_arn=certificate_arn,
            default_actions=[{
                "type": "forward",
                "target_group_arn": self.target_group.arn,
            }],
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        self.target_group_arn = self.target_group.arn
        self.alb_dns_name = self.alb.dns_name

        self.register_outputs({
            "target_group_arn": self.target_group_arn,
            "alb_dns_name": self.alb_dns_name
        })