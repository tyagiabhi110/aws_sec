provider "aws" {
    region = "eu-west-1"
}
module "ec2_instance"{
    source = "./modules/ec2_instance"
    ami_value = "ami-02934ed"
    instance_type_value="t2.micro"
    subnet_value="subnet-afsdcsfdsdf"
}
