# Demonstration Application

Manual deployment in Kubernetes:

```shell
kubectl create namespace manual-test-1

kubectl apply -f awesome_webpage.yaml -n manual-test-1

# Expose the service in order to test
kubectl port-forward service/app1-service 7111:app1-service-http-port -n manual-test-1
```

In a separate terminal window, test with the following command:

```shell
curl http://localhost:7111/
```

# Cleanup

Run the following to delete the application:

```shell
kubectl delete -f awesome_webpage.yaml -n manual-test-1

kubectl delete namespace manual-test-1
```

