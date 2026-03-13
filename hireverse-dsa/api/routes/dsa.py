import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List

from db.database import get_db
from models.models import DSAProblem, DSASubmission
from services.sandbox.executor import run_code
from services.analyser.complexity import analyse
from services.ai.feedback import generate_feedback, generate_hint, generate_follow_up, calculate_dsa_score

router = APIRouter()

class SubmitRequest(BaseModel):
    problem_id: int
    language: str
    code: str

class HintRequest(BaseModel):
    problem_id: int
    code: str
    level: int

@router.get("/problems")
async def get_problems(difficulty: Optional[str] = None, category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(DSAProblem)
    if difficulty:
        query = query.where(DSAProblem.difficulty == difficulty)
    if category:
        query = query.where(DSAProblem.category == category)
        
    result = await db.execute(query)
    problems = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "title": p.title,
            "difficulty": p.difficulty,
            "category": p.category
        }
        for p in problems
    ]

@router.get("/problems/{id}")
async def get_problem(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DSAProblem).where(DSAProblem.id == id))
    p = result.scalars().first()
    if not p:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    visible_tests = [tc for tc in p.test_cases if not tc.get("is_hidden")]
    
    return {
        "id": p.id,
        "title": p.title,
        "difficulty": p.difficulty,
        "category": p.category,
        "problem_statement": p.problem_statement,
        "python_signature": p.python_signature,
        "java_signature": p.java_signature,
        "examples": p.examples,
        "test_cases": visible_tests
    }

@router.post("/submit")
async def submit_solution(req: SubmitRequest, db: AsyncSession = Depends(get_db)):
    # 1. Fetch problem
    result = await db.execute(select(DSAProblem).where(DSAProblem.id == req.problem_id))
    problem = result.scalars().first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    # 2. Call run_code with overall API timeout handling
    try:
        # We enforce a hard 10-second ceiling across all test cases combined.
        # run_code execution already has a 5-second timeout *per* testcase.
        exec_res = await asyncio.wait_for(
            asyncio.to_thread(run_code, req.code, req.language, problem.test_cases),
            timeout=10.0
        )
    except asyncio.TimeoutError:
        exec_res = {
            "status": "timeout",
            "passed_cases": 0,
            "total_cases": len(problem.test_cases),
            "runtime_ms": 10000,
            "memory_kb": 0,
            "per_case_results": [{"case_id": i+1, "passed": False, "error": "Overall API execution timeout (10s limit)"} for i in range(len(problem.test_cases))]
        }
    
    # 3. Call analyse
    analysis = analyse(req.code, req.language)
    
    # 4. Call generate_feedback
    quality_score = 10 # Base quality score out of 20
    if analysis["confidence"] == "high":
        quality_score += 5
        
    feedback = generate_feedback(
        problem.problem_statement,
        req.code,
        req.language,
        exec_res["passed_cases"],
        exec_res["total_cases"],
        analysis["time_complexity"],
        analysis["space_complexity"]
    )
    
    # 5. Follow up if all cases passed
    follow_up = ""
    if exec_res["status"] == "pass" and exec_res["passed_cases"] == exec_res["total_cases"] and exec_res["total_cases"] > 0:
        follow_up = generate_follow_up(problem.problem_statement, req.code)
        
    # 6. Calculate Score
    score = calculate_dsa_score(
        exec_res["passed_cases"],
        exec_res["total_cases"],
        analysis["time_complexity"],
        quality_score
    )
    
    # 7. Save to DB
    submission = DSASubmission(
        candidate_id="guest", # Or None if upstream integration is used later
        problem_id=problem.id,
        language=req.language,
        code=req.code,
        status=exec_res["status"],
        passed_cases=exec_res["passed_cases"],
        total_cases=exec_res["total_cases"],
        runtime_ms=exec_res["runtime_ms"],
        memory_kb=exec_res["memory_kb"],
        time_complexity=analysis["time_complexity"],
        space_complexity=analysis["space_complexity"],
        ai_feedback=feedback,
        follow_up=follow_up,
        dsa_score=score
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    
    return {
        "status": exec_res["status"],
        "passed_cases": exec_res["passed_cases"],
        "total_cases": exec_res["total_cases"],
        "runtime_ms": exec_res["runtime_ms"],
        "memory_kb": exec_res["memory_kb"],
        "per_case_results": exec_res["per_case_results"],
        "time_complexity": analysis["time_complexity"],
        "space_complexity": analysis["space_complexity"],
        "ai_feedback": feedback,
        "follow_up_question": follow_up,
        "dsa_score": score
    }

@router.post("/hint")
async def get_hint(req: HintRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DSAProblem).where(DSAProblem.id == req.problem_id))
    problem = result.scalars().first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    hint = generate_hint(problem.problem_statement, req.code, req.level)
    return {
        "hint": hint,
        "level": req.level
    }

