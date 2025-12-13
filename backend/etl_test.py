# test_etl_integration.py
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_etl_status():
    """Testira ETL status endpoint"""
    print("🔍 Testing ETL status...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/etl/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ ETL Status API is working")
            print(f"📊 Movies in DB: {data['collection_stats']['films']}")
            print(f"📊 Places in DB: {data['collection_stats']['places']}")
            print(f"📊 ETL Jobs: {data['collection_stats']['etl_jobs']}")
            print(f"📊 Success Rate: {data['job_summary']['success_rate']}")
            return True
        else:
            print(f"❌ Failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_correlation_stats():
    """Testira correlation stats endpoint"""
    print("\n🔗 Testing correlation stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/etl/correlation-stats")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Status: {data['status']}")
            if data['status'] == 'success':
                print(f"📊 Total correlations: {data['total_correlations']}")
                print(f"📊 Average per film: {data['avg_correlations_per_film']}")
                if data['sample_correlations']:
                    print("🎭 Sample correlations:")
                    for corr in data['sample_correlations'][:3]:
                        print(f"  • {corr['film_title']} -> {corr['place_city']} ({corr['match_score']:.2f})")
            return True
        else:
            print(f"❌ Failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def check_visualization():
    """Provjerava da li je vizualizacija dostupna"""
    print("\n📊 Testing visualization dashboard...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/etl/visualize")
        if response.status_code == 200:
            print("✅ Visualization dashboard is available")
            print(f"📋 Access it at: {BASE_URL}/api/v1/etl/visualize")
            return True
        else:
            print(f"❌ Failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_manual_etl():
    """Ručno pokreće ETL pipeline"""
    print("\n🚀 Running manual ETL pipeline...")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/etl/run-combined")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ETL pipeline started: {data['task_id']}")
            print(f"📋 Message: {data['message']}")
            return data['task_id']
        else:
            print(f"❌ Failed with status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Glavna test funkcija"""
    print("=" * 60)
    print("🎬 FILM & LOCATION ETL INTEGRATION TEST")
    print("=" * 60)

    # Test 1: Basic API status
    if not test_etl_status():
        print("\n❌ Please make sure the backend is running!")
        print("   Run: docker-compose up -d")
        return

    # Test 2: Correlation stats
    test_correlation_stats()

    # Test 3: Visualization
    check_visualization()

    # Test 4: Ask about running ETL
    print("\n" + "=" * 60)
    choice = input("🚀 Do you want to run the ETL pipeline now? (y/n): ")

    if choice.lower() == 'y':
        task_id = run_manual_etl()
        if task_id:
            print(f"\n⏳ Waiting 10 seconds to check results...")
            time.sleep(10)
            test_etl_status()
            test_correlation_stats()

    print("\n" + "=" * 60)
    print("✅ Integration test completed!")
    print(f"📊 Dashboard URL: {BASE_URL}/api/v1/etl/visualize")
    print("=" * 60)


if __name__ == "__main__":
    main()