import logging
from backend.database import get_db_connection
from backend.services.skill_extractor import determine_level, get_difficulty

logger = logging.getLogger("skillmatch")

QUESTION_BANK = [
    # ==================== LEVEL 1 (Medium) ====================

    # --- Python Theory (3 for L1) ---
    {"skill": "Python", "type": "theory", "level": "Level 1",
     "question": "What is the difference between a list and a tuple in Python?",
     "correct_answer": "Lists are mutable, tuples are immutable"},
    {"skill": "Python", "type": "theory", "level": "Level 1",
     "question": "What is a dictionary in Python?",
     "correct_answer": "An unordered collection of key-value pairs"},
    {"skill": "Python", "type": "theory", "level": "Level 1",
     "question": "What is a lambda function in Python?",
     "correct_answer": "An anonymous function defined with the lambda keyword that can take any number of arguments but has a single expression"},

    # --- Python MCQ (2 for L1) ---
    {"skill": "Python", "type": "mcq", "level": "Level 1",
     "question": "Which keyword is used to define a function in Python?",
     "option_a": "function", "option_b": "def", "option_c": "func", "option_d": "lambda",
     "correct_answer": "B"},
    {"skill": "Python", "type": "mcq", "level": "Level 1",
     "question": "Which of the following is NOT a Python data type?",
     "option_a": "list", "option_b": "tuple", "option_c": "array", "option_d": "dict",
     "correct_answer": "C"},

    # --- Python Code Output (2 for L1) ---
    {"skill": "Python", "type": "code_output", "level": "Level 1",
     "question": "What is the output of the following code?\n\nx = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)",
     "correct_answer": "[1, 2, 3, 4]"},
    {"skill": "Python", "type": "code_output", "level": "Level 1",
     "question": "What is the output of the following code?\n\nprint([i**2 for i in range(4)])",
     "correct_answer": "[0, 1, 4, 9]"},

    # --- Python Debugging (2 for L1) ---
    {"skill": "Python", "type": "debugging", "level": "Level 1",
     "question": "Find and fix the error in the following code:\n\ndef add(a, b)\n    return a + b",
     "correct_answer": "Missing colon after the function signature: def add(a, b):"},
    {"skill": "Python", "type": "debugging", "level": "Level 1",
     "question": "Find and fix the error in the following code:\n\nfor i in range(5)\n    print(i)",
     "correct_answer": "Missing colon after range(5): for i in range(5):"},

    # --- Python Coding (2 for L1) ---
    {"skill": "Python", "type": "coding", "level": "Level 1",
     "question": "Write a Python function to check if a string is a palindrome.\n\nExample Input: 'radar'\nExample Output: True",
     "reference_code": "def is_palindrome(s):\n    return s == s[::-1]\n\nprint(is_palindrome('radar'))",
     "expected_output": "True", "test_input": "radar"},
    {"skill": "Python", "type": "coding", "level": "Level 1",
     "question": "Write a Python function to count the number of vowels in a string.\n\nExample Input: 'hello world'\nExample Output: 3",
     "reference_code": "def count_vowels(s):\n    return sum(1 for c in s.lower() if c in 'aeiou')\n\nprint(count_vowels('hello world'))",
     "expected_output": "3", "test_input": "hello world"},

    # --- HTML Theory (2 for L1) ---
    {"skill": "HTML", "type": "theory", "level": "Level 1",
     "question": "What is the purpose of the HTML <form> element?",
     "correct_answer": "It collects user input through form controls like text fields, checkboxes, and buttons"},
    {"skill": "HTML", "type": "theory", "level": "Level 1",
     "question": "What is the difference between inline and block-level elements in HTML?",
     "correct_answer": "Inline elements do not start a new line and only take necessary width, block-level elements start on a new line and take full width"},

    # --- HTML MCQ (1 for L1) ---
    {"skill": "HTML", "type": "mcq", "level": "Level 1",
     "question": "Which HTML tag is used to create a hyperlink?",
     "option_a": "<link>", "option_b": "<a>", "option_c": "<href>", "option_d": "<url>",
     "correct_answer": "B"},

    # --- HTML Coding (1 for L1) ---
    {"skill": "HTML", "type": "coding", "level": "Level 1",
     "question": "Write HTML for a simple contact form with a name field, email field, and a submit button.",
     "reference_code": "<form>\n  <input type=\"text\" name=\"name\" placeholder=\"Name\">\n  <input type=\"email\" name=\"email\" placeholder=\"Email\">\n  <button type=\"submit\">Submit</button>\n</form>",
     "expected_output": "form with name input email input and submit button", "test_input": ""},

    # --- CSS Theory (2 for L1) ---
    {"skill": "CSS", "type": "theory", "level": "Level 1",
     "question": "What is the CSS box model?",
     "correct_answer": "The CSS box model consists of content, padding, border, and margin layers around every HTML element"},
    {"skill": "CSS", "type": "theory", "level": "Level 1",
     "question": "What is the difference between margin and padding in CSS?",
     "correct_answer": "Margin is the space outside an element's border, padding is the space between the content and the border"},

    # --- CSS MCQ (1 for L1) ---
    {"skill": "CSS", "type": "mcq", "level": "Level 1",
     "question": "Which CSS property controls the text size?",
     "option_a": "text-size", "option_b": "font-size", "option_c": "text-style", "option_d": "font-style",
     "correct_answer": "B"},

    # --- CSS Code Output (1 for L1) ---
    {"skill": "CSS", "type": "code_output", "level": "Level 1",
     "question": "What does this CSS rule do?\n\ndiv { display: flex; justify-content: center; }",
     "correct_answer": "It centers the flex items horizontally inside the div"},

    # --- CSS Coding (1 for L1) ---
    {"skill": "CSS", "type": "coding", "level": "Level 1",
     "question": "Write CSS to create a centered card with a border radius of 12px, padding of 20px, and a light gray (#f5f5f5) background.",
     "reference_code": ".card {\n  margin: 0 auto;\n  border-radius: 12px;\n  padding: 20px;\n  background: #f5f5f5;\n}",
     "expected_output": "centered card with border-radius 12px", "test_input": ""},

    # --- JavaScript Theory (2 for L1) ---
    {"skill": "JavaScript", "type": "theory", "level": "Level 1",
     "question": "What is the DOM in JavaScript?",
     "correct_answer": "The Document Object Model, a tree-like representation of an HTML document that JavaScript can manipulate"},
    {"skill": "JavaScript", "type": "theory", "level": "Level 1",
     "question": "What is the difference between let and var in JavaScript?",
     "correct_answer": "let is block-scoped while var is function-scoped, and let does not allow redeclaration in the same scope"},

    # --- JavaScript MCQ (1 for L1) ---
    {"skill": "JavaScript", "type": "mcq", "level": "Level 1",
     "question": "Which keyword declares a block-scoped variable in JavaScript?",
     "option_a": "var", "option_b": "let", "option_c": "function", "option_d": "static",
     "correct_answer": "B"},

    # --- JavaScript Code Output (1 for L1) ---
    {"skill": "JavaScript", "type": "code_output", "level": "Level 1",
     "question": "What is the output of the following code?\n\nconsole.log(typeof null)",
     "correct_answer": "object"},

    # --- JavaScript Coding (1 for L1) ---
    {"skill": "JavaScript", "type": "coding", "level": "Level 1",
     "question": "Write a JavaScript function to reverse a string.\n\nExample Input: 'hello'\nExample Output: 'olleh'",
     "reference_code": "function reverseString(str) {\n  return str.split('').reverse().join('');\n}\nconsole.log(reverseString('hello'));",
     "expected_output": "olleh", "test_input": "hello"},

    # --- MySQL Theory (2 for L1) ---
    {"skill": "MySQL", "type": "theory", "level": "Level 1",
     "question": "What is a primary key in MySQL?",
     "correct_answer": "A column that uniquely identifies each row in a table"},
    {"skill": "MySQL", "type": "theory", "level": "Level 1",
     "question": "What is the difference between WHERE and HAVING in SQL?",
     "correct_answer": "WHERE filters rows before grouping, HAVING filters groups after GROUP BY"},

    # --- MySQL MCQ (1 for L1) ---
    {"skill": "MySQL", "type": "mcq", "level": "Level 1",
     "question": "Which SQL clause is used to filter results?",
     "option_a": "ORDER BY", "option_b": "WHERE", "option_c": "GROUP BY", "option_d": "HAVING",
     "correct_answer": "B"},

    # --- MySQL Code Output (1 for L1) ---
    {"skill": "MySQL", "type": "code_output", "level": "Level 1",
     "question": "What does this query return?\n\nSELECT COUNT(*) FROM employees WHERE salary > 50000;",
     "correct_answer": "The number of employees with a salary greater than 50000"},

    # --- MySQL Coding (1 for L1) ---
    {"skill": "MySQL", "type": "coding", "level": "Level 1",
     "question": "Write a SQL query to select all employees with a salary greater than 50000, ordered by salary descending.\n\nTable: employees (id, name, salary)",
     "reference_code": "SELECT * FROM employees WHERE salary > 50000 ORDER BY salary DESC;",
     "expected_output": "SELECT * FROM employees WHERE salary > 50000 ORDER BY salary DESC;", "test_input": ""},

    # --- SQL Theory (2 for L1) ---
    {"skill": "SQL", "type": "theory", "level": "Level 1",
     "question": "What is a foreign key?",
     "correct_answer": "A column that references the primary key of another table to establish a relationship"},
    {"skill": "SQL", "type": "theory", "level": "Level 1",
     "question": "What is the difference between TRUNCATE and DELETE in SQL?",
     "correct_answer": "TRUNCATE removes all rows quickly without logging individual deletions and cannot be rolled back, DELETE removes rows conditionally and can be rolled back"},

    # --- SQL MCQ (1 for L1) ---
    {"skill": "SQL", "type": "mcq", "level": "Level 1",
     "question": "Which SQL statement is used to insert new data into a table?",
     "option_a": "ADD", "option_b": "INSERT INTO", "option_c": "CREATE", "option_d": "UPDATE",
     "correct_answer": "B"},

    # --- SQL Coding (3 for L1) ---
    {"skill": "SQL", "type": "coding", "level": "Level 1",
     "question": "Write a SQL query to find the second highest salary from an employees table.\n\nTable: employees (id, name, salary)",
     "reference_code": "SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees);",
     "expected_output": "SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees);", "test_input": ""},
    {"skill": "SQL", "type": "coding", "level": "Level 1",
     "question": "Write a SQL query to select all columns from a table named 'students' where the age is greater than 18.\n\nTable: students (id, name, age)",
     "reference_code": "SELECT * FROM students WHERE age > 18;",
     "expected_output": "SELECT * FROM students WHERE age > 18;", "test_input": ""},
    {"skill": "SQL", "type": "coding", "level": "Level 1",
     "question": "Write a SQL query to find the maximum salary from an employees table.\n\nTable: employees (id, name, salary)",
     "reference_code": "SELECT MAX(salary) FROM employees;",
     "expected_output": "SELECT MAX(salary) FROM employees;", "test_input": ""},

    # ==================== LEVEL 2 (Hard) ====================

    # --- Python Theory (3 for L2) ---
    {"skill": "Python", "type": "theory", "level": "Level 2",
     "question": "Explain the difference between deepcopy and shallow copy in Python.",
     "correct_answer": "deepcopy recursively copies all nested objects, shallow copy creates a new container but references the same nested objects"},
    {"skill": "Python", "type": "theory", "level": "Level 2",
     "question": "Explain what decorators are in Python and how they work.",
     "correct_answer": "Decorators are functions that take another function as an argument and extend its behavior without modifying it, using the @ syntax"},
    {"skill": "Python", "type": "theory", "level": "Level 2",
     "question": "What is the purpose of the 'self' parameter in Python class methods?",
     "correct_answer": "It refers to the current instance of the class and allows access to instance attributes and methods"},

    # --- Python MCQ (2 for L2) ---
    {"skill": "Python", "type": "mcq", "level": "Level 2",
     "question": "What does the 'is' operator check in Python?",
     "option_a": "Value equality", "option_b": "Object identity (same memory location)",
     "option_c": "Type compatibility", "option_d": "Hash equality",
     "correct_answer": "B"},
    {"skill": "Python", "type": "mcq", "level": "Level 2",
     "question": "What is the output of: print(type(lambda x: x))?",
     "option_a": "<class 'function'>", "option_b": "<class 'method'>", "option_c": "<class 'lambda'>", "option_d": "<class 'object'>",
     "correct_answer": "A"},

    # --- Python Code Output (2 for L2) ---
    {"skill": "Python", "type": "code_output", "level": "Level 2",
     "question": "What is the output of the following code?\n\nprint([i**2 for i in range(4)])",
     "correct_answer": "[0, 1, 4, 9]"},
    {"skill": "Python", "type": "code_output", "level": "Level 2",
     "question": "What is the output of the following code?\n\nx = {'a': 1, 'b': 2}\nprint(list(x.keys()))",
     "correct_answer": "['a', 'b']"},

    # --- Python Debugging (2 for L2) ---
    {"skill": "Python", "type": "debugging", "level": "Level 2",
     "question": "Find and fix the error in the following code:\n\nnums = [1, 2, 3]\nprint(nums[3])",
     "correct_answer": "Index out of range: the list has indices 0, 1, 2. The max valid index is 2, not 3"},
    {"skill": "Python", "type": "debugging", "level": "Level 2",
     "question": "Find and fix the error in the following code:\n\nclass Dog:\n    def __init(self, name):\n        self.name = name\n\nd = Dog('Rex')",
     "correct_answer": "The method name should be __init__ (double underscore on both sides), not __init"},

    # --- Python Coding (2 for L2) ---
    {"skill": "Python", "type": "coding", "level": "Level 2",
     "question": "Write a Python function to find the factorial of a number using recursion.\n\nExample Input: 5\nExample Output: 120",
     "reference_code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n\nprint(factorial(5))",
     "expected_output": "120", "test_input": "5"},
    {"skill": "Python", "type": "coding", "level": "Level 2",
     "question": "Write a Python function to merge two sorted lists into a single sorted list.\n\nExample Input: [1, 3, 5], [2, 4, 6]\nExample Output: [1, 2, 3, 4, 5, 6]",
     "reference_code": "def merge_sorted(a, b):\n    result = []\n    i = j = 0\n    while i < len(a) and j < len(b):\n        if a[i] <= b[j]:\n            result.append(a[i]); i += 1\n        else:\n            result.append(b[j]); j += 1\n    result.extend(a[i:])\n    result.extend(b[j:])\n    return result\n\nprint(merge_sorted([1, 3, 5], [2, 4, 6]))",
     "expected_output": "[1, 2, 3, 4, 5, 6]", "test_input": "[1, 3, 5], [2, 4, 6]"},

    # --- HTML Theory (2 for L2) ---
    {"skill": "HTML", "type": "theory", "level": "Level 2",
     "question": "Explain the difference between GET and POST methods in HTML forms.",
     "correct_answer": "GET appends form data to the URL and is visible, POST sends data in the request body and is not visible in the URL"},
    {"skill": "HTML", "type": "theory", "level": "Level 2",
     "question": "What is the purpose of the HTML5 semantic tags like header, nav, section, and footer?",
     "correct_answer": "They provide meaningful structure to web pages, improving accessibility and SEO by describing the content's role"},

    # --- HTML MCQ (1 for L2) ---
    {"skill": "HTML", "type": "mcq", "level": "Level 2",
     "question": "Which input type creates a date picker in HTML5?",
     "option_a": "type='calendar'", "option_b": "type='date'", "option_c": "type='datepicker'", "option_d": "type='datetime'",
     "correct_answer": "B"},

    # --- CSS Theory (2 for L2) ---
    {"skill": "CSS", "type": "theory", "level": "Level 2",
     "question": "Explain the difference between position: relative and position: absolute in CSS.",
     "correct_answer": "position: relative offsets from the element's normal position, position: absolute offsets from the nearest positioned ancestor"},
    {"skill": "CSS", "type": "theory", "level": "Level 2",
     "question": "What is CSS specificity and how is it calculated?",
     "correct_answer": "Specificity determines which CSS rule applies when multiple rules target the same element, calculated from inline styles, IDs, classes, and element selectors"},

    # --- CSS MCQ (1 for L2) ---
    {"skill": "CSS", "type": "mcq", "level": "Level 2",
     "question": "Which CSS property is used to create space between elements in a flex container?",
     "option_a": "gap", "option_b": "spacing", "option_c": "margin-gap", "option_d": "flex-spacing",
     "correct_answer": "A"},

    # --- CSS Code Output (1 for L2) ---
    {"skill": "CSS", "type": "code_output", "level": "Level 2",
     "question": "What does this CSS rule do?\n\ndiv { display: flex; flex-direction: column; }",
     "correct_answer": "It arranges the flex items vertically in a column inside the div"},

    # --- CSS Coding (1 for L2) ---
    {"skill": "CSS", "type": "coding", "level": "Level 2",
     "question": "Write CSS for a responsive grid that displays 3 columns on desktop and 1 column on mobile (max-width 600px).",
     "reference_code": ".grid {\n  display: grid;\n  grid-template-columns: repeat(3, 1fr);\n}\n@media (max-width: 600px) {\n  .grid {\n    grid-template-columns: 1fr;\n  }\n}",
     "expected_output": "responsive grid with 3 columns desktop 1 column mobile", "test_input": ""},

    # --- JavaScript Theory (2 for L2) ---
    {"skill": "JavaScript", "type": "theory", "level": "Level 2",
     "question": "Explain the difference between == and === in JavaScript.",
     "correct_answer": "== compares values with type coercion, === compares both value and type without coercion (strict equality)"},
    {"skill": "JavaScript", "type": "theory", "level": "Level 2",
     "question": "What is a closure in JavaScript?",
     "correct_answer": "A closure is a function that retains access to variables from its outer scope even after the outer function has returned"},

    # --- JavaScript MCQ (1 for L2) ---
    {"skill": "JavaScript", "type": "mcq", "level": "Level 2",
     "question": "What is the output of: console.log([1, 2, 3].map(x => x * 2))?",
     "option_a": "[1, 2, 3]", "option_b": "[2, 4, 6]", "option_c": "[1, 4, 9]", "option_d": "[2, 3, 6]",
     "correct_answer": "B"},

    # --- JavaScript Code Output (1 for L2) ---
    {"skill": "JavaScript", "type": "code_output", "level": "Level 2",
     "question": "What is the output of the following code?\n\nconsole.log([1,2,3].map(x => x * 2))",
     "correct_answer": "[2, 4, 6]"},

    # --- JavaScript Coding (1 for L2) ---
    {"skill": "JavaScript", "type": "coding", "level": "Level 2",
     "question": "Write a JavaScript function to find the largest number in an array.\n\nExample Input: [3, 7, 2, 8, 1]\nExample Output: 8",
     "reference_code": "function findLargest(arr) {\n  return Math.max(...arr);\n}\nconsole.log(findLargest([3, 7, 2, 8, 1]));",
     "expected_output": "8", "test_input": "[3, 7, 2, 8, 1]"},

    # --- MySQL Theory (2 for L2) ---
    {"skill": "MySQL", "type": "theory", "level": "Level 2",
     "question": "Explain the difference between INNER JOIN and LEFT JOIN.",
     "correct_answer": "INNER JOIN returns only rows that match in both tables, LEFT JOIN returns all rows from the left table and matching rows from the right table"},
    {"skill": "MySQL", "type": "theory", "level": "Level 2",
     "question": "What is database normalization and why is it important?",
     "correct_answer": "Normalization is the process of organizing data to reduce redundancy and improve data integrity by dividing tables into smaller related tables"},

    # --- MySQL MCQ (1 for L2) ---
    {"skill": "MySQL", "type": "mcq", "level": "Level 2",
     "question": "What is the difference between INNER JOIN and LEFT JOIN?",
     "option_a": "INNER JOIN returns all rows from both tables",
     "option_b": "INNER JOIN returns only matching rows, LEFT JOIN returns all rows from the left table plus matching rows from the right",
     "option_c": "LEFT JOIN returns only matching rows",
     "option_d": "There is no difference",
     "correct_answer": "B"},

    # --- MySQL Code Output (1 for L2) ---
    {"skill": "MySQL", "type": "code_output", "level": "Level 2",
     "question": "What does this query return?\n\nSELECT AVG(salary) FROM employees;",
     "correct_answer": "The average salary of all employees"},

    # --- MySQL Coding (1 for L2) ---
    {"skill": "MySQL", "type": "coding", "level": "Level 2",
     "question": "Write a SQL query to find the names of employees who earn more than the average salary.\n\nTable: employees (id, name, salary)",
     "reference_code": "SELECT name FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);",
     "expected_output": "SELECT name FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);", "test_input": ""},

    # --- SQL Theory (2 for L2) ---
    {"skill": "SQL", "type": "theory", "level": "Level 2",
     "question": "What is a database index and why is it used?",
     "correct_answer": "An index is a data structure that improves the speed of data retrieval operations on a database table"},
    {"skill": "SQL", "type": "theory", "level": "Level 2",
     "question": "What is the difference between a clustered and non-clustered index?",
     "correct_answer": "A clustered index determines the physical order of data in a table, a non-clustered index is a separate structure that points to the data rows"},

    # --- SQL MCQ (1 for L2) ---
    {"skill": "SQL", "type": "mcq", "level": "Level 2",
     "question": "Which SQL keyword is used to combine rows from two or more tables based on a related column?",
     "option_a": "MERGE", "option_b": "JOIN", "option_c": "COMBINE", "option_d": "UNION",
     "correct_answer": "B"},

    # --- SQL Coding (3 for L2) ---
    {"skill": "SQL", "type": "coding", "level": "Level 2",
     "question": "Write a SQL query to count the number of employees in each department, ordered by count descending.\n\nTable: employees (id, name, department)",
     "reference_code": "SELECT department, COUNT(*) as count FROM employees GROUP BY department ORDER BY count DESC;",
     "expected_output": "SELECT department, COUNT(*) as count FROM employees GROUP BY department ORDER BY count DESC;", "test_input": ""},
    {"skill": "SQL", "type": "coding", "level": "Level 2",
     "question": "Write a SQL query using JOIN to display employee names along with their department names.\n\nTables: employees (id, name, department_id), departments (id, name)",
     "reference_code": "SELECT e.name, d.name FROM employees e JOIN departments d ON e.department_id = d.id;",
     "expected_output": "SELECT e.name, d.name FROM employees e JOIN departments d ON e.department_id = d.id;", "test_input": ""},
    {"skill": "SQL", "type": "coding", "level": "Level 2",
     "question": "Write a SQL query to find employees who have the same salary as at least one other employee.\n\nTable: employees (id, name, salary)",
     "reference_code": "SELECT name FROM employees WHERE salary IN (SELECT salary FROM employees GROUP BY salary HAVING COUNT(*) > 1);",
     "expected_output": "SELECT name FROM employees WHERE salary IN (SELECT salary FROM employees GROUP BY salary HAVING COUNT(*) > 1);", "test_input": ""},

    # ==================== ADDITIONAL DEBUGGING QUESTIONS ====================

    # --- HTML Debugging (1 for L1) ---
    {"skill": "HTML", "type": "debugging", "level": "Level 1",
     "question": "Find and fix the error in the following HTML:\n\n<a href='home.html'>Home</a><img src='logo.png'>",
     "correct_answer": "The img tag is missing the alt attribute: <img src='logo.png' alt='Logo'>"},

    # --- CSS Debugging (1 for L1) ---
    {"skill": "CSS", "type": "debugging", "level": "Level 1",
     "question": "Find and fix the error in the following CSS:\n\n.container {\n  display: flex\n  justify-content: center;\n}",
     "correct_answer": "Missing semicolon after 'display: flex': display: flex;"},

    # --- JavaScript Debugging (1 for L1) ---
    {"skill": "JavaScript", "type": "debugging", "level": "Level 1",
     "question": "Find and fix the error in the following code:\n\nlet arr = [1, 2, 3]\narr.lenght",
     "correct_answer": "Typo: 'lenght' should be 'length': arr.length"},

    # --- HTML Debugging (1 for L2) ---
    {"skill": "HTML", "type": "debugging", "level": "Level 2",
     "question": "Find and fix the error in the following HTML:\n\n<input type='text' name='username' required>\n<button>Submit</form>",
     "correct_answer": "The closing tag should be </button> not </form>: <button>Submit</button>"},

    # --- CSS Debugging (1 for L2) ---
    {"skill": "CSS", "type": "debugging", "level": "Level 2",
     "question": "Find and fix the error in the following CSS:\n\n@media max-width: 600px {\n  .container { width: 100%; }\n}",
     "correct_answer": "Missing parentheses in the media query: @media (max-width: 600px)"},

    # --- JavaScript Debugging (1 for L2) ---
    {"skill": "JavaScript", "type": "debugging", "level": "Level 2",
     "question": "Find and fix the error in the following code:\n\nconst obj = {a: 1};\nconsole.log(obj.b.c);",
     "correct_answer": "Cannot read property 'c' of undefined: obj.b is undefined. Check if obj.b exists first: console.log(obj.b?.c)"},

    # --- MySQL Debugging (1 for L1) ---
    {"skill": "MySQL", "type": "debugging", "level": "Level 1",
     "question": "Find and fix the error in the following SQL:\n\nSELECT * FROM employees WHERE salary > 50000 ORDER salary DESC;",
     "correct_answer": "Missing BY keyword after ORDER: ORDER BY salary DESC"},

    # --- MySQL Debugging (1 for L2) ---
    {"skill": "MySQL", "type": "debugging", "level": "Level 2",
     "question": "Find and fix the error in the following SQL:\n\nSELECT name, COUNT(*) FROM employees GROUP name;",
     "correct_answer": "Missing BY keyword after GROUP: GROUP BY name"},

    # ==================== ADDITIONAL CODING QUESTIONS (to meet 6 per level) ====================

    # --- Level 1 extra coding (need 1 more to reach 6) ---
    {"skill": "Python", "type": "coding", "level": "Level 1",
     "question": "Write a Python function to find the maximum element in a list without using the max() function.\n\nExample Input: [3, 1, 4, 1, 5, 9, 2, 6]\nExample Output: 9",
     "reference_code": "def find_max(lst):\n    m = lst[0]\n    for x in lst:\n        if x > m:\n            m = x\n    return m\n\nprint(find_max([3, 1, 4, 1, 5, 9, 2, 6]))",
     "expected_output": "9", "test_input": "[3, 1, 4, 1, 5, 9, 2, 6]"},

    # --- Level 2 extra coding (need 2 more to reach 6) ---
    {"skill": "Python", "type": "coding", "level": "Level 2",
     "question": "Write a Python function to check if a number is prime.\n\nExample Input: 7\nExample Output: True",
     "reference_code": "def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\nprint(is_prime(7))",
     "expected_output": "True", "test_input": "7"},
    {"skill": "JavaScript", "type": "coding", "level": "Level 2",
     "question": "Write a JavaScript function to check if a string is a palindrome.\n\nExample Input: 'racecar'\nExample Output: true",
     "reference_code": "function isPalindrome(str) {\n  return str === str.split('').reverse().join('');\n}\nconsole.log(isPalindrome('racecar'));",
     "expected_output": "true", "test_input": "racecar"},
]

