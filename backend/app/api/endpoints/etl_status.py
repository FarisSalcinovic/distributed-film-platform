# backend/app/api/endpoints/etl_status.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, Any
from datetime import datetime
from pymongo import MongoClient
import os
import json

# Kreirajte router
router = APIRouter()


# Funkcija za MongoDB konekciju
def get_mongo_db():
    """Kreira MongoDB konekciju"""
    MONGO_URL = os.getenv("MONGO_URL",
                          "mongodb://mongo_admin:mongo_admin_password@mongodb:27017/film_data?authSource=admin")
    client = MongoClient(MONGO_URL)
    return client["film_data"]


@router.get("/api/v1/etl/status", response_model=Dict[str, Any])
async def get_etl_status():
    """Vraća status ETL sistema"""
    try:
        db = get_mongo_db()

        # Osnovne statistike
        stats = {
            "films": db.films.count_documents({}) if "films" in db.list_collection_names() else 0,
            "places": db.places.count_documents({}) if "places" in db.list_collection_names() else 0,
            "cities": db.cities.count_documents({}) if "cities" in db.list_collection_names() else 0,
            "etl_jobs": db.etl_jobs.count_documents({}) if "etl_jobs" in db.list_collection_names() else 0,
            "film_place_correlations": db.film_place_correlations.count_documents(
                {}) if "film_place_correlations" in db.list_collection_names() else 0,
            "film_place_connections": db.film_place_connections.count_documents(
                {}) if "film_place_connections" in db.list_collection_names() else 0
        }

        # Poslednji jobovi
        last_jobs = []
        if "etl_jobs" in db.list_collection_names():
            last_jobs = list(db.etl_jobs.find().sort("started_at", -1).limit(5))

        # Proveri da li postoje podaci
        has_data = stats["films"] > 0 or stats["places"] > 0

        return {
            "status": "ok" if has_data else "no_data",
            "timestamp": datetime.now().isoformat(),
            "message": "ETL system is operational" if has_data else "No ETL data found. Run ETL pipeline first.",
            "collection_stats": stats,
            "last_jobs": [
                {
                    "job_id": job.get("job_id", ""),
                    "job_type": job.get("job_type", ""),
                    "status": job.get("status", ""),
                    "started_at": job.get("started_at", ""),
                    "completed_at": job.get("completed_at", ""),
                    "results": job.get("results", {})
                }
                for job in last_jobs
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {str(e)}")


@router.get("/api/v1/etl/correlation-stats", response_model=Dict[str, Any])
async def get_correlation_stats():
    """Vraća statistiku korelacija"""
    try:
        db = get_mongo_db()

        # Proveri da li postoje kolekcije
        collections = db.list_collection_names()

        if "film_place_correlations" not in collections or db.film_place_correlations.count_documents({}) == 0:
            return {
                "status": "no_data",
                "message": "No correlation data available yet",
                "suggested_action": "Run ETL pipeline first"
            }

        # Osnovna statistika
        total_correlations = db.film_place_correlations.count_documents({})

        # Uzmi nekoliko uzoraka
        sample_correlations = list(db.film_place_correlations.find().limit(3))

        return {
            "status": "success",
            "total_correlations": total_correlations,
            "sample_correlations": [
                {
                    "film_id": corr.get("film_id", "unknown"),
                    "film_title": corr.get("film_title", "Unknown Film"),
                    "place_city": corr.get("place_city", "Unknown City"),
                    "place_country": corr.get("place_country", "Unknown Country"),
                    "match_score": corr.get("match_score", 0.5)
                }
                for corr in sample_correlations
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/etl/visualize", response_class=HTMLResponse)
async def visualize_etl_data():
    """HTML dashboard za vizualizaciju"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ETL Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .card { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px; }
            .status-ok { color: green; }
            .status-error { color: red; }
            .stat { font-size: 24px; font-weight: bold; }
            .refresh-btn { padding: 10px 20px; background: #4CAF50; color: white; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>🎬 Film & Location ETL Dashboard</h1>

        <div class="card">
            <h2>System Status</h2>
            <div id="status">Loading...</div>
        </div>

        <div class="card">
            <h2>Data Statistics</h2>
            <div id="stats">Loading...</div>
            <canvas id="dataChart" width="400" height="200"></canvas>
        </div>

        <div class="card">
            <h2>Recent ETL Jobs</h2>
            <div id="jobs">Loading...</div>
        </div>

        <button class="refresh-btn" onclick="loadData()">Refresh Data</button>

        <script>
            async function loadData() {
                try {
                    // Load ETL status
                    const statusRes = await fetch('/api/v1/etl/status');
                    const statusData = await statusRes.json();

                    document.getElementById('status').innerHTML = `
                        <span class="status-${statusData.status === 'ok' ? 'ok' : 'error'}">
                            ${statusData.message}
                        </span>
                        <br>Last updated: ${new Date(statusData.timestamp).toLocaleString()}
                    `;

                    // Update stats
                    const stats = statusData.collection_stats;
                    document.getElementById('stats').innerHTML = `
                        <div class="stat">🎬 ${stats.films} Movies</div>
                        <div class="stat">📍 ${stats.places} Places</div>
                        <div class="stat">🔗 ${stats.film_place_correlations} Correlations</div>
                        <div class="stat">🔄 ${stats.etl_jobs} ETL Jobs</div>
                    `;

                    // Update chart
                    updateChart(stats);

                    // Update jobs
                    if (statusData.last_jobs && statusData.last_jobs.length > 0) {
                        let jobsHtml = '<ul>';
                        statusData.last_jobs.forEach(job => {
                            jobsHtml += `
                                <li>
                                    <strong>${job.job_type}</strong>: 
                                    <span style="color: ${job.status === 'completed' ? 'green' : 'orange'}">
                                        ${job.status}
                                    </span>
                                    (${new Date(job.started_at).toLocaleString()})
                                </li>
                            `;
                        });
                        jobsHtml += '</ul>';
                        document.getElementById('jobs').innerHTML = jobsHtml;
                    }

                } catch (error) {
                    document.getElementById('status').innerHTML = 
                        '<span class="status-error">Error loading data. Make sure backend is running.</span>';
                    console.error('Error:', error);
                }
            }

            function updateChart(stats) {
                const ctx = document.getElementById('dataChart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: ['Movies', 'Places', 'Correlations', 'Jobs'],
                        datasets: [{
                            label: 'Count',
                            data: [stats.films, stats.places, stats.film_place_correlations, stats.etl_jobs],
                            backgroundColor: ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56']
                        }]
                    }
                });
            }

            // Load data on page load
            loadData();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)