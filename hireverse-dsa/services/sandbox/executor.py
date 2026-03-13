import docker
import docker.errors
import subprocess
import tempfile
import time
import os
import base64
import logging
import shutil

logger = logging.getLogger(__name__)

def run_code(code: str, language: str, test_cases: list) -> dict:
    try:
        client = docker.from_env()
        client.ping()
        use_docker = True
    except docker.errors.DockerException:
        logger.warning("Docker daemon unavailable. Falling back to subprocess.")
        use_docker = False

    passed_cases = 0
    total_cases = len(test_cases)
    status = "pass"
    runtime_ms = 0
    memory_kb = 0
    per_case_results = []

    for idx, tc in enumerate(test_cases):
        case_id = idx + 1
        input_data = tc.get("input", "")
        # Handle variations between expected / expected_output mapping
        expected_output = tc.get("expected_output", tc.get("expected", ""))
        is_hidden = tc.get("is_hidden", False)
        
        start_time = time.time()
        
        if use_docker:
            actual_output, error, run_status = _run_docker(client, code, language, input_data)
        else:
            actual_output, error, run_status = _run_subprocess(code, language, input_data)
            
        case_runtime_ms = int((time.time() - start_time) * 1000)
        runtime_ms += case_runtime_ms
        
        passed = False
        if run_status == "timeout":
            status = "timeout"
        elif run_status == "error" or error:
            status = "error" if status == "pass" else status
        else:
            passed = (actual_output.strip() == expected_output.strip())
            if not passed:
                status = "fail" if status == "pass" else status
                
        if passed:
            passed_cases += 1
            
        per_case_results.append({
            "case_id": case_id,
            "passed": passed,
            "input": "" if is_hidden else input_data,
            "expected": "" if is_hidden else expected_output,
            "actual": actual_output.strip(),
            "hidden": is_hidden,
            "error": error.strip() if error else ""
        })
        
    return {
        "status": status,
        "passed_cases": passed_cases,
        "total_cases": total_cases,
        "runtime_ms": runtime_ms,
        "memory_kb": memory_kb,
        "per_case_results": per_case_results
    }

def _run_docker(client, code, language, input_data):
    image = "python:3.11-slim" if language == "python" else "eclipse-temurin:17-jre"
    b64_code = base64.b64encode(code.encode("utf-8")).decode("utf-8")
    b64_input = base64.b64encode(input_data.encode("utf-8")).decode("utf-8") if input_data else ""
    
    if language == "python":
        if b64_input:
            cmd = "echo $CODE | base64 -d > /tmp/solution.py && echo $INPUT | base64 -d | python /tmp/solution.py"
        else:
            cmd = "echo $CODE | base64 -d > /tmp/solution.py && python /tmp/solution.py"
    else:
        if b64_input:
            cmd = "echo $CODE | base64 -d > /tmp/Solution.java && javac /tmp/Solution.java && echo $INPUT | base64 -d | java -cp /tmp Solution"
        else:
            cmd = "echo $CODE | base64 -d > /tmp/Solution.java && javac /tmp/Solution.java && java -cp /tmp Solution"
            
    try:
        container = client.containers.run(
            image,
            command=["sh", "-c", cmd],
            environment={"CODE": b64_code, "INPUT": b64_input},
            mem_limit="256m",
            cpu_quota=50000,
            network_disabled=True,
            detach=True
        )
        
        start_time = time.time()
        timeout = 5
        
        while container.status in ["created", "running"]:
            if time.time() - start_time > timeout:
                container.kill()
                container.remove(force=True)
                return "", "Execution timed out", "timeout"
            time.sleep(0.1)
            container.reload()
            
        logs = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
        err_logs = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")
        
        result = container.wait()
        container.remove(force=True)
        
        run_status = "success"
        if result.get("StatusCode", 0) != 0:
            run_status = "error"
            
        return logs, err_logs, run_status
    except Exception as e:
        return "", str(e), "error"

def _run_subprocess(code, language, input_data):
    if language == "python":
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as f:
            f.write(code)
            temp_path = f.name
        cmd = ["python", temp_path]
        try:
            result = subprocess.run(cmd, input=input_data, text=True, capture_output=True, timeout=5)
            os.remove(temp_path)
            
            run_status = "success"
            if result.returncode != 0:
                run_status = "error"
            return result.stdout, result.stderr, run_status
        except subprocess.TimeoutExpired as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return e.stdout or "", e.stderr or "Execution timed out", "timeout"
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return "", str(e), "error"
    else:
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, "Solution.java")
        with open(temp_path, "w", encoding='utf-8') as f:
            f.write(code)
            
        comp = subprocess.run(["javac", temp_path], capture_output=True, text=True)
        if comp.returncode != 0:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return "", comp.stderr, "error"
            
        cmd = ["java", "-cp", temp_dir, "Solution"]
        try:
            result = subprocess.run(cmd, input=input_data, text=True, capture_output=True, timeout=5)
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            run_status = "success"
            if result.returncode != 0:
                run_status = "error"
            return result.stdout, result.stderr, run_status
        except subprocess.TimeoutExpired as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return e.stdout or "", e.stderr or "Execution timed out", "timeout"
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return "", str(e), "error"
