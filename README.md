# SpendWise: Containerized Expense Tracker

A small web application for tracking personal expenses, built to demonstrate a cloud-style deployment with Docker.
Users can add and delete expenses, choose a category and a date, and see the total spending for the current month.

## Architecture

```
Browser -> port 8000 -> [Nginx] -> web-1 (Flask) \
                                -> web-2 (Flask)  -> [PostgreSQL] -> Docker volume
                                -> web-3 (Flask) /
```

| Service | Technology | Role |
|---|---|---|
| `nginx` | Nginx | Load balancer, the only service open to the outside (port 8000) |
| `web` (3 replicas) | Python, Flask | Web application |
| `db` | PostgreSQL 16 | Stores the expenses |
| `db_data` | Docker volume | Keeps the data when containers restart |

## Cloud features

- **Containers:** each part of the system runs in its own container.
- **Scalability:** the web service runs as 3 identical replicas; Nginx distributes requests between them.
- **Availability:** health checks for the database and for every web replica; `restart: unless-stopped` restarts failed containers automatically.
- **Startup order:** web containers start only after the database is healthy (`depends_on` with `service_healthy`).
- **Networking:** Compose creates an internal network; the web app reaches the database by the name `db`. Only Nginx is published to the host.
- **Storage:** database files live in a named Docker volume, so data survives container restarts.
- **Configuration as code:** the whole system is described in `compose.yaml` and started with one command.

## Project structure

```
spendwise/
├── compose.yaml        # all services, network and volume
├── app/
│   ├── app.py          # Flask application
│   ├── Dockerfile      # image for the web service
│   └── requirements.txt
├── db/
│   └── init.sql        # creates the expenses table on first start
└── nginx/
    └── nginx.conf      # reverse proxy / load balancer settings
```

## How to run

Requirements: Docker Desktop (with Docker Compose).

```
git clone https://github.com/Anujin16/spendwise-cloud-project.git
cd spendwise-cloud-project
docker compose up -d --build
```

Open http://localhost:8000

Useful commands:

```
docker compose ps                 # list containers and their health
docker compose logs web --tail 20 # latest logs of the web service
docker compose down               # stop and remove containers (data is kept)
```

## Demonstration

1. **Scaling:** `for i in 1 2 3 4 5 6; do curl -s localhost:8000/whoami; echo; done` prints three different container names, so requests are shared between replicas.
2. **Failure:** `docker kill spendwise-web-1` stops one replica; the site stays available because Nginx uses the other two.
3. **Recovery:** after a few seconds Docker restarts the killed container (`docker compose ps`).
4. **Persistence:** add an expense, run `docker compose restart`, reload the page; the data is still there.

## Endpoints

| Path | Description |
|---|---|
| `/` | Expense list, form and monthly total |
| `/add` | Adds an expense (POST) |
| `/delete/<id>` | Deletes an expense (POST) |
| `/whoami` | Name of the container that answered |
| `/health` | Health check used by Docker |

## Author

Anujin16