JOB_ROLES = [
    {"name": "Python Developer", "skills": [
        {"skill": "Python", "weight": 3.0},
        {"skill": "MySQL", "weight": 1.5},
        {"skill": "Problem Solving", "weight": 1.0},
        {"skill": "DSA", "weight": 1.0},
        {"skill": "Backend Basics", "weight": 1.0},
    ]},
    {"name": "Frontend Developer", "skills": [
        {"skill": "HTML", "weight": 2.0},
        {"skill": "CSS", "weight": 2.0},
        {"skill": "JavaScript", "weight": 2.5},
        {"skill": "Responsive Design", "weight": 1.0},
        {"skill": "DOM", "weight": 1.0},
    ]},
    {"name": "Backend Developer", "skills": [
        {"skill": "Python", "weight": 2.0},
        {"skill": "FastAPI", "weight": 1.5},
        {"skill": "MySQL", "weight": 1.5},
        {"skill": "REST API", "weight": 1.5},
        {"skill": "Database", "weight": 1.0},
    ]},
    {"name": "Full Stack Developer", "skills": [
        {"skill": "HTML", "weight": 1.5},
        {"skill": "CSS", "weight": 1.5},
        {"skill": "JavaScript", "weight": 1.5},
        {"skill": "Python", "weight": 1.5},
        {"skill": "Database", "weight": 1.0},
        {"skill": "REST API", "weight": 1.0},
    ]},
]

