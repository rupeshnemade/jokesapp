# Chuck Norris Jokes 

This app simply pulls a random Joke from the Chuck Norris API (<https://api.chucknorris.io/jokes/random>), and then saves it to the mongo db instance.. 

The UI forwards requests to Nginx proxy which allows you to retrieve information from the MongoDB instance via Flask web server. 

## Infrastructure

![My Image][infra-diagram.png]

### Flask

The Python Flask app reads and write in a mongo database at : 

```r
app.config["MONGO_URI"] = "mongodb://mongo:27017/dev"
mongo = PyMongo(app)
db = mongo.db
```

## Local Docker Deployment

### Build 

```
git clone https://github.com/rupeshnemade/jokesapp && docker build -t chuck-norris-jokes:0.1 .
# OR 
docker pull nemadern/chuck-norris-jokes:0.1
docker pull mongo 
```

### Launch 

```
docker network create jokesapp-net

docker run --name=mongo --rm -d --network=jokesapp-net mongo

docker run --name=jokesapp --rm -p 5000:5000 -d --network=jokesapp-net chuck-norris-jokes:0.1

On local browser run localhost:5000/add_joke to add new joke & localhost:5000/get_joke to read jokes
```


### Stop 

```
docker stop mongo && docker rm mongo
docker stop jokesapp && docker rm jokesapp
docker network rm jokesapp-net
```

## Deploy on Kuberenets

### Create Cluster with kubeadm or AWS EKS

I have used AWS EKS to deploy the setup. 


```
cd deploy/
kubectl apply -f kuberenets/.
kubectl get all -n jokes
```

+ This will create following resources:-

        1. Deployment: Jokes web server
        2. Deployment: Mongodb 
        3. Deployment: Nginx ingress
        4. Service
        5. PersistantVolume & PersistantVolumeClaim for MongoDB data storage
        6. Network Policies to manage traffic rules
        
+ To test the setup run Curl pod & exec it it as below. Curl on nginx service endpoint to add & get jokes.

```
kubectl run mycurlpod --image=curlimages/curl -i --tty -- sh
curl nginx-proxy.jokes.svc.cluster.local:80/add_joke
curl nginx-proxy.jokes.svc.cluster.local:80/get_joke
```

## Things to consider before deploying on Production Kubernetes cluster

####Zero downtime

Add PodDisruptionBudget for deployments in order to make sure our application is always up & running even when there is mantainance like node rotation.

Also add HorizontalPodAutoscaler to handle surge in traffic for the application.

#### Rolling update
As we have each component running as a kubernetes deployments it will give us flexibility of rolling update. 

Configure rolling update by adding below in current deployment.
Currently I have set replica count as 1 and we should increase it for rolling update.

```
type: RollingUpdate
 rollingUpdate:
  maxSurge: 3
  maxUnavailable: 1
  timeoutSeconds: 100
  intervalSeconds: 5
  updatePeriodSeconds: 5
```
        
####Logging & Monitoring

1. For Nginx, I have enabled Prometheus scraping with 'nginx-prometheus-exporter', so that prometheus can scrape Nginx metrics & we can use them for monitoring incoming traffic or connections drop.
2. For each deployment we should monitor below basic metrics at minimum for general application health-
    - Pod count (Pod desired vs current replica)
    - CPU Utilisation
    - Memory utilisation
    - OOM restart count
3. To enable logging we should only scrape Errors from logs to keep minimum load on logging infrastructure (Fluentbit & fluentd) and also to avoid uneccessary logs volume ingestion cost. Other log level Warning or INFO should be enable while troubleshooting.
4. Alerting can be added for logs pattern like error logs or any know logs regex pattern.
5. Pod events & audit trail can be logged to understand manual intervention or any other pod lifecycle issues. 


#### Security

1. Currently I am using DockerHub images but for better security push docker images in private ECR or DockerHub registry & create Kuberenetes ServiceAccounts with pull credentials linked so that all resources for the linked SA will pull only signed & secured images.
2. Network policies are setup to allow only required communication from restricted pod & restricted port. This is require as on Production cluster there might be by default Deny all network policies which can impact our setup communication.
3. I have added resource request & limit to restrict overutilisation. 