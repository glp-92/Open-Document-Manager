import requests

PRESIGNED_URL: str = "http://storage:9000/testbucket/60d6e56d-f010-4015-a086-d01a81115121/uv.lock?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=testuser%2F20260402%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260402T015139Z&X-Amz-Expires=1800&X-Amz-SignedHeaders=host&X-Amz-Signature=bb4a64c7f4d32d5ccd5b8e93d20de14bca6b2fcf41c33d5d923fc02bc3f55770"
file_path: str = "/home/glp-desktop/Workspace/Open-Document-Manager/api/uv.lock"

with open(file_path, "rb") as f:
    response = requests.put(PRESIGNED_URL, data=f)
if response.status_code == 200:
    print(response.text)  # noqa: T201
else:
    print(f"❌ Error upload: {response.status_code}")  # noqa: T201
    print(response.text)  # noqa: T201
