import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DSAProblem(Base):
    __tablename__ = "dsa_problems"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    difficulty = Column(String)  # 'beginner' | 'intermediate' | 'advanced'
    category = Column(String)  # 'arrays' | 'strings' | 'trees' | 'graphs' | 'dp' | 'greedy' | 'sorting' | 'binary_search'
    problem_statement = Column(Text, nullable=False)
    python_signature = Column(Text)  # starter function stub
    java_signature = Column(Text)  # starter function stub
    examples = Column(JSON)  # [{input, output, explanation}]
    test_cases = Column(JSON)  # [{input, expected_output, is_hidden}]
    time_limit_ms = Column(Integer, default=5000)
    memory_limit_mb = Column(Integer, default=256)

class DSASubmission(Base):
    __tablename__ = "dsa_submissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String, nullable=True)  # Provided by integrating platform
    problem_id = Column(Integer, ForeignKey("dsa_problems.id"))
    language = Column(String)  # 'python' | 'java'
    code = Column(Text)
    status = Column(String)  # 'pass' | 'fail' | 'error' | 'timeout'
    passed_cases = Column(Integer, default=0)
    total_cases = Column(Integer, default=0)
    runtime_ms = Column(Integer)
    memory_kb = Column(Integer)
    time_complexity = Column(String)
    space_complexity = Column(String)
    ai_feedback = Column(Text)
    follow_up = Column(Text)
    dsa_score = Column(Integer, default=0)
    submitted_at = Column(TIMESTAMP, default=datetime.utcnow)
