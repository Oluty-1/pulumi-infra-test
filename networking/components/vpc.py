from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws

class VPCStack(ComponentResource):
    def __init__(self, name, tags=None, opts=None):
        super().__init__("custom:networking:VPCStack", name, None, opts)

        # Create VPC
        self.vpc = aws.ec2.Vpc(f"{name}-vpc",
            cidr_block="10.0.0.0/16",
            enable_dns_hostnames=True,
            enable_dns_support=True,
            tags=tags or {},
            opts=ResourceOptions(parent=self)
        )

        # Create Internet Gateway with VPC as parent
        self.igw = aws.ec2.InternetGateway(f"{name}-igw",
            vpc_id=self.vpc.id,
            tags=tags or {},
            opts=ResourceOptions(parent=self.vpc)
        )

        # Create public subnets with VPC as parent
        self.public_subnets = []
        for i, az in enumerate(["us-west-1b", "us-west-1c"]):
            subnet = aws.ec2.Subnet(f"{name}-public-{i+1}",
                vpc_id=self.vpc.id,
                cidr_block=f"10.0.{i*32}.0/20",
                availability_zone=az,
                map_public_ip_on_launch=True,
                tags=dict(tags or {}, **{"Type": "Public"}),
                opts=ResourceOptions(parent=self.vpc)
            )
            self.public_subnets.append(subnet)

        # Create NAT Gateway and Elastic IP with first public subnet as parent
        self.eip = aws.ec2.Eip(f"{name}-nat-eip",
            domain="vpc",
            tags=tags or {},
            opts=ResourceOptions(parent=self.public_subnets[0])
        )

        self.nat_gateway = aws.ec2.NatGateway(f"{name}-nat",
            allocation_id=self.eip.id,
            subnet_id=self.public_subnets[0].id,
            tags=tags or {},
            opts=ResourceOptions(
                parent=self.public_subnets[0],
                depends_on=[self.eip]
            )
        )

        # Create private subnets with VPC as parent
        self.private_subnets = []
        for i, az in enumerate(["us-west-1b", "us-west-1c"]):
            subnet = aws.ec2.Subnet(f"{name}-private-{i+1}",
                vpc_id=self.vpc.id,
                cidr_block=f"10.0.{(i+2)*32}.0/20",
                availability_zone=az,
                tags=dict(tags or {}, **{"Type": "Private"}),
                opts=ResourceOptions(parent=self.vpc)
            )
            self.private_subnets.append(subnet)

        # Create route tables with their respective parents
        self.public_rt = aws.ec2.RouteTable(f"{name}-public-rt",
            vpc_id=self.vpc.id,
            routes=[{
                "cidr_block": "0.0.0.0/0",
                "gateway_id": self.igw.id
            }],
            tags=tags or {},
            opts=ResourceOptions(parent=self.vpc)
        )

        self.private_rt = aws.ec2.RouteTable(f"{name}-private-rt",
            vpc_id=self.vpc.id,
            routes=[{
                "cidr_block": "0.0.0.0/0",
                "nat_gateway_id": self.nat_gateway.id
            }],
            tags=tags or {},
            opts=ResourceOptions(
                parent=self.vpc,
                depends_on=[self.nat_gateway]
            )
        )

        # Create route table associations with their respective subnets as parents
        for i, subnet in enumerate(self.public_subnets):
            aws.ec2.RouteTableAssociation(f"{name}-public-rta-{i+1}",
                subnet_id=subnet.id,
                route_table_id=self.public_rt.id,
                opts=ResourceOptions(parent=subnet)
            )

        for i, subnet in enumerate(self.private_subnets):
            aws.ec2.RouteTableAssociation(f"{name}-private-rta-{i+1}",
                subnet_id=subnet.id,
                route_table_id=self.private_rt.id,
                opts=ResourceOptions(parent=subnet)
            )

        # Export values
        self.vpc_id = self.vpc.id
        self.private_subnet_ids = [subnet.id for subnet in self.private_subnets]
        self.public_subnet_ids = [subnet.id for subnet in self.public_subnets]

        self.register_outputs({})
