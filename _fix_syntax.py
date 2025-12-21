import re

with open('fraud_demo.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the double parenthesis
content = content.replace('Style.RESET_ALL}\\n"))', 'Style.RESET_ALL}\\n")')

with open('fraud_demo.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed!")
