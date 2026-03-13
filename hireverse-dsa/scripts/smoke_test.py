import asyncio
import httpx
import sys

BASE_URL = "http://localhost:8000"

async def main():
    print("Starting HireVerse DSA Module Smoke Tests...")
    passed_checks = 0
    total_checks = 7
    token = None

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=15.0) as client:
        # Step 1: Register
        try:
            res1 = await client.post("/auth/register", json={
                "name": "Test Student",
                "email": "test@hireverse.dev",
                "password": "test1234",
                "college": "SRM TRP"
            })
            if res1.status_code in [200, 409]:
                print("[PASS] Step 1: Register a test student")
                passed_checks += 1
            else:
                print(f"[FAIL] Step 1: Register failed with status {res1.status_code} - {res1.text}")
        except Exception as e:
            print(f"[FAIL] Step 1 Exception: {e}")

        # Step 2: Login
        try:
            res2 = await client.post("/auth/login", json={
                "email": "test@hireverse.dev",
                "password": "test1234"
            })
            if res2.status_code == 200 and "access_token" in res2.json():
                print("[PASS] Step 2: Login")
                token = res2.json()["access_token"]
                passed_checks += 1
            else:
                print(f"[FAIL] Step 2: Login failed with status {res2.status_code} - {res2.text}")
        except Exception as e:
            print(f"[FAIL] Step 2 Exception: {e}")

        if not token:
            print(f"\nFinal summary: {passed_checks}/{total_checks} checks passed")
            sys.exit(1)

        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Fetch problems
        try:
            res3 = await client.get("/dsa/problems")
            if res3.status_code == 200 and len(res3.json()) >= 10:
                print("[PASS] Step 3: Fetch problem list")
                passed_checks += 1
            else:
                print(f"[FAIL] Step 3: Problem list count less than 10 or fetch failed. Status: {res3.status_code}")
        except Exception as e:
            print(f"[FAIL] Step 3 Exception: {e}")

        # Step 4: Fetch problem 1 detail
        try:
            res4 = await client.get("/dsa/problems/1")
            data4 = res4.json()
            if res4.status_code == 200 and "problem_statement" in data4 and "python_signature" in data4:
                print("[PASS] Step 4: Fetch problem 1 detail")
                passed_checks += 1
            else:
                print(f"[FAIL] Step 4: Missing expected data. Status: {res4.status_code}")
        except Exception as e:
            print(f"[FAIL] Step 4 Exception: {e}")

        # Step 5: Submit solution
        solution = """def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i"""
        try:
            res5 = await client.post("/dsa/submit", headers=headers, json={
                "problem_id": 1,
                "language": "python",
                "code": solution
            }, timeout=20.0) # Larger timeout for execution
            
            data5 = res5.json() if res5.status_code == 200 else {}
            if res5.status_code == 200 and data5.get("dsa_score", 0) > 0:
                print("[PASS] Step 5: Submit a correct Two Sum solution")
                passed_checks += 1
            else:
                print(f"[FAIL] Step 5: Submission failed or score 0. Status: {res5.status_code} - {res5.text}")
        except Exception as e:
            print(f"[FAIL] Step 5 Exception: {e}")

        # Step 6: Request a hint
        try:
            res6 = await client.post("/dsa/hint", headers=headers, json={
                "problem_id": 1,
                "code": "def two_sum(): pass",
                "level": 1
            })
            if res6.status_code == 200 and res6.json().get("hint"):
                print("[PASS] Step 6: Request a hint")
                passed_checks += 1
            else:
                print(f"[FAIL] Step 6: Hint fetch failed or empty string returned. Status: {res6.status_code}")
        except Exception as e:
            print(f"[FAIL] Step 6 Exception: {e}")

        # Step 7: Fetch leaderboard
        try:
            res7 = await client.get("/dsa/leaderboard")
            if res7.status_code == 200 and isinstance(res7.json(), list):
                print("[PASS] Step 7: Fetch leaderboard")
                passed_checks += 1
            else:
                print(f"[FAIL] Step 7: Leaderboard generic fetch failed. Status: {res7.status_code}")
        except Exception as e:
            print(f"[FAIL] Step 7 Exception: {e}")

    print(f"\nFinal summary: {passed_checks}/{total_checks} checks passed")
    if passed_checks == total_checks:
        print("HireVerse DSA Module is demo-ready!")

if __name__ == "__main__":
    asyncio.run(main())
