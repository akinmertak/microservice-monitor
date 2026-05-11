# microservice-monitor

> A microservice-based backend application demonstrating **Application Monitoring** and **CI/CD automation** in a fully containerized Docker environment.
> Built with Python (FastAPI), monitored with Nagios, and deployed via Jenkins pipelines.

---

## 🏗️ Architecture

Three independent microservices communicate over a shared Docker network, each with its own PostgreSQL database:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Service  │────▶│ Product Service  │◀────│  Order Service  │
│   port: 8001    │     │   port: 8002     │     │   port: 8003    │
│   db: usersdb   │     │  db: productsdb  │     │  db: ordersdb   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │                        │
         └──────────────────────┴────────────────────────┘
                                │
                        ┌───────▼───────┐
                        │  PostgreSQL   │
                        │  port: 5432   │
                        └───────────────┘

┌─────────────────┐     ┌─────────────────┐
│     Jenkins     │     │     Nagios      │
│   port: 8090    │     │   port: 8080    │
│  CI/CD Pipeline │     │   Monitoring    │
└─────────────────┘     └─────────────────┘
```

---

## ⚙️ Tech Stack

| Layer            | Technology          |
|------------------|---------------------|
| Language         | Python 3.11         |
| Framework        | FastAPI             |
| Database         | PostgreSQL 15       |
| ORM              | SQLAlchemy          |
| Containerization | Docker & Docker Compose |
| Monitoring       | Nagios              |
| CI/CD            | Jenkins             |

---

## 🚀 Quick Start

**Prerequisites:** Docker Desktop must be installed and running.

```bash
# Clone the repository
git clone https://github.com/mscicek/microservice-monitor.git
cd microservice-monitor

# Start all services
docker-compose up -d

# Verify containers are running
docker ps
```

> All six containers should show `Up` status within 30 seconds.

---

## 🔗 Service URLs

| Service             | URL                              | Credentials                   |
|---------------------|----------------------------------|-------------------------------|
| User Service API    | http://localhost:8001/docs       | —                             |
| Product Service API | http://localhost:8002/docs       | —                             |
| Order Service API   | http://localhost:8003/docs       | —                             |
| Nagios Dashboard    | http://localhost:8080/nagios     | `nagiosadmin` / `nagios`      |
| Jenkins             | http://localhost:8090            | set on first login            |

---

## 📡 API Overview

### User Service

| Method | Endpoint       | Description       |
|--------|----------------|-------------------|
| POST   | /users         | Create a new user |
| GET    | /users         | List all users    |
| GET    | /users/{id}    | Get user by ID    |
| DELETE | /users/{id}    | Delete a user     |
| GET    | /health        | Health check      |

### Product Service

| Method | Endpoint              | Description           |
|--------|-----------------------|-----------------------|
| POST   | /products             | Add a new product     |
| GET    | /products             | List all products     |
| GET    | /products/{id}        | Get product by ID     |
| PUT    | /products/{id}/stock  | Update stock quantity |
| GET    | /health               | Health check          |

### Order Service

| Method | Endpoint            | Description        |
|--------|---------------------|--------------------|
| POST   | /orders             | Place a new order  |
| GET    | /orders             | List all orders    |
| GET    | /orders/{id}        | Get order by ID    |
| PUT    | /orders/{id}/cancel | Cancel an order    |
| GET    | /health             | Health check       |

---

## 🧪 Testing the Flow

```bash
# 1. Create a user
curl -X POST http://localhost:8001/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Ali Yilmaz", "email": "ali@example.com"}'

# 2. Add a product
curl -X POST http://localhost:8002/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "price": 15000.0, "stock": 5}'

# 3. Place an order (triggers inter-service communication)
curl -X POST http://localhost:8003/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "product_id": 1, "quantity": 1}'
```

---

## 📊 Monitoring with Nagios

Nagios checks the `/health` endpoint of each microservice every minute.

| Status       | Meaning                          |
|--------------|----------------------------------|
| ✅ OK        | Service is running normally      |
| ⚠️ WARNING   | Service is slow or degraded      |
| 🔴 CRITICAL  | Service is down                  |

**Live demo — simulate a failure:**

```bash
docker stop user-service    # Nagios turns CRITICAL
docker start user-service   # Nagios returns to OK
```

---

## 🔄 CI/CD with Jenkins

The `Jenkinsfile` defines a **6-stage pipeline**:

```
Checkout → Lint → Test → Build → Deploy → Health Check
```

**First-time Jenkins setup:**

```bash
# Get the initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Then open http://localhost:8090, complete the setup wizard, and create a Pipeline job pointing to this repository.

---

## 🛑 Stopping the System

```bash
# Stop all containers
docker-compose down

# Stop and remove all data (full reset)
docker-compose down -v
```

---

## 📁 Project Structure

```
microservice-monitor/
├── docker-compose.yml        # Orchestration config
├── Jenkinsfile               # CI/CD pipeline definition
├── README.md
├── init-scripts/
│   └── init.sql              # Database initialization
├── user-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/main.py
├── product-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/main.py
├── order-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/main.py
└── nagios/
    └── services.cfg          # Nagios monitoring config
```