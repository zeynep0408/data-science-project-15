from unittest.mock import patch
import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tasks.task_manager import *

def test_simple_random_sampling():
    data = list(range(100))
    sample = simple_random_sampling(data, 10)
    assert len(sample) == 10
    assert all(x in data for x in sample)

def test_systematic_sampling():
    data = list(range(20))
    sample = systematic_sampling(data, 5)
    assert len(sample) <= len(data)
    assert sample[1] - sample[0] == 5 or len(sample) == 1

def test_stratified_sampling():
    data = [{'name': 'Walt', 'role': 'chemist'},
            {'name': 'Jesse', 'role': 'assistant'},
            {'name': 'Gus', 'role': 'boss'},
            {'name': 'Mike', 'role': 'boss'}]
    sample = stratified_sampling(data, lambda x: x['role'], 1)
    roles = set([x['role'] for x in sample])
    assert roles == {'chemist', 'assistant', 'boss'}

def test_cluster_sampling():
    clusters = {
        'cluster1': [1,2,3],
        'cluster2': [4,5],
        'cluster3': [6,7,8]
    }
    sample = cluster_sampling(clusters, ['cluster1', 'cluster3'])
    assert set(sample) == {1,2,3,6,7,8}

def test_convenience_sampling():
    data = list(range(50))
    sample = convenience_sampling(data, 10)
    assert sample == data[:10]

def test_judgmental_sampling():
    data = list(range(10))
    sample = judgmental_sampling(data, lambda x: x % 2 == 0)
    assert all(x % 2 == 0 for x in sample)

def test_quota_sampling():
    data = [{'name': 'Walt', 'role': 'chemist'},
            {'name': 'Jesse', 'role': 'assistant'},
            {'name': 'Gus', 'role': 'boss'},
            {'name': 'Mike', 'role': 'boss'}]
    quotas = {'chemist': 1, 'assistant': 1, 'boss': 1}
    sample = quota_sampling(data, lambda x: x['role'], quotas)
    roles = [x['role'] for x in sample]
    assert roles.count('boss') == 1

def test_snowball_sampling():
    data = list(range(1, 6))
    neighbors_map = {
        1: [2,3],
        2: [4],
        3: [5],
        4: [],
        5: []
    }
    def get_neighbors(x):
        return neighbors_map.get(x, [])
    sample = snowball_sampling(data, [1], get_neighbors, 4)
    assert 1 in sample
    assert len(sample) <= 4

def send_post_request(url: str, data: dict, headers: dict = None):
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # hata varsa exception fırlatır
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
    except Exception as err:
        print(f"Other error occurred: {err}")

class ResultCollector:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            if report.passed:
                self.passed += 1
            elif report.failed:
                self.failed += 1

def run_tests():
    collector = ResultCollector()
    pytest.main(["tests"], plugins=[collector])
    print(f"\nToplam Başarılı: {collector.passed}")
    print(f"Toplam Başarısız: {collector.failed}")
    
    user_score = (collector.passed / (collector.passed + collector.failed)) * 100
    print(round(user_score, 2))
    
    url = "https://kaizu-api-8cd10af40cb3.herokuapp.com/projectLog"
    payload = {
        "user_id": 34,
        "project_id": 632,
        "user_score": round(user_score, 2),
        "is_auto": False
    }
    headers = {
        "Content-Type": "application/json"
    }
    send_post_request(url, payload, headers)

if __name__ == "__main__":
    run_tests()
