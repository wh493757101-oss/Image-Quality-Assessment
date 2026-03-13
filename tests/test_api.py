from fastapi.testclient import TestClient
from main import app
import time

client = TestClient(app)

def test_webpage_loads():
    """测试用例 1：验证前端看板是否正常加载"""
    response = client.get("/")
    assert response.status_code == 200
    assert "VisionGuard" in response.text

def test_submit_without_file():
    """测试用例 2：异常边界测试 - 不传文件直接请求"""
    response = client.post("/api/v1/submit_eval")
    assert response.status_code == 422 

def test_submit_valid_image_async_decoupling():
    """测试用例 3：集成测试 - 验证异步解耦机制"""
    files = {"pred_file": ("test.jpg", b"fake_image_data", "image/jpeg")}
    response = client.post("/api/v1/submit_eval", files=files)
    
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"