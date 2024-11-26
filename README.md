# pulumi-infra-test
setting up a production ready infrastructure with application deployment on ecs using pulumi

#### PULUMI Installation:
Follow Pulumi's documentation for details on how to install pulumi depending on which OS you run here >> https://www.pulumi.com/docs/iac/download-install/

This project builds the entire infrastructure along with the dependencies needes for an application to be deployed and ran on Amazon ECS.

Which includes the Network infrastructure, the security setup and management, the database setup, and the compute infrastructure, while keepingcts minimal and right sizing resources while allowing for scalling up in moments of high traffic.

#### Here's a snippet of the infrastructure from pulumi graph view

![Screenshot from 2024-11-25 23-22-53](https://github.com/user-attachments/assets/04f102e4-03fd-43c7-aaef-65b61b2bf2fb)
This shows the heiravchy and dependencies or resources in this particular infrastructure
