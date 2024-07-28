# k8s-elected-api
sample service election implementation for k8s 

## Building the sample demo 
### Please Note:
As a prerequisite [docker](https://docs.docker.com/engine/install/ubuntu/) must be installed.

### Start kind k8s + Registry

~~~
bash ./kind_registry.sh
~~~

### Build Docker image and push to registry

~~~
python3 ./builder
~~~

Please see following [article](https://medium.com/p/3b5ef263df97) - for more details.