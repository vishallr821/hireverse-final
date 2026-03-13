import ast
import json
import os
from groq import Groq

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.max_loop_depth = 0
        self.current_loop_depth = 0
        self.has_recursion = False
        self.recursive_log_n = False
        self.has_sorting = False
        self.grows_space = False
        self.current_func = None
        
    def visit_FunctionDef(self, node):
        prev_func = self.current_func
        self.current_func = node.name
        self.generic_visit(node)
        self.current_func = prev_func

    def visit_For(self, node):
        self.current_loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)
        self.generic_visit(node)
        self.current_loop_depth -= 1

    def visit_While(self, node):
        self.current_loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)
        self.generic_visit(node)
        self.current_loop_depth -= 1

    def visit_Call(self, node):
        # Detect recursion
        if isinstance(node.func, ast.Name) and node.func.id == self.current_func:
            self.has_recursion = True
            # check if argument is n//2 or n/2
            for arg in node.args:
                if isinstance(arg, ast.BinOp):
                    if isinstance(arg.op, (ast.Div, ast.FloorDiv)):
                        if isinstance(arg.right, ast.Constant) and arg.right.value == 2:
                            self.recursive_log_n = True
                            
        # Detect sorting
        if isinstance(node.func, ast.Name) and node.func.id in ['sorted', 'heapq']:
            self.has_sorting = True
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'sort':
            self.has_sorting = True
            
        # Detect space complexity (growing list/dict/set)
        if isinstance(node.func, ast.Attribute) and node.func.attr in ['append', 'add', 'insert']:
            self.grows_space = True
            
        self.generic_visit(node)
        
    def visit_ListComp(self, node):
        self.current_loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)
        self.grows_space = True
        self.generic_visit(node)
        self.current_loop_depth -= 1
        
    def visit_DictComp(self, node):
        self.current_loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)
        self.grows_space = True
        self.generic_visit(node)
        self.current_loop_depth -= 1

    def visit_SetComp(self, node):
        self.current_loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)
        self.grows_space = True
        self.generic_visit(node)
        self.current_loop_depth -= 1

def analyse(code: str, language: str) -> dict:
    if language.lower() == "python":
        try:
            tree = ast.parse(code)
            return _analyse_python_ast(tree, code)
        except Exception:
            return _fallback_groq(code, language)
    else:
        return _fallback_groq(code, language)
        
def _analyse_python_ast(tree, code):
    visitor = ComplexityVisitor()
    visitor.visit(tree)
    
    time_complexity = "O(1)"
    space_complexity = "O(1)"
    confidence = "high"
    
    # Time complexity
    if visitor.has_recursion:
        if visitor.recursive_log_n:
            time_complexity = "O(log n)"
        else:
            time_complexity = "O(2ⁿ)"
    elif visitor.has_sorting:
        time_complexity = "O(n log n)"
    else:
        if visitor.max_loop_depth == 1:
            time_complexity = "O(n)"
        elif visitor.max_loop_depth == 2:
            time_complexity = "O(n²)"
        elif visitor.max_loop_depth >= 3:
            time_complexity = "O(n³)"
            
    # Space complexity
    if visitor.grows_space or visitor.has_recursion:
        space_complexity = "O(n)"
        
    return {
        "time_complexity": time_complexity,
        "space_complexity": space_complexity,
        "confidence": confidence
    }

def _fallback_groq(code, language):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    prompt = f"Analyse this {language} code.\nReturn exactly: \n{{time_complexity: str, space_complexity: str, confidence: str}}\n\nCode:\n{code}"
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an algorithm complexity analyser. Respond only in raw JSON, no markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        response_text = completion.choices[0].message.content.strip()
        
        # Clean markdown formatting if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
            
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        data = json.loads(response_text.strip())
        return {
            "time_complexity": data.get("time_complexity", "unknown"),
            "space_complexity": data.get("space_complexity", "unknown"),
            "confidence": data.get("confidence", "low")
        }
    except Exception:
        return {
            "time_complexity": "unknown",
            "space_complexity": "unknown",
            "confidence": "low"
        }
