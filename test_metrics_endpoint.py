#!/usr/bin/env python3

import requests

def test_metrics_endpoint():
    backend_url = "https://innomaticshackathonbackend-production.up.railway.app"
    
    try:
        print(f"Testing /metrics/ endpoint at: {backend_url}")
        print("=" * 60)
        
        # Test /metrics/ endpoint
        url = f"{backend_url}/metrics/"
        response = requests.get(url)
        
        if response.status_code == 200:
            metrics = response.json()
            print("✅ Metrics endpoint successful!")
            print(f"Total Applications: {metrics.get('total_applications', 'N/A')}")
            print(f"Average Score: {metrics.get('avg_score', 'N/A')}")
            print(f"Open Positions: {metrics.get('open_positions', 'N/A')}")
            print(f"High-Fit Candidates: {metrics.get('high_fit_candidates', 'N/A')}")
            
            # Check if this matches our manual calculation
            print("\n" + "=" * 60)
            print("Comparison with /applications/ endpoint:")
            
            # Get applications for comparison
            apps_url = f"{backend_url}/applications/"
            apps_response = requests.get(apps_url)
            
            if apps_response.status_code == 200:
                applications = apps_response.json()
                manual_total = len(applications)
                manual_avg = sum(app.get('relevance_score', 0) for app in applications) / len(applications) if applications else 0
                manual_high_fit = len([app for app in applications if 'High' in app.get('verdict', '')])
                
                print(f"Manual calculation from /applications/:")
                print(f"  Total Applications: {manual_total}")
                print(f"  Average Score: {manual_avg:.1f}")
                print(f"  High-Fit Candidates: {manual_high_fit}")
                
                print(f"\n/metrics/ endpoint:")
                print(f"  Total Applications: {metrics.get('total_applications')}")
                print(f"  Average Score: {metrics.get('avg_score')}")
                print(f"  High-Fit Candidates: {metrics.get('high_fit_candidates')}")
                
                # Check if they match
                total_match = metrics.get('total_applications') == manual_total
                score_match = abs(metrics.get('avg_score', 0) - manual_avg) < 0.1
                high_fit_match = metrics.get('high_fit_candidates') == manual_high_fit
                
                print(f"\nData consistency:")
                print(f"  Total Applications: {'✅' if total_match else '❌'}")
                print(f"  Average Score: {'✅' if score_match else '❌'}")
                print(f"  High-Fit Candidates: {'✅' if high_fit_match else '❌'}")
            
        else:
            print(f"❌ Metrics endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing metrics endpoint: {str(e)}")

if __name__ == "__main__":
    test_metrics_endpoint()