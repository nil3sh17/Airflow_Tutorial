#!/usr/bin/env python3
import re

with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix missing code block closures and proper markdown
replacements = [
    # Fix code blocks that are missing closing backticks
    (r'(def choose_path\(\):\n    sales_count = 10\n    if sales_count > 0:\n        return "process_sales"\n    return "skip_sales")\nThen', 
     r'\1\n```\n\nThen'),
    
    # Fix code block for branch_task
    (r'Then define tasks:\n\n```python\nbranch_task >> \[process_sales, skip_sales\]\n### Important',
     r'Then define tasks:\n```python\nbranch_task >> [process_sales, skip_sales]\n```\n\n**Important**'),
    
    # Fix "Example scenario" formatting
    (r'\nExample scenario\n',
     r'\n**Example scenario:**\n'),
    
    # Fix if/else formatting in branching section
    (r'If sales count > 0:\n\nrun processing task\nElse:\n\nrun "skip_processing" task',
     r'If sales count > 0:\n- run processing task\nElse:\n- run "skip_processing" task'),
    
    # Fix section headers
    (r'\n### BranchPythonOperator\n',
     r'\n#### BranchPythonOperator\n'),
     
    (r'\n### Important behavior\n',
     r'\n**Important behavior:**\n'),
     
    (r'\n### Interview explanation\n',
     r'\n**Interview explanation:**\n'),
     
    # Fix "Example" to be bold before code blocks  
    (r'\nExample\n```python',
     r'\n**Example:**\n```python'),
    
    # Fix "Cron Syntax" and other sections
    (r'\n### Cron Syntax\n',
     r'\n### Cron Syntax\n'),
     
    # Fix numbered sections to headers
    (r'\n## Scheduling, Time, and "The Change"\n',
     r'\n## Scheduling, Time, and Key Concepts\n'),
]

for old, new in replacements:
    try:
        content = re.sub(old, new, content)
    except:
        pass

# More manual fixes for common patterns
lines = content.split('\n')
output = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Clean up standalone plain text headers that should be markdown
    if i > 0 and i < len(lines) - 1:
        # Check if next line is blank or plain text (likely description)
        next_line = lines[i+1] if i+1 < len(lines) else ''
        
        # Fix plain text headers
        if line.strip() in ['Full load vs Incremental load', 'Full load', 'Incremental load']:
            if not line.startswith('#'):
                output.append('#### ' + line.strip())
                i += 1
                continue
        
        if line.strip() in ['Example in BashOperator', 'Example in SQL']:
            if not line.startswith('#'):
                output.append('\n**' + line.strip() + ':**')
                i += 1
                continue
    
    output.append(line)
    i += 1

content = '\n'.join(output)

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('README.md has been reformatted comprehensively')
