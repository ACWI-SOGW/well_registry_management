#!/bin/bash
# Starts the Monitoring Locations Registry ci docker database container and waits for postgres database to be up.
# Any existing container is first removed.

ci_container_name="registry_postgres"
db_ready_text="PostgreSQL init process complete; ready for start up.*database system is ready to accept connections"

container_id=$(docker ps -a | grep $ci_container_name | awk '{print $1;}')
if [ -n "$container_id" ]; then
   echo "Removing existing ci db container"
   docker rm -f "$container_id"
fi

# start the docker database container
echo "Starting docker ci database container..."
docker run --name $ci_container_name -d -p 5432:5432 usgswma/well-registry-db:ci
status=$?
if [ $status -ne  0 ]; then
  echo "Error starting docker ci db container, status is $status"
  exit 1
fi

echo "docker container started."
retries=30
timer=3
db_started=0

sleep $timer
until [ $retries -eq 0 ]; do
  echo "Waiting for postgres server, $((retries--)) remaining attempts..."
  (docker logs $ci_container_name) 2>&1 | paste -s | grep -q "$db_ready_text"
  status=$?
  if [ $status -eq 0 ]; then
    retries=0
    db_started=1
  else
    sleep $timer
  fi
done

if [ $db_started -eq 0 ]; then
  status=2
  echo "postgres server failed to start"
  echo "postgres log:"
  docker logs $ci_container_name 
else
  status=0
  echo "Postgres server started."
fi

exit $status
