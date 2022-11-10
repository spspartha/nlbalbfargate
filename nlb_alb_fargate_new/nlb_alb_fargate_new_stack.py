from aws_cdk import (
    # Duration,
    Stack,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as targets,
    aws_ecs as ecs,
    aws_ecs_patterns as patterns,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    CfnOutput,
    # aws_sqs as sqs,
)
from constructs import Construct

class NlbAlbFargateNewStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        vpc = ec2.Vpc(self, "MyVpc", max_azs=3)     # default is all AZs in region

        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        task = ecs.FargateTaskDefinition(self, "FargateTask", cpu=256, memory_limit_mib=512)
        task.add_container("nginx",
                image=ecs.ContainerImage.from_registry("public.ecr.aws/nginx/nginx:latest"),
                port_mappings=[ecs.PortMapping(container_port=80)]
        )

        svc = patterns.ApplicationLoadBalancedFargateService(self, "Service",
                vpc=vpc,
                task_definition=task,
                public_load_balancer=False
        )
        nlb = elbv2.NetworkLoadBalancer(self, "Nlb",
                vpc=vpc,
                cross_zone_enabled=True,
                internet_facing=True
        )

        listener = nlb.add_listener("listener", port=80)
        listener.add_targets("Targets",
                targets=[targets.AlbTarget(svc.load_balancer, 80)],
                port=80
        )

        CfnOutput(self, "NlbEndpoint", value=f"http://{nlb.load_balancer_dns_name}")
