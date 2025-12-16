# distributed-film-platform -> "CineCity"
**CineCity** is a **Web based platform** where users can view popular movies & genres based on location that is selected through a **map**. By combining data from two combined public APIs, the system provides users with an **interactive world map showcasing regional film popularity**.

This repository contains the **frontend application**, which interacts with a **Python-based backend** and a **distributed database setup**.

## Project Objectives
- Integrate at least 2 public APIs (TMDb + Geoapify)
- Provide a REST API
- Offer a functioning Web App
- Include an Admin Dashboard
- Perform Cross-Source Analysis

## System Overview
The platform is made up of the following components:
-	Frontend: React + TailwindCSS
- Backend: Python, REST API
-	Databases: MongoDB and PostgreSQL
-	External APIs: TMDb, Geoapify
-	Containerization: Docker, Docker Compose
-	Deployment: Cloud-based deployment using containerized service

## Key Features
- **World Film Popularity Map:** Interactive map showing top movies and genres per country.
- **Analytics Dashboard:** Aggregated insights and statistics based on collected data.
- **User Authentication:** Login and Signup with Role-based access (user / admin).
- **Admin Dashboard:** Triggering ETL processes and viewing raw data and usage statistics.

## Authentication & Roles
Authentication is handled using JWT tokens. 
This ensures only admin users can access app's core features.
- **User:** Access map, analytics, profile
- **Admin:** Access admin dashboard and system management tools

## Deployment & Running the Project
The backend services are deployed using **Docker Compose**, while the frontend runs using the **React development server**.
### Steps:

**Build and start backend services:**
```bash
docker compose up --build
```
This starts:
- BackendAPI
- Data Ingestion Service Layer (DISL)
- MongoDB
- PostgreSQL

**Start frontend:**
```bash
cd frontend
npm install
npm start
```