QUESTION_DISTRIBUTION = {
    "theory": 8,
    "mcq": 6,
    "code_output": 4,
    "debugging": 3,
    "coding": 6,
    "sql": 3,
}


def seed_questions():
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM assessment_questions")
        conn.execute("DELETE FROM answers")
        conn.execute("DELETE FROM results")
        conn.execute("DELETE FROM skill_scores")
        conn.execute("DELETE FROM skill_matches")
        conn.execute("DELETE FROM questions")
        for q in QUESTION_BANK:
            conn.execute(
                """INSERT INTO questions (skill, type, level, question, option_a, option_b, option_c, option_d,
                   correct_answer, reference_code, test_input, expected_output, points)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (q["skill"], q["type"], q["level"], q["question"],
                 q.get("option_a"), q.get("option_b"), q.get("option_c"), q.get("option_d"),
                 q.get("correct_answer"), q.get("reference_code"), q.get("test_input"),
                 q.get("expected_output"), 1),
            )
        conn.commit()
    finally:
        conn.close()


def seed_job_roles():
    conn = get_db_connection()
    try:
        existing = conn.execute("SELECT COUNT(*) as c FROM job_roles").fetchone()["c"]
        if existing == 0:
            for role in JOB_ROLES:
                conn.execute("INSERT INTO job_roles (name) VALUES (%s)", (role["name"],))
                role_id = conn.execute("SELECT id FROM job_roles WHERE name = %s", (role["name"],)).fetchone()["id"]
                for s in role["skills"]:
                    conn.execute("INSERT INTO job_role_skills (role_id, skill, weight) VALUES (%s, %s, %s)",
                                 (role_id, s["skill"], s["weight"]))
            conn.commit()
    finally:
        conn.close()


def seed_skills():
    conn = get_db_connection()
    try:
        from backend.services.skill_extractor import SKILL_CATEGORIES
        existing = conn.execute("SELECT COUNT(*) as c FROM skills").fetchone()["c"]
        if existing == 0:
            for skill, category in SKILL_CATEGORIES.items():
                conn.execute("INSERT IGNORE INTO skills (name, category) VALUES (%s, %s)", (skill, category))
            conn.commit()
    finally:
        conn.close()


def seed_demo_company():
    conn = get_db_connection()
    try:
        existing = conn.execute("SELECT COUNT(*) as c FROM companies").fetchone()["c"]
        if existing == 0:
            conn.execute(
                "INSERT INTO companies (name, email, password) VALUES (%s, %s, %s)",
                ("SkillMatch Demo Company", "hr@skillmatch.ai", "hr123"),
            )
            conn.commit()
    finally:
        conn.close()


def _count_questions(conn, qtype: str, level: str) -> int:
    if qtype == "sql":
        row = conn.execute(
            "SELECT COUNT(*) as c FROM questions WHERE skill IN ('SQL', 'MySQL') AND type = 'coding' AND level = %s",
            (level,),
        ).fetchone()
    elif qtype == "coding":
        row = conn.execute(
            "SELECT COUNT(*) as c FROM questions WHERE type = 'coding' AND skill NOT IN ('SQL', 'MySQL') AND level = %s",
            (level,),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT COUNT(*) as c FROM questions WHERE type = %s AND level = %s",
            (qtype, level),
        ).fetchone()
    return row["c"]


def _validate_question_availability(conn, level: str) -> dict | None:
    """Check if enough questions exist. Returns error dict if not, None if OK."""
    availability = {}
    for qtype, needed in QUESTION_DISTRIBUTION.items():
        available = _count_questions(conn, qtype, level)
        availability[qtype] = available
        if available < needed:
            return {
                "success": False,
                "error": f"Insufficient questions for {level}",
                "details": availability,
            }
    return None


def create_assessment_for_candidate(candidate_id: int, skills: list[str], degree: str) -> int:
    conn = get_db_connection()
    try:
        level = determine_level(degree)
        difficulty = get_difficulty(level)

        logger.info("=== Assessment Generation ===")
        logger.info("Candidate ID: %s", candidate_id)
        logger.info("Qualification: %s", degree)
        logger.info("Assessment Level: %s", level)
        logger.info("Difficulty: %s", difficulty)

        validation_error = _validate_question_availability(conn, level)
        logger.info("Question availability for %s: %s", level, {
        qtype: _count_questions(conn, qtype, level)
        for qtype in QUESTION_DISTRIBUTION
})
        if validation_error:
            raise ValueError(f"{validation_error['error']} - {validation_error['details']}")

        cursor = conn.execute(
            "INSERT INTO assessments (candidate_id, level, status) VALUES (%s, %s, 'pending')",
            (candidate_id, level),
        )
        assessment_id = cursor.lastrowid

        priority_skills = list(dict.fromkeys(skills + ["Python", "SQL"]))

        selected_ids = []
        used_ids = set()

        for qtype, count in QUESTION_DISTRIBUTION.items():
            needed = count

            if qtype == "sql":
                for skill in ["SQL", "MySQL"]:
                    if needed <= 0:
                        break
                    rows = conn.execute(
                        "SELECT id FROM questions WHERE skill = %s AND type = 'coding' AND level = %s AND id NOT IN ({}) ORDER BY id".format(
                            ",".join(str(uid) for uid in used_ids) if used_ids else "0"
                        ),
                        (skill, level),
                    ).fetchall()
                    for row in rows:
                        if needed <= 0:
                            break
                        selected_ids.append(row["id"])
                        used_ids.add(row["id"])
                        needed -= 1
                continue

            if qtype == "coding":
                for skill in priority_skills:
                    if needed <= 0:
                        break
                    if skill in ("SQL", "MySQL"):
                        continue
                    rows = conn.execute(
                        "SELECT id FROM questions WHERE skill = %s AND type = 'coding' AND level = %s AND id NOT IN ({}) ORDER BY id".format(
                            ",".join(str(uid) for uid in used_ids) if used_ids else "0"
                        ),
                        (skill, level),
                    ).fetchall()
                    for row in rows:
                        if needed <= 0:
                            break
                        selected_ids.append(row["id"])
                        used_ids.add(row["id"])
                        needed -= 1

                if needed > 0:
                    rows = conn.execute(
                        "SELECT id FROM questions WHERE type = 'coding' AND skill NOT IN ('SQL', 'MySQL') AND level = %s AND id NOT IN ({}) ORDER BY id".format(
                            ",".join(str(uid) for uid in used_ids) if used_ids else "0"
                        ),
                        (level,),
                    ).fetchall()
                    for row in rows:
                        if needed <= 0:
                            break
                        selected_ids.append(row["id"])
                        used_ids.add(row["id"])
                        needed -= 1
                continue

            # Standard types: theory, mcq, code_output, debugging
            for skill in priority_skills:
                if needed <= 0:
                    break
                rows = conn.execute(
                    "SELECT id FROM questions WHERE skill = %s AND type = %s AND level = %s AND id NOT IN ({}) ORDER BY id".format(
                        ",".join(str(uid) for uid in used_ids) if used_ids else "0"
                    ),
                    (skill, qtype, level),
                ).fetchall()
                for row in rows:
                    if needed <= 0:
                        break
                    selected_ids.append(row["id"])
                    used_ids.add(row["id"])
                    needed -= 1

            if needed > 0:
                rows = conn.execute(
                    "SELECT id FROM questions WHERE type = %s AND level = %s AND id NOT IN ({}) ORDER BY id".format(
                        ",".join(str(uid) for uid in used_ids) if used_ids else "0"
                    ),
                    (qtype, level),
                ).fetchall()
                for row in rows:
                    if needed <= 0:
                        break
                    selected_ids.append(row["id"])
                    used_ids.add(row["id"])
                    needed -= 1

        # Validate: exactly 30, no duplicates, no level mixing
        if len(selected_ids) != 30:
            raise ValueError(f"Assessment generation failed: expected 30 questions, got {len(selected_ids)} for {level}")

        if len(set(selected_ids)) != 30:
            raise ValueError("Duplicate questions detected in assessment")

        for qid in selected_ids:
            conn.execute(
                "INSERT INTO assessment_questions (assessment_id, question_id) VALUES (%s, %s)",
                (assessment_id, qid),
            )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return assessment_id
