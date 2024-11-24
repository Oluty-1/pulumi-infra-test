from pulumi import Config

def get_config():
    """Get environment-specific configuration"""
    config = Config()
    
    return {
        "environment": config.get("environment") or "dev2",
        "vpc_cidr": config.get("vpc_cidr") or "10.0.0.0/16",
        "region": config.get("region") or "us-west-2",
        "availability_zones": config.get_object("availability_zones") or ["us-west-2a", "us-west-2b"],
        "rds_instance_class": config.get("rds_instance_class") or "db.t3.medium",
        "rds_allocated_storage": config.get_int("rds_allocated_storage") or 20,
        "ecs_desired_count": config.get_int("ecs_desired_count") or 2,
        "certificate_arn": config.get("certificate_arn") or "arn:aws:acm:us-west-2:123456789012:certificate/example",
        "domain_name": config.get("domain_name") or "example.com"
    }