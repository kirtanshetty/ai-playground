# Common Infrastructure

This folder contains shared AWS infrastructure resources, including the RDS database.

## RDS Database Stack

The RDS stack creates a PostgreSQL database with minimal configuration:
- **Engine**: PostgreSQL 15.4
- **Instance**: db.t3.micro (minimal cost)
- **Storage**: 20GB (auto-scales up to 100GB)
- **Network**: Default VPC with public subnets (for minimal config)
- **Security**: Credentials stored in AWS Secrets Manager
- **Backup**: Deletion protection disabled (for development)

## Deployment

1. Initialize and deploy:
```bash
make deploy
```

Or manually:
```bash
# Install dependencies
pip install -r requirements.txt

# Generate Terraform provider bindings
cdktf get

# Deploy the stack
cdktf deploy --auto-approve
```

2. Destroy the stack:
```bash
make destroy
```

Or manually:
```bash
cdktf destroy --auto-approve
```

## Stack Outputs

The stack outputs the following values (accessible via `cdktf output`):
- `database_endpoint`: Database endpoint hostname
- `database_port`: Database port (5432)
- `database_name`: Database name (appdb)
- `database_secret_arn`: ARN of the secret containing credentials
- `rds_security_group_id`: Security group ID for database access

## Production Considerations

For production deployments, consider:
- Using private subnets for RDS
- Placing Lambda functions in VPC for secure access
- Enabling deletion protection
- Enabling multi-AZ deployment
- Restricting security group rules to specific sources
- Enabling automated backups
- Using larger instance sizes based on workload

