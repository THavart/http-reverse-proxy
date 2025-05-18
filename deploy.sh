#!/bin/bash
eval $(minikube docker-env) && \
docker build -t proxy-server:latest . && \
kubectl apply -f proxy-deployment.yaml && \
kubectl rollout restart deployment proxy-server
minikube service proxy-server-service
