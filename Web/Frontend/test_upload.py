import requests
import os

def test_upload_api():
    """Test the upload API endpoint"""
    url = "http://localhost:8000/upload"
    
    # Test with a simple text file
    test_file_content = "This is a test file for upload API"
    test_filename = "test.txt"
    
    # Create a temporary test file
    with open(test_filename, "w") as f:
        f.write(test_file_content)
    
    try:
        # Test upload
        with open(test_filename, "rb") as f:
            files = {"files": (test_filename, f, "text/plain")}
            response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Upload API is working correctly!")
        else:
            print("❌ Upload API has issues")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
    finally:
        # Clean up test file
        if os.path.exists(test_filename):
            os.remove(test_filename)

if __name__ == "__main__":
    test_upload_api()
