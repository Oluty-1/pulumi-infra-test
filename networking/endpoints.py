from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws


class VPCEndpoints(ComponentResource):
    def __init__(self, name, vpc_id, private_subnet_ids, security_group_id, tags=None, opts=None):
        super().__init__("custom:networking:VPCEndpoints", name, None, opts)

        # Create a single Interface endpoint for all AWS services
        self.vpc_endpoint = aws.ec2.VpcEndpoint(f"{name}-aws-endpoint",
            vpc_id=vpc_id,
            service_name=f"com.amazonaws.{aws.get_region().name}.execute-api",  # Main endpoint for AWS services
            vpc_endpoint_type="Interface",
            subnet_ids=private_subnet_ids,
            security_group_ids=[security_group_id],
            private_dns_enabled=True,
            tags=dict(tags or {}, **{"Name": f"{name}-aws-endpoint"}),
            opts=ResourceOptions(parent=self)
        )

        # Create S3 Gateway endpoint (this is free and recommended)
        self.s3_endpoint = aws.ec2.VpcEndpoint(f"{name}-s3-endpoint",
            vpc_id=vpc_id,
            service_name=f"com.amazonaws.{aws.get_region().name}.s3",
            vpc_endpoint_type="Gateway",
            tags=dict(tags or {}, **{"Name": f"{name}-s3-endpoint"}),
            opts=ResourceOptions(parent=self)
        )

        self.register_outputs({})