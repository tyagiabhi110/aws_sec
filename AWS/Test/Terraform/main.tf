variable "public_subnet_cidrs" {
    type = lsit(string)
    description = "public Subnet CIDR values"
    default = ["10.0.1.0/24", "10.0.2.0/24"]
  
}
variable "azs" {
    type = list(string)
    description = "Availability Zones"
    default = ["eu-central-1a", "eu-central-1b"]
}
variable "private_subnet_cidrs"{
    type = list(string)
    description = "Private Subnet CIDR"
    default = [ "10.0.4.0/24", "10.0.5.0/24" ]
}
provider "aws" {
    region = us-east-1
  
}

resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"
    tags = {
      Name = "Project VPC"
    }
}

resource "aws_subnet" "public_subnets" {
    count = length(var.public_subnet_cidrs)
    vpc_id = aws_vpc.main.id
    cidr_block = element(var.public_subnet_cidrs, count.index)
    availability_zone = element(var.azs, count.index)
    tags = {
      Name = "Public Subnet ${count.index + 1}"
    }
  
}

resource "aws_subnet" "private_subnets" {
    count = length(var.private_subnet_cidrs)
    vpc_id = aws_vpc.main
    cidr_block = element(var.private_subnet_cidrs, counter.index)
    availability_zone = element(var.azs, count.index)
    tags = {
        Name = "private Subnet ${count.index + 1}"
    }
  
}

resource "aws_internet_gateway" "gw" {
    vpc_id = aws_vpc.main.id
    tags = {
        name = "Project VPC IG"
    }
}

resource "aws_route_table" "second_rt" {
    vpc_id = aws_vpc.main.id
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.gw.id

    }
    tags = {
        Name = "2nd Route Table"
    }
}
resource "aws_route_table_association" "public_subnet_association" {
    count = length(var.public_subnet_cidrs)
    subnet_id = element(aws_subnet.public_subnets[*].id, count.index)
    route_table_id = aws_route_table.second_rt.id
}
