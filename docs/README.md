# Numeris Infrastructure

## Overview
This repository contains the Infrastructure as Code (IaC) implementation using Pulumi for the Numeris project. The infrastructure is designed to run containerized applications on AWS ECS with a focus on scalability, security, and maintainability.

## Architecture Components
- **Networking**: VPC, subnets, NAT Gateway, VPC Endpoints
- **Compute**: ECS Fargate, Application Load Balancer
- **Data**: RDS PostgreSQL with automated backups
- **Security**: IAM roles, Security Groups, Secrets Manager
- **Monitoring**: CloudWatch, OpenSearch, Custom Alerts

## Key Features
- Auto-scaling capabilities for ECS services
- High availability across multiple AZs
- Automated backup and recovery
- Comprehensive monitoring and alerting
- Least privilege security model

## Directory Structure



numeris/
├── compute/ # ECS and compute-related resources
├── data/ # Database and storage resources
├── monitoring/ # Monitoring and alerting configurations
├── networking/ # VPC and network configurations
├── security/ # IAM, security groups, and secrets
├── utils/ # Utility functions and helpers
├── config/ # Configuration management
└── docs/ # Project documentation

## Prerequisites
- AWS Account with appropriate permissions
- Pulumi CLI installed
- Python 3.8 or higher
- AWS CLI configured

## Quick Start
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure Pulumi: `pulumi config set aws:region us-west-1`
4. Deploy: `pulumi up`

## Documentation
- [Architecture Overview](docs/architecture/README.md)
- [Security Documentation](docs/security/SECURITY.md)
- [Deployment Guide](docs/deployment/deployment.md)
- [Cost Analysis](docs/costs/cost-breakdown.md)

## Contributing
Please read our contributing guidelines before submitting pull requests.

## License
[Specify your license]

