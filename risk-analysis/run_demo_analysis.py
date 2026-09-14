"""
Demo script executing real API analysis requests across key hackathon scenarios.
"""

import json
from risk_engine import RiskEngine
from models import AnalysisRequest


def main():
    engine = RiskEngine()
    
    with open("sample_data/sample_conversations.json", "r") as f:
        scenarios = json.load(f)

    print("=" * 80)
    print("NEXORA - CONVERSATION & RISK ANALYSIS DEMO EXECUTIONS")
    print("=" * 80)

    for sc in scenarios:
        print(f"\n▶ [{sc['scenario_id']}] {sc['name']}")
        print(f"Description: {sc['description']}")
        
        req_data = sc["request"]
        request = AnalysisRequest(**req_data)
        
        print("\n--- API REQUEST ---")
        print(json.dumps(req_data, indent=2))
        
        response = engine.evaluate(request)
        
        print("\n--- API RESPONSE ---")
        print(json.dumps(response.model_dump(), indent=2))
        print("-" * 80)


if __name__ == "__main__":
    main()
