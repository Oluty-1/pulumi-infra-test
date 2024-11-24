from pulumi import ComponentResource, ResourceOptions
from .components.vpc import VPCStack
from .components.endpoints import VPCEndpoints

class NetworkStack(ComponentResource):
    def __init__(self, name, security_groups=None, tags=None, opts=None):
        super().__init__("custom:networking:NetworkStack", name, None, opts)

        # Create VPC and basic networking components
        self.vpc = VPCStack(name,
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        # Store name and tags for later use
        self._name = name
        self._tags = tags
        self.endpoints = None

        # Export basic values
        self.vpc_id = self.vpc.vpc_id
        self.private_subnet_ids = self.vpc.private_subnet_ids
        self.public_subnet_ids = self.vpc.public_subnet_ids

        self.register_outputs({})

    def create_endpoints(self, security_groups):
        """Create VPC Endpoints after security groups are available"""
        if security_groups and not self.endpoints:
            self.endpoints = VPCEndpoints(self._name,
                vpc_id=self.vpc_id,
                private_subnet_ids=self.private_subnet_ids,
                security_group_id=security_groups.vpc_endpoints_sg_id,
                tags=self._tags,
                opts=ResourceOptions(parent=self, depends_on=[self.vpc])
            )
