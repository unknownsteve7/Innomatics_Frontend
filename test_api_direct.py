#!/usr/bin/env python3
"""
Test the get_candidates API method directly
"""

import requests
from typing import Dict

def test_get_candidates_api(base_url: str) -> Dict:
    """Test the get_candidates method logic"""
    try:
        url = f"{base_url}/applications/"
        params = {
            'skip': 0,
            'limit': 100
        }
        print(f"Getting applications from: {url} with params: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            applications = response.json()
            print(f"Retrieved {len(applications)} applications")
            
            # Transform the data to match frontend expectations
            candidates = []
            for app in applications:
                candidate = {
                    'id': app.get('id'),
                    'name': f"Candidate {app.get('id', 'Unknown')}",
                    'job_role': app.get('job', {}).get('job_title', 'Unknown Position'),
                    'job_id': app.get('job_id'),
                    'score': app.get('relevance_score', 0),
                    'verdict': app.get('verdict', 'Medium'),
                    'missing_skills': app.get('missing_skills', []),
                    'feedback': app.get('feedback', ''),
                    'resume_file': app.get('resume_filename', 'resume.pdf'),
                    'application_date': app.get('application_date'),
                    'application_id': app.get('id')
                }
                candidates.append(candidate)
            
            return {"candidates": candidates, "total": len(candidates)}
        else:
            error_msg = f"Failed to get applications with status {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f": {error_detail}"
            except:
                error_msg += f": {response.text}"
            print(error_msg)
            return {"error": error_msg}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error getting applications: {str(e)}"
        print(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Error getting applications: {str(e)}"
        print(error_msg)
        return {"error": error_msg}

if __name__ == "__main__":
    backend_url = "https://ancient-selections-broad-logical.trycloudflare.com"
    
    print(f"Testing get_candidates API with URL: {backend_url}")
    print("=" * 60)
    
    result = test_get_candidates_api(backend_url)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    elif "candidates" in result:
        print(f"✅ Success! Found {result['total']} candidates")
        print("\nFirst few candidates:")
        for i, candidate in enumerate(result['candidates'][:2]):
            print(f"\nCandidate {i+1}:")
            print(f"  Name: {candidate['name']}")
            print(f"  Job: {candidate['job_role']}")
            print(f"  Score: {candidate['score']}")
            print(f"  Verdict: {candidate['verdict']}")
            print(f"  Missing Skills: {', '.join(candidate['missing_skills'][:3])}...")
            print(f"  Resume: {candidate['resume_file']}")
    else:
        print(f"⚠️ Unexpected result: {result}")