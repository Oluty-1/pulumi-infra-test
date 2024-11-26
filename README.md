# pulumi-infra-test
setting up a production ready infrastructure with application deployment on ecs using pulumi

#### PULUMI Installation:
Follow Pulumi's documentation for details on how to install pulumi depending on which OS you run here >> https://www.pulumi.com/docs/iac/download-install/

This project builds the entire infrastructure along with the dependencies needes for an application to be deployed and ran on Amazon ECS.

Which includes the Network infrastructure, the security setup and management, the database setup, and the compute infrastructure, while keepingcts minimal and right sizing resources while allowing for scalling up in moments of high traffic.

#### Here's a snippet of the infrastructure from pulumi graph view

![Screenshot from 2024-11-25 23-22-53](https://github.com/user-attachments/assets/04f102e4-03fd-43c7-aaef-65b61b2bf2fb)
This shows the heirachy and dependencies or resources in this particular infrastructure

## DEPLOYMENT GUIDE
## Steps to build this Infrastruture on your AWS account
1. Have pulumi installed on you machine
2. Configure aws credentials using the command "aws config" in your terminal, (Make sure it's an account that with administrator access)
3. Clone this repository into your machine
4. Edit the "Pulumi.dev.yaml" file to select the aws region of your choice
5. Manually create a free certificate from your aws console and replace the arn in the "Pulumi.dev.yaml" file
6. Run the command "pulumi up"

   This will display the resources in order or how they will be created, looking like this:
   ![Screenshot from 2024-11-26 02-17-35](https://github.com/user-attachments/assets/c8ad48cf-fe40-40d6-858d-ac48c2bdb909)

   It might promt you to log into pulumi, so you will have to have a pulumi account.
   ![Screenshot from 2024-11-26 02-19-26](https://github.com/user-attachments/assets/0088ebe6-d8d2-4a90-8643-ed297c3c04aa)
   It'll show the number of resources to be created in the pulumi stack, go ahead and select yes.

   it will take a while, but you can check the aws console to see the resources being created, and check ulumi side for the graph view of the infrastructure.

## Cost Analysis
   Here's an aproximate breakdown of what the coloud expense will be in a month
   

## Destroy the Infrastructure
   To destroy the infrastrcture, run the command "pulumi destroy".
   This will delete the resources and tear down the entire infrastruture.
   
