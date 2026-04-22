#!/usr/bin/env python3
# Script to fix README.md formatting

with open('README.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Fix section numbers that should be headers
    if line.startswith('6. ') or line.startswith('7. '):
        output.append('## ' + line[3:])
    # Fix subsection headers
    elif line.strip() in ['BranchPythonOperator', 'Important behavior', 'Interview explanation',
                          'Cron Syntax', 'Logical Date / Execution Date concept', 'Catchup',
                          'Backfilling', 'Idempotency', 'Jinja Templating', 'Incremental Loads',
                          'Event-Driven Architecture', 'Modular DAGs']:
        output.append('### ' + line.strip() + '\n')
    elif line.strip() in ['Full load vs Incremental load', 'Full load', 'Incremental load']:
        output.append('#### ' + line.strip() + '\n')
    # Add proper formatting for code blocks
    elif line.strip().startswith('python') and i > 0 and '```' not in lines[i-1]:
        output.append('```python\n')
    else:
        output.append(line)
    
    i += 1

with open('README.md', 'w', encoding='utf-8') as f:
    f.writelines(output)

print('README.md has been reformatted')
