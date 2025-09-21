#!/usr/bin/env python3

from services.api_service import get_api_service

def test_verdict_mapping():
    api_service = get_api_service()
    result = api_service.get_candidates()
    print('Sample backend data:')
    
    if isinstance(result, list) and len(result) > 0:
        app = result[0]
        backend_verdict = app.get('verdict', 'Medium')
        
        # Map backend verdict to expected format
        if 'High' in backend_verdict:
            verdict = 'High'
        elif 'Medium' in backend_verdict:
            verdict = 'Medium'  
        elif 'Low' in backend_verdict:
            verdict = 'Low'
        else:
            verdict = 'Medium'
            
        print(f'Original verdict: {backend_verdict}')
        print(f'Mapped verdict: {verdict}')
        print(f'Score: {app.get("relevance_score", 0)}')
        print(f'Job title: {app.get("job", {}).get("job_title", "Unknown")}')
        
        # Check all candidates
        low_count = 0
        medium_count = 0
        high_count = 0
        
        for app in result:
            backend_verdict = app.get('verdict', 'Medium')
            if 'High' in backend_verdict:
                high_count += 1
            elif 'Medium' in backend_verdict:
                medium_count += 1
            elif 'Low' in backend_verdict:
                low_count += 1
        
        print(f'\nVerdict Distribution:')
        print(f'High: {high_count}')
        print(f'Medium: {medium_count}') 
        print(f'Low: {low_count}')
        print(f'Total: {len(result)}')

if __name__ == "__main__":
    test_verdict_mapping()