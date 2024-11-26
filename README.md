# pulumi-infra-test
setting up a production ready infrastructure with application deployment on ecs using pulumi

PULUMI Installation:
follow Pulumi's documentation for details on how to install pulumi depending on which OS you run here >> https://www.pulumi.com/docs/iac/download-install/

Here's the file structure for this project and what to expect

numeris/
├── docs/
│   ├── architecture/
│   │   ├── diagrams/
│   │   │   ├── infrastructure-overview.png
│   │   │   ├── network-layout.png
│   │   │   └── security-groups.png
│   │   └── README.md       # Architecture overview
│   ├── security/
│   │   ├── iam-policies/Secretsmanagement/ security group
│   │   │   
│   │   └── SECURITY.md     # Security overview & best practices
│   ├── deployment/
│   │   ├── prerequisites.md
│   │   ├── configuration.md
│   │   └── deployment.md   # Step-by-step deployment guide
│   └── costs/
│       ├── cost-breakdown.md
│       └── optimization.md  # Cost optimization strategies
└── README.md               # Project overview
