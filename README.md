# API-Gateway-Python
Python API Gateway

username = email address

## Command to run the API Gateway:
```uvicorn app.main:app --reload --port 9000```

## Pulling container image from GitHub Container Registry
```docker pull ghcr.io/voltcast-a-ase-project/api-gateway-python/api-gateway:latest```

### Important!
Before you pull the images, make sure to run the following command in your LOCAL TERMINAL:

```docker network create VoltCast_Network```

Without creating this docker network, the container won't be able to communicate to each other!

After creating the network, bind all running container to it:
```docker network connect VoltCast_Network <CONTAINER_NAME>```
