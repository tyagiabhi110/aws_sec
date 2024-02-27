variable "ami_value" {
  description = "Value for AMI"
}
variable "instance_type_value" {
  description = " for instance type"
}
provider "aws" {
    region = "us-east-1"
}

resource "aws_instance" "test_example" {
  ami = var.ami_value
  instance_type = var.instance_type_value
  
}