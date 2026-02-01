# Invalid Terraform - Syntax Error Test (TC-007)

resource "aws_s3_bucket" "broken" {
  bucket = "broken-bucket"
  tags = {
    Name = "Broken"
  # Missing closing brace - intentional error

resource "aws_instance" "broken" {
  ami = "ami-12345"
  invalid_attribute = true  # Invalid attribute
}
