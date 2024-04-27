# Create a VPC
resource "aws_vpc" "terraform-vpc" {
    cidr_block = var.vpc_cidr
    instance_tenancy = "default"
    tags={
        Name = var.vpc_name
    }
}

#Create first public subnet in vpc

resource "aws_subnet" "pub-sub1" {
    vpc_id= aws_vpc.terraform-vpc.id
    cidr_block = var.pub_sub1_cidr
    availability_zone = var.availability_zone-1
    map_public_ip_on_launch = true
    tags={
        Name = var.pub-sub1-name
    }
}

# Create second public subnet in vpc

resource "aws_subnet" "pub-sub2" {
    vpc_id = aws_vpc.terraform-vpc.id
    cidr_block = var.pub_sub2_cidr
    availability_zone = var.availability_zone-2
    map_public_ip_on_launch= true
    tags= {
        Name = var.pub-sub2-name
    }
}

# Create first private subnet in vpc

resource "aws_subnet" "priv-sub1" {
    vpc_id = aws_vpc.terraform-vpc.id
    cidr_block = var.priv_sub1_cidr
    availability_zone = var.availability_zone-1
    map_public_ip_on_launch = true
    tags = {
        Name = var.priv-sub1-name
    }
}

# Create second private subnet

resource "aws_subnet" "priv-sub2" {
    vpc_id = aws_vpc.terraform-vpc.id
    cidr_block = var.priv_sub2_cidr
    availability_zone = var.availability_zone-2
    map_public_ip_on_launch= true
    tags= {
        Name= var.priv-sub2-name
    }
}

#Create Internet gateway and associate it with VPC
resource "aws_internet_gateway" "terraform-igw" {
    vpc_id = aws_vpc.terraform-vpc.id
    tags= {
        Name = var.igw-name
    }
}

# Create Elastip IP
resource "aws_eip" "ngw-eip" {
    vpc=true
}

# Create a nat gateway and associate with EIP and a public subnet
resource "aws_nat_gateway" "terraform-ngw" {
    allocation_id = aws_eip.ngw-eip.id
    subnet_id = aws_subnet.pub-sub1.id
    tags = {
        Name = var.nat-gw-name
    }
    depends_on = [aws_internet_gateway.terraform-igw]
}