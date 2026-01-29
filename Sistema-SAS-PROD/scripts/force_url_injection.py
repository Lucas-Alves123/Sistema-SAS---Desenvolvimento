
import re

file_path = r'c:\Users\lucas.luna\sistema de atendimento ao servidor - sas\Sistema-SAS---Desenvolvimento\Sistema-SAS---Desenvolvimento\identificacao.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace URL Logic
# We look for `// Determine Base URL` and replace the block until `const apiUrl =`

start_marker = "// Determine Base URL"
end_marker = "const apiUrl ="

if start_marker in content and end_marker in content:
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    # Find the end of the line for end_marker to include it in replacement or keep it?
    # Actually, let's keep `const apiUrl =` but change the value.
    
    # Let's replace the whole block including `const apiUrl = ...` line.
    # We find the end of the line containing `const apiUrl =`
    line_end_idx = content.find('\n', end_idx)
    
    new_block = """// FORCE LOCALHOST 5000
                const baseUrl = 'http://localhost:5000';
                const apiUrl = `${baseUrl}/api/identificacao/validar?valor=${encodeURIComponent(valor)}`;"""
    
    content = content[:start_idx] + new_block + content[line_end_idx:]
    print("Replaced URL logic.")
else:
    print("Could not find URL logic block.")

# 2. Add Alert
# Find `console.error(err);` in the catch block and add alert after it.
alert_code = "\n                alert('Erro: ' + err.message);"

if "console.error(err);" in content:
    # Check if alert already exists to avoid duplication
    if "alert('Erro: ' + err.message);" not in content:
        content = content.replace("console.error(err);", "console.error(err);" + alert_code)
        print("Added alert.")
    else:
        print("Alert already exists.")
else:
    print("Could not find console.error(err).")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
