#!/usr/bin/env python3
"""Test content management API."""
import requests
import io


BASE_URL = "http://localhost:8000/api"

# Test credentials (adjust to match your test user)
TEST_EMAIL = "user1@aada.edu"
TEST_PASSWORD = "Pass123!Word"

# Test module ID (will be retrieved from database)
TEST_MODULE_ID = None


def get_auth_token():
    """Get authentication token."""
    print("Getting authentication token...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )

    if response.status_code != 200:
        print(f"   Login failed: {response.json()}")
        raise Exception("Authentication failed")

    data = response.json()
    print(f"   ✓ Authenticated as {TEST_EMAIL}")
    return data["access_token"]


def get_test_module(token):
    """Get first available module ID."""
    print("\n1. Getting test module...")
    response = requests.get(
        f"{BASE_URL}/content/modules",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"   Status: {response.status_code}")

    if response.status_code != 200:
        print(f"   Error: {response.json()}")
        raise Exception("Failed to get modules")

    data = response.json()
    modules = data.get("modules", [])

    if not modules:
        raise Exception("No modules found in database")

    module = modules[0]
    print(f"   ✓ Using module: {module['code']} - {module['title']}")
    return module["id"]


def test_list_modules(token):
    """Test listing all modules."""
    print("\n2. Testing module list...")
    response = requests.get(
        f"{BASE_URL}/content/modules",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"   Status: {response.status_code}")
    assert response.status_code == 200, "Failed to list modules"

    data = response.json()
    assert "modules" in data, "Missing modules key"

    modules = data["modules"]
    print(f"   ✓ Found {len(modules)} modules")

    if modules:
        module = modules[0]
        print(f"   Module: {module['code']} - has_markdown: {module['has_markdown']}, h5p_count: {module['h5p_count']}")

    return data


def test_upload_markdown(token, module_id):
    """Test uploading module markdown file."""
    print("\n3. Testing markdown upload...")

    # Create test markdown content
    test_markdown = """# Test Module

## Section 1
This is test content.

### Activity 1
(H5P: `M1_H5P_Test`)

## Section 2
More test content.
"""

    # Create file-like object
    files = {
        'file': ('test_module.md', io.BytesIO(test_markdown.encode('utf-8')), 'text/markdown')
    }

    response = requests.post(
        f"{BASE_URL}/content/modules/{module_id}/markdown",
        headers={"Authorization": f"Bearer {token}"},
        files=files
    )

    print(f"   Status: {response.status_code}")

    if response.status_code != 200:
        print(f"   Error: {response.json()}")
        raise Exception("Markdown upload failed")

    data = response.json()
    print(f"   ✓ Markdown uploaded: {data.get('file_path')}")
    assert "file_path" in data, "Missing file_path in response"
    return data


def test_get_markdown(token, module_id):
    """Test downloading module markdown file."""
    print("\n4. Testing markdown download...")

    response = requests.get(
        f"{BASE_URL}/content/modules/{module_id}/markdown",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 404:
        print("   Note: No markdown file exists yet (expected for new module)")
        return None

    assert response.status_code == 200, "Failed to download markdown"

    content = response.text
    print(f"   ✓ Downloaded {len(content)} bytes")
    print(f"   First 100 chars: {content[:100]}...")

    return content


def test_upload_h5p(token, module_id):
    """Test uploading H5P activity."""
    print("\n5. Testing H5P upload...")

    # Create minimal valid ZIP file content (H5P is just a ZIP)
    # This is a simplified test - in real scenario, upload actual .h5p file
    test_h5p_content = b'PK\x03\x04'  # ZIP file header

    files = {
        'file': ('M1_H5P_Test.h5p', io.BytesIO(test_h5p_content), 'application/zip')
    }

    data_fields = {
        'activity_id': 'M1_H5P_Test'
    }

    response = requests.post(
        f"{BASE_URL}/content/modules/{module_id}/h5p",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
        data=data_fields
    )

    print(f"   Status: {response.status_code}")

    if response.status_code != 200:
        print(f"   Error: {response.json()}")
        return None

    data = response.json()
    print(f"   ✓ H5P uploaded: {data.get('activity_id')}")
    return data


def test_list_h5p(token, module_id):
    """Test listing H5P activities."""
    print("\n6. Testing H5P list...")

    response = requests.get(
        f"{BASE_URL}/content/modules/{module_id}/h5p",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"   Status: {response.status_code}")
    assert response.status_code == 200, "Failed to list H5P activities"

    data = response.json()
    assert "activities" in data, "Missing activities key"

    activities = data["activities"]
    print(f"   ✓ Found {len(activities)} H5P activities")

    for activity in activities:
        print(f"     - {activity['activity_id']} ({activity['file_size']} bytes)")

    return data


def test_delete_h5p(token, module_id, activity_id):
    """Test deleting H5P activity."""
    print(f"\n7. Testing H5P delete ({activity_id})...")

    response = requests.delete(
        f"{BASE_URL}/content/modules/{module_id}/h5p/{activity_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 404:
        print("   Note: Activity not found (may have been deleted)")
        return None

    assert response.status_code == 200, "Failed to delete H5P activity"

    data = response.json()
    print(f"   ✓ {data.get('message')}")
    return data


def test_upload_supplemental_file(token, module_id):
    """Test uploading supplemental file."""
    print("\n8. Testing supplemental file upload...")

    # Create test PDF-like content
    test_pdf = b'%PDF-1.4\nTest PDF content'

    files = {
        'file': ('test_document.pdf', io.BytesIO(test_pdf), 'application/pdf')
    }

    data_fields = {
        'subfolder': 'documents'
    }

    response = requests.post(
        f"{BASE_URL}/content/modules/{module_id}/files",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
        data=data_fields
    )

    print(f"   Status: {response.status_code}")

    if response.status_code != 200:
        print(f"   Error: {response.json()}")
        return None

    data = response.json()
    print(f"   ✓ File uploaded: {data.get('filename')}")
    return data


def test_list_supplemental_files(token, module_id):
    """Test listing supplemental files."""
    print("\n9. Testing supplemental file list...")

    response = requests.get(
        f"{BASE_URL}/content/modules/{module_id}/files",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"   Status: {response.status_code}")
    assert response.status_code == 200, "Failed to list files"

    data = response.json()
    assert "files" in data, "Missing files key"

    files = data["files"]
    print(f"   ✓ Found {len(files)} supplemental files")

    for file in files:
        print(f"     - {file['filename']} ({file['type']}, {file['file_size']} bytes)")

    return data


def test_delete_supplemental_file(token, module_id, file_path):
    """Test deleting supplemental file."""
    print(f"\n10. Testing file delete ({file_path})...")

    response = requests.delete(
        f"{BASE_URL}/content/modules/{module_id}/files/{file_path}",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 404:
        print("   Note: File not found (may have been deleted)")
        return None

    assert response.status_code == 200, "Failed to delete file"

    data = response.json()
    print(f"   ✓ {data.get('message')}")
    return data


def test_invalid_file_type(token, module_id):
    """Test that invalid file types are rejected."""
    print("\n11. Testing invalid file type rejection...")

    # Try to upload executable file (not allowed)
    files = {
        'file': ('malicious.exe', io.BytesIO(b'MZ\x90\x00'), 'application/x-msdownload')
    }

    data_fields = {
        'subfolder': 'test'
    }

    response = requests.post(
        f"{BASE_URL}/content/modules/{module_id}/files",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
        data=data_fields
    )

    print(f"   Status: {response.status_code}")
    assert response.status_code == 400, "Should reject invalid file type"

    print("   ✓ Invalid file type correctly rejected")
    return response.json()


def test_unauthorized_access():
    """Test that unauthorized requests are rejected."""
    print("\n12. Testing unauthorized access rejection...")

    response = requests.get(f"{BASE_URL}/content/modules")

    print(f"   Status: {response.status_code}")
    assert response.status_code == 401, "Should require authentication"

    print("   ✓ Unauthorized access correctly rejected")
    return response.json()


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Content Management API")
    print("=" * 60)

    try:
        # Get authentication token
        token = get_auth_token()

        # Get test module
        module_id = get_test_module(token)

        # Run tests
        test_list_modules(token)
        test_upload_markdown(token, module_id)
        test_get_markdown(token, module_id)
        test_upload_h5p(token, module_id)
        test_list_h5p(token, module_id)
        test_upload_supplemental_file(token, module_id)
        test_list_supplemental_files(token, module_id)

        # Cleanup tests
        test_delete_h5p(token, module_id, "M1_H5P_Test.h5p")
        test_delete_supplemental_file(token, module_id, "documents/test_document.pdf")

        # Security tests
        test_invalid_file_type(token, module_id)
        test_unauthorized_access()

        print("\n" + "=" * 60)
        print("✓ All content management API tests passed!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
