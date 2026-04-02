import requests

PRESIGNED_URL: str = "http://storage:9000/testbucket/uv.lock?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=testuser%2F20260402%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260402T000239Z&X-Amz-Expires=1800&X-Amz-SignedHeaders=host&X-Amz-Signature=6eb33d9b551de119e69b486a88e18b99583e13a33d2e978d89342e4352c985be"
file_path: str = "/home/glp-desktop/Workspace/Open-Document-Manager/api/uv.lock"

with open(file_path, "rb") as f:
    response = requests.put(PRESIGNED_URL, data=f)
if response.status_code == 200:
    print(response.text)  # noqa: T201
else:
    print(f"❌ Error upload: {response.status_code}")  # noqa: T201
    print(response.text)  # noqa: T201
