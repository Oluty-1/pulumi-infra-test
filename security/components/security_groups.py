from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws

class SecurityGroups(ComponentResource):
    def __init__(self, name, vpc_id, tags=None, opts=None):
        super().__init__("custom:security:SecurityGroups", name, None, opts)

        # Create security groups with proper parenting
        self.vpc_endpoints_sg = aws.ec2.SecurityGroup(f"{name}-vpc-endpoints-sg",
            vpc_id=vpc_id,
            description="Security group for VPC endpoints",
            ingress=[
                aws.ec2.SecurityGroupIngressArgs(
                    from_port=443,
                    to_port=443,
                    protocol="tcp",
                    cidr_blocks=["10.0.0.0/16"]
                )
            ],
            tags=dict(tags or {}, **{"Name": f"{name}-vpc-endpoints-sg"}),
            opts=ResourceOptions(parent=self)
        )

        self.ecs_tasks_sg = aws.ec2.SecurityGroup(f"{name}-ecs-tasks-sg",
            vpc_id=vpc_id,
            description="Security group for ECS tasks",
            ingress=[
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp",
                    from_port=8080,
                    to_port=8080,
                    cidr_blocks=["10.0.0.0/16"]
                )
            ],
            tags=dict(tags or {}, **{"Name": f"{name}-ecs-tasks-sg"}),
            opts=ResourceOptions(parent=self)
        )

        self.alb_sg = aws.ec2.SecurityGroup(f"{name}-alb-sg",
            vpc_id=vpc_id,
            description="Security group for Application Load Balancer",
            ingress=[
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp",
                    from_port=80,
                    to_port=80,
                    cidr_blocks=["0.0.0.0/0"]
                ),
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp",
                    from_port=443,
                    to_port=443,
                    cidr_blocks=["0.0.0.0/0"]
                )
            ],
            egress=[
                aws.ec2.SecurityGroupEgressArgs(
                    protocol="-1",
                    from_port=0,
                    to_port=0,
                    cidr_blocks=["0.0.0.0/0"]
                )
            ],
            tags=dict(tags or {}, **{"Name": f"{name}-alb-sg"}),
            opts=ResourceOptions(parent=self)
        )

        # Updated RDS security group with more flexible access
        self.rds_sg = aws.ec2.SecurityGroup(f"{name}-db-sg",
            vpc_id=vpc_id,
            description="Security group for RDS instance",
            ingress=[
                # Allow access from ECS tasks
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp",
                    from_port=5432,
                    to_port=5432,
                    security_groups=[self.ecs_tasks_sg.id]
                ),
                # Allow access from within VPC
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp",
                    from_port=5432,
                    to_port=5432,
                    cidr_blocks=["10.0.0.0/16"]
                )
            ],
            tags=dict(tags or {}, **{"Name": f"{name}-db-sg"}),
            opts=ResourceOptions(parent=self)
        )

        # Export security group IDs
        self.vpc_endpoints_sg_id = self.vpc_endpoints_sg.id
        self.ecs_tasks_sg_id = self.ecs_tasks_sg.id
        self.alb_sg_id = self.alb_sg.id
        self.rds_sg_id = self.rds_sg.id

        self.register_outputs({})
