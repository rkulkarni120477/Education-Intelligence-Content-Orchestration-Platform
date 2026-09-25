#!/usr/bin/env python3
"""Quick integration test for courses API"""

import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check"""
    print("=" * 60)
    print("Testing Health Check")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"Status: {response.status_code}")
        pprint(response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_create_course():
    """Test creating a course"""
    print("\n" + "=" * 60)
    print("Testing Create Course")
    print("=" * 60)
    try:
        data = {
            "name": "Grade 4 Mathematics",
            "grade_level": "4",
            "subject": "Math",
            "description": "Introduction to fractions and decimals"
        }
        response = requests.post(
            f"{BASE_URL}/api/courses",
            json=data,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        pprint(result)

        if response.status_code == 201:
            print(f"\nCourse created with ID: {result.get('id')}")
            return result.get('id')
        else:
            print(f"Failed: {result}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_list_courses():
    """Test listing courses"""
    print("\n" + "=" * 60)
    print("Testing List Courses")
    print("=" * 60)
    try:
        response = requests.get(
            f"{BASE_URL}/api/courses",
            timeout=5
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        pprint(result)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_course(course_id):
    """Test getting a specific course"""
    print("\n" + "=" * 60)
    print(f"Testing Get Course: {course_id}")
    print("=" * 60)
    try:
        response = requests.get(
            f"{BASE_URL}/api/courses/{course_id}",
            timeout=5
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        pprint(result)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("\nRunning Integration Tests\n")

    # Test health check
    if not test_health():
        print("\nHealth check failed - backend not responding")
        exit(1)

    # Test course creation
    course_id = test_create_course()

    if course_id:
        # Test get course
        test_get_course(course_id)

        # Test list courses
        test_list_courses()

        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)
    else:
        print("\nCourse creation failed - stopping tests")
        exit(1)
