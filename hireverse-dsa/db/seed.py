import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import async_session
from models.models import DSAProblem

async def run_seed():
    async with async_session() as session:
        result = await session.execute(select(DSAProblem).limit(1))
        if result.scalars().first():
            return
            
        problems = [
            DSAProblem(
                title="Two Sum",
                difficulty="beginner",
                category="arrays",
                problem_statement="Given a list of integers and a target, return the indices of two numbers that add up to the target. Assume exactly one solution exists.\nInput format: first line = space-separated integers (the list), second line = target integer\nOutput format: two space-separated indices",
                python_signature='def two_sum(nums: list[int], target: int) -> list[int]:\n    # Write your code here\n    pass\n\nif __name__ == "__main__":\n    import sys\n    input_data = sys.stdin.read().splitlines()\n    if len(input_data) >= 2:\n        nums = list(map(int, input_data[0].split()))\n        target = int(input_data[1])\n        res = two_sum(nums, target)\n        if res: print(f"{res[0]} {res[1]}")',
                java_signature='import java.util.*;\n\npublic class Solution {\n    public static int[] twoSum(int[] nums, int target) {\n        // Write your code here\n        return new int[]{0, 0};\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextLine()) {\n            String[] parts = sc.nextLine().trim().split("\\\\s+");\n            int[] nums = new int[parts.length];\n            for (int i=0; i<parts.length; i++) nums[i] = Integer.parseInt(parts[i]);\n            int target = sc.nextInt();\n            int[] res = twoSum(nums, target);\n            if (res != null && res.length >= 2) System.out.println(res[0] + " " + res[1]);\n        }\n    }\n}',
                examples=[
                    {"input": "2 7 11 15\n9", "output": "0 1", "explanation": "nums[0] + nums[1] == 9, we return 0 1"},
                    {"input": "3 2 4\n6", "output": "1 2", "explanation": "nums[1] + nums[2] == 6"},
                    {"input": "3 3\n6", "output": "0 1", "explanation": "nums[0] + nums[1] == 6"}
                ],
                test_cases=[
                    {"input": "2 7 11 15\n9", "expected_output": "0 1", "is_hidden": False},
                    {"input": "3 2 4\n6", "expected_output": "1 2", "is_hidden": False},
                    {"input": "3 3\n6", "expected_output": "0 1", "is_hidden": False},
                    {"input": "2 5 5 11\n10", "expected_output": "1 2", "is_hidden": True},
                    {"input": "-1 -2 -3 -4 -5\n-8", "expected_output": "2 4", "is_hidden": True}
                ]
            ),
            DSAProblem(
                title="Reverse a String",
                difficulty="beginner",
                category="strings",
                problem_statement="Given a string, return it reversed.\nInput: a single string. Output: reversed string.",
                python_signature='def reverse_string(s: str) -> str:\n    # Write your code here\n    pass\n\nif __name__ == "__main__":\n    import sys\n    s = sys.stdin.read().strip()\n    print(reverse_string(s))',
                java_signature='import java.util.*;\n\npublic class Solution {\n    public static String reverseString(String s) {\n        // Write your code here\n        return "";\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextLine()) {\n            String s = sc.nextLine();\n            System.out.println(reverseString(s));\n        }\n    }\n}',
                examples=[
                    {"input": "hello", "output": "olleh", "explanation": "'hello' reversed is 'olleh'"},
                    {"input": "HireVerse", "output": "esreVeriH", "explanation": "Case is preserved"},
                    {"input": "a", "output": "a", "explanation": "Single character string remains same"}
                ],
                test_cases=[
                    {"input": "hello", "expected_output": "olleh", "is_hidden": False},
                    {"input": "HireVerse", "expected_output": "esreVeriH", "is_hidden": False},
                    {"input": "a", "expected_output": "a", "is_hidden": False},
                    {"input": "racecar", "expected_output": "racecar", "is_hidden": True},
                    {"input": "12345", "expected_output": "54321", "is_hidden": True}
                ]
            ),
            DSAProblem(
                title="Binary Search",
                difficulty="beginner",
                category="binary_search",
                problem_statement="Given a sorted list of integers and a target, return the index of the target. Return -1 if not found.\nInput: first line = sorted integers, second line = target\nOutput: index or -1",
                python_signature='def binary_search(nums: list[int], target: int) -> int:\n    # Write your code here\n    pass\n\nif __name__ == "__main__":\n    import sys\n    lines = sys.stdin.read().splitlines()\n    if len(lines) >= 2:\n        nums = list(map(int, lines[0].split())) if lines[0].strip() else []\n        target = int(lines[1])\n        print(binary_search(nums, target))',
                java_signature='import java.util.*;\n\npublic class Solution {\n    public static int binarySearch(int[] nums, int target) {\n        // Write your code here\n        return -1;\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextLine()) {\n            String firstLine = sc.nextLine().trim();\n            int[] nums = new int[0];\n            if (!firstLine.isEmpty()) {\n                String[] parts = firstLine.split("\\\\s+");\n                nums = new int[parts.length];\n                for (int i=0; i<parts.length; i++) nums[i] = Integer.parseInt(parts[i]);\n            }\n            if (sc.hasNextInt()) {\n                int target = sc.nextInt();\n                System.out.println(binarySearch(nums, target));\n            }\n        }\n    }\n}',
                examples=[
                    {"input": "-1 0 3 5 9 12\n9", "output": "4", "explanation": "9 exists in nums and its index is 4"},
                    {"input": "-1 0 3 5 9 12\n2", "output": "-1", "explanation": "2 does not exist in nums so return -1"},
                    {"input": "5\n5", "output": "0", "explanation": "5 is at index 0"}
                ],
                test_cases=[
                    {"input": "-1 0 3 5 9 12\n9", "expected_output": "4", "is_hidden": False},
                    {"input": "-1 0 3 5 9 12\n2", "expected_output": "-1", "is_hidden": False},
                    {"input": "5\n5", "expected_output": "0", "is_hidden": False},
                    {"input": "1 2 3\n0", "expected_output": "-1", "is_hidden": True},
                    {"input": "1 2 3 4 5 6 7\n7", "expected_output": "6", "is_hidden": True}
                ]
            ),
            DSAProblem(
                title="Valid Parentheses",
                difficulty="beginner",
                category="strings",
                problem_statement="Given a string of brackets ()[]{} return True if the brackets are valid (properly opened and closed), else False.\nInput: bracket string. Output: True or False",
                python_signature='def is_valid(s: str) -> bool:\n    # Write your code here\n    pass\n\nif __name__ == "__main__":\n    import sys\n    s = sys.stdin.read().strip()\n    print(is_valid(s))',
                java_signature='import java.util.*;\n\npublic class Solution {\n    public static boolean isValid(String s) {\n        // Write your code here\n        return false;\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextLine()) {\n            String s = sc.nextLine().trim();\n            System.out.println(isValid(s) ? "True" : "False");\n        }\n    }\n}',
                examples=[
                    {"input": "()", "output": "True", "explanation": "Valid"},
                    {"input": "()[]{}", "output": "True", "explanation": "Valid sequence of brackets"},
                    {"input": "(]", "output": "False", "explanation": "Invalid proper closure"}
                ],
                test_cases=[
                    {"input": "()", "expected_output": "True", "is_hidden": False},
                    {"input": "()[]{}", "expected_output": "True", "is_hidden": False},
                    {"input": "(]", "expected_output": "False", "is_hidden": False},
                    {"input": "([)]", "expected_output": "False", "is_hidden": True},
                    {"input": "{[]}", "expected_output": "True", "is_hidden": True}
                ]
            ),
            DSAProblem(
                title="Maximum Subarray",
                difficulty="intermediate",
                category="arrays",
                problem_statement="Given an integer array, find the contiguous subarray with the largest sum and return that sum. (Kadane's algorithm)\nInput: space-separated integers. Output: integer (max sum)",
                python_signature='def max_subarray(nums: list[int]) -> int:\n    # Write your code here\n    pass\n\nif __name__ == "__main__":\n    import sys\n    nums = list(map(int, sys.stdin.read().split()))\n    print(max_subarray(nums))',
                java_signature='import java.util.*;\n\npublic class Solution {\n    public static int maxSubArray(int[] nums) {\n        // Write your code here\n        return 0;\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextLine()) {\n            String[] parts = sc.nextLine().trim().split("\\\\s+");\n            if (parts.length > 0 && !parts[0].isEmpty()) {\n                int[] nums = new int[parts.length];\n                for (int i=0; i<parts.length; i++) nums[i] = Integer.parseInt(parts[i]);\n                System.out.println(maxSubArray(nums));\n            }\n        }\n    }\n}',
                examples=[
                    {"input": "-2 1 -3 4 -1 2 1 -5 4", "output": "6", "explanation": "[4,-1,2,1] has the largest sum = 6"},
                    {"input": "1", "output": "1", "explanation": "[1] is the only subarray"},
                    {"input": "5 4 -1 7 8", "output": "23", "explanation": "The entire array is the max subarray"}
                ],
                test_cases=[
                    {"input": "-2 1 -3 4 -1 2 1 -5 4", "expected_output": "6", "is_hidden": False},
                    {"input": "1", "expected_output": "1", "is_hidden": False},
                    {"input": "5 4 -1 7 8", "expected_output": "23", "is_hidden": False},
                    {"input": "-1 -2 -3 -4", "expected_output": "-1", "is_hidden": True},
                    {"input": "-5 2 3 -2 5 -1", "expected_output": "8", "is_hidden": True}
                ]
            ),
            DSAProblem(
                title="Merge Two Sorted Arrays",
                difficulty="intermediate",
                category="arrays",
                problem_statement="Given two sorted arrays, return a single merged sorted array.\nInput: first line = array a, second line = array b\nOutput: merged sorted array (space-separated)",
                python_signature='def merge_sorted(a: list[int], b: list[int]) -> list[int]:\n    # Write your code here\n    pass\n\nif __name__ == "__main__":\n    import sys\n    lines = sys.stdin.read().splitlines()\n    a = list(map(int, lines[0].split())) if len(lines) > 0 and lines[0].strip() else []\n    b = list(map(int, lines[1].split())) if len(lines) > 1 and lines[1].strip() else []\n    res = merge_sorted(a, b)\n    if res is not None:\n        print(" ".join(map(str, res)))',
                java_signature='import java.util.*;\n\npublic class Solution {\n    public static int[] mergeSorted(int[] a, int[] b) {\n        // Write your code here\n        return new int[0];\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int[] a = new int[0];\n        int[] b = new int[0];\n        if (sc.hasNextLine()) {\n            String la = sc.nextLine().trim();\n            if (!la.isEmpty()) {\n                String[] pa = la.split("\\\\s+");\n                a = new int[pa.length];\n                for (int i=0; i<pa.length; i++) a[i] = Integer.parseInt(pa[i]);\n            }\n        }\n        if (sc.hasNextLine()) {\n            String lb = sc.nextLine().trim();\n            if (!lb.isEmpty()) {\n                String[] pb = lb.split("\\\\s+");\n                b = new int[pb.length];\n                for (int i=0; i<pb.length; i++) b[i] = Integer.parseInt(pb[i]);\n            }\n        }\n        int[] res = mergeSorted(a, b);\n        if (res != null) {\n            StringBuilder sb = new StringBuilder();\n            for (int i=0; i<res.length; i++) {\n                sb.append(res[i]);\n                if (i < res.length - 1) sb.append(" ");\n            }\n            System.out.println(sb.toString().trim());\n        }\n    }\n}',
                examples=[
                    {"input": "1 2 4\n1 3 4", "output": "1 1 2 3 4 4", "explanation": "Merged maintaining sorted order"},
                    {"input": "\n0", "output": "0", "explanation": "First array is empty"},
                    {"input": "2\n1", "output": "1 2", "explanation": "Merged and sorted"}
                ],
                test_cases=[
                    {"input": "1 2 4\n1 3 4", "expected_output": "1 1 2 3 4 4", "is_hidden": False},
                    {"input": "\n0", "expected_output": "0", "is_hidden": False},
                    {"input": "2\n1", "expected_output": "1 2", "is_hidden": False},
                    {"input": "5 6 7\n1 2 3", "expected_output": "1 2 3 5 6 7", "is_hidden": True},
                    {"input": "\n", "expected_output": "", "is_hidden": True}
                ]
            ),
            DSAProblem(
                title="Climbing Stairs",
                difficulty="intermediate",
                category="dp",
                problem_statement="You are climbing a staircase. Each time you can climb 1 or 2 steps. Given n steps, how many distinct ways can you reach the top?\nInput: integer n. Output: integer (number of ways)",
                python_signature='def climb_stairs(n: int) -> int:\n    # Write your code here\n    pass\n\nif __name__ == "__main__":\n    import sys\n    n = int(sys.stdin.read().strip())\n    print(climb_stairs(n))',
                java_signature='import java.util.*;\n\npublic class Solution {\n    public static int climbStairs(int n) {\n        // Write your code here\n        return 0;\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextInt()) {\n            int n = sc.nextInt();\n            System.out.println(climbStairs(n));\n        }\n    }\n}',
                examples=[
                    {"input": "2", "output": "2", "explanation": "1 step + 1 step, or 2 steps"},
                    {"input": "3", "output": "3", "explanation": "1+1+1, 1+2, 2+1"},
                    {"input": "1", "output": "1", "explanation": "Only 1 step"}
                ],
                test_cases=[
                    {"input": "2", "expected_output": "2", "is_hidden": False},
                    {"input": "3", "expected_output": "3", "is_hidden": False},
                    {"input": "1", "expected_output": "1", "is_hidden": False},
                    {"input": "4", "expected_output": "5", "is_hidden": True},
                    {"input": "10", "expected_output": "89", "is_hidden": True}
                ]
            ),
            DSAProblem(
                title="Number of Islands",
                difficulty="intermediate",
                category="graphs",
                problem_statement="Given a 2D grid of '1' (land) and '0' (water), count the number of islands. An island is surrounded by water and formed by connecting adjacent lands horizontally/vertically.\nInput: rows of space-separated characters (1 or 0)\nOutput: integer (number of islands)",
                python_signature='def num_islands(grid: list[list[str]]) -> int:\n    # Write your code here\n    pass\n\nif __name__ == "__main__":\n    import sys\n    grid = [line.split() for line in sys.stdin.read().splitlines() if line.strip()]\n    print(num_islands(grid))',
                java_signature='import java.util.*;\n\npublic class Solution {\n    public static int numIslands(char[][] grid) {\n        // Write your code here\n        return 0;\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        List<char[]> list = new ArrayList<>();\n        while (sc.hasNextLine()) {\n            String line = sc.nextLine().trim();\n            if (line.isEmpty()) continue;\n            String[] parts = line.split("\\\\s+");\n            char[] row = new char[parts.length];\n            for (int i=0; i<parts.length; i++) {\n                row[i] = parts[i].charAt(0);\n            }\n            list.add(row);\n        }\n        char[][] grid = list.toArray(new char[0][0]);\n        System.out.println(numIslands(grid));\n    }\n}',
                examples=[
                    {"input": "1 1 1 1 0\n1 1 0 1 0\n1 1 0 0 0\n0 0 0 0 0", "output": "1", "explanation": "One large connected island"},
                    {"input": "1 1 0 0 0\n1 1 0 0 0\n0 0 1 0 0\n0 0 0 1 1", "output": "3", "explanation": "Three distinct islands"},
                    {"input": "0 0\n0 0", "output": "0", "explanation": "No islands"}
                ],
                test_cases=[
                    {"input": "1 1 1 1 0\n1 1 0 1 0\n1 1 0 0 0\n0 0 0 0 0", "expected_output": "1", "is_hidden": False},
                    {"input": "1 1 0 0 0\n1 1 0 0 0\n0 0 1 0 0\n0 0 0 1 1", "expected_output": "3", "is_hidden": False},
                    {"input": "0 0\n0 0", "expected_output": "0", "is_hidden": False},
                    {"input": "1 0 1\n0 1 0\n1 0 1", "expected_output": "5", "is_hidden": True},
                    {"input": "1 1 1\n0 0 1\n1 1 1", "expected_output": "1", "is_hidden": True}
                ]
            ),
            DSAProblem(
                title="Longest Increasing Subsequence",
                difficulty="advanced",
                category="dp",
                problem_statement="Given an integer array, return the length of the longest strictly increasing subsequence.\nInput: space-separated integers. Output: integer (LIS length)",
                python_signature='def length_of_lis(nums: list[int]) -> int:\n    # Write your code here\n    pass\n\nif __name__ == "__main__":\n    import sys\n    data = sys.stdin.read().split()\n    if data:\n        nums = list(map(int, data))\n        print(length_of_lis(nums))\n    else:\n        print(0)',
                java_signature='import java.util.*;\n\npublic class Solution {\n    public static int lengthOfLIS(int[] nums) {\n        // Write your code here\n        return 0;\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextLine()) {\n            String line = sc.nextLine().trim();\n            if (line.isEmpty()) {\n                System.out.println(0);\n                return;\n            }\n            String[] parts = line.split("\\\\s+");\n            int[] nums = new int[parts.length];\n            for (int i=0; i<parts.length; i++) nums[i] = Integer.parseInt(parts[i]);\n            System.out.println(lengthOfLIS(nums));\n        }\n    }\n}',
                examples=[
                    {"input": "10 9 2 5 3 7 101 18", "output": "4", "explanation": "The LIS is [2, 3, 7, 101], length is 4."},
                    {"input": "0 1 0 3 2 3", "output": "4", "explanation": "The LIS is [0, 1, 2, 3]"},
                    {"input": "7 7 7 7 7 7 7", "output": "1", "explanation": "Strictly increasing means length 1"}
                ],
                test_cases=[
                    {"input": "10 9 2 5 3 7 101 18", "expected_output": "4", "is_hidden": False},
                    {"input": "0 1 0 3 2 3", "expected_output": "4", "is_hidden": False},
                    {"input": "7 7 7 7 7 7 7", "expected_output": "1", "is_hidden": False},
                    {"input": "1 3 6 7 9 4 10 5 6", "expected_output": "6", "is_hidden": True},
                    {"input": "5 4 3 2 1", "expected_output": "1", "is_hidden": True}
                ]
            ),
            DSAProblem(
                title="Word Break",
                difficulty="advanced",
                category="dp",
                problem_statement="Given a string s and a list of words (the dictionary), return True if s can be segmented into one or more dictionary words, else False.\nInput: first line = string s, second line = space-separated words\nOutput: True or False",
                python_signature='def word_break(s: str, word_dict: list[str]) -> bool:\n    # Write your code here\n    pass\n\nif __name__ == "__main__":\n    import sys\n    lines = sys.stdin.read().splitlines()\n    if len(lines) >= 2:\n        s = lines[0].strip()\n        word_dict = lines[1].split()\n        print(word_break(s, word_dict))',
                java_signature='import java.util.*;\n\npublic class Solution {\n    public static boolean wordBreak(String s, List<String> wordDict) {\n        // Write your code here\n        return false;\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextLine()) {\n            String s = sc.nextLine().trim();\n            if (sc.hasNextLine()) {\n                String[] w = sc.nextLine().trim().split("\\\\s+");\n                List<String> wd = Arrays.asList(w);\n                System.out.println(wordBreak(s, wd) ? "True" : "False");\n            }\n        }\n    }\n}',
                examples=[
                    {"input": "leetcode\nleet code", "output": "True", "explanation": "'leetcode' can be segmented as 'leet code'."},
                    {"input": "applepenapple\napple pen", "output": "True", "explanation": "'applepenapple' can be segmented as 'apple pen apple'."},
                    {"input": "catsandog\ncats dog sand and cat", "output": "False", "explanation": "'catsandog' cannot be segmented."}
                ],
                test_cases=[
                    {"input": "leetcode\nleet code", "expected_output": "True", "is_hidden": False},
                    {"input": "applepenapple\napple pen", "expected_output": "True", "is_hidden": False},
                    {"input": "catsandog\ncats dog sand and cat", "expected_output": "False", "is_hidden": False},
                    {"input": "cars\ncar ca rs", "expected_output": "True", "is_hidden": True},
                    {"input": "aaaaaaa\naaaa aa", "expected_output": "False", "is_hidden": True}
                ]
            )
        ]
        
        session.add_all(problems)
        await session.commit()
