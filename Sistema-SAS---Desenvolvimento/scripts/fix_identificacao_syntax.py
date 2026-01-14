
import re

file_path = r'c:\Users\lucas.luna\sistema de atendimento ao servidor - sas\Sistema-SAS---Desenvolvimento\Sistema-SAS---Desenvolvimento\identificacao.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix the mangled code fragment
# Look for ":${ minutes.toString().padStart(2, '0') } `;" and the closing brace
# This seems to be a leftover from a deleted function. We should remove it.
# It appears around line 739 in the user's paste.
mangled_pattern = r':\$\{ minutes\.toString\(\)\.padStart\(2, \'0\'\) \} `;\s*\n\s*}'
content = re.sub(mangled_pattern, '', content)

# Also remove the comment if it's dangling: "// Helper to generate random time"
content = content.replace('// Helper to generate random time', '')


# 2. Fix spaces in fetch URL
# fetch(`/ agendamentos / disponibilidade ? atendente_id = ${ attendantId }& data=${ dateStr }`)
# We want to remove spaces around slashes and question marks in this specific string.
# Or just replace the whole line with the correct one.
bad_fetch = "`/ agendamentos / disponibilidade ? atendente_id = ${ attendantId }& data=${ dateStr }`"
good_fetch = "`/agendamentos/disponibilidade?atendente_id=${attendantId}&data=${dateStr}`"
content = content.replace(bad_fetch, good_fetch)


# 3. Fix spaces in HTML tags in template literals
# < div class="...
content = content.replace('< div', '<div')
content = content.replace('</ div', '</div>')
content = content.replace('</div >', '</div>')
content = content.replace('div >', 'div>')


# 4. Fix spaces in Tailwind classes
# "flex items - center gap - 1.5 ..."
# We can use regex to fix "word - word" to "word-word"
# But be careful not to break math operations.
# In class names, it's usually "text - xs", "bg - red - 500".
# Let's target the specific line for badge.className
# badge.className = `flex items - center ...`

def fix_tailwind_classes(match):
    # Remove spaces around hyphens
    return match.group(0).replace(' - ', '-')

# Regex for the badge.className line
# It starts with `badge.className =` and ends with `;`
badge_class_pattern = r'badge\.className = `[^`]+`;'
content = re.sub(badge_class_pattern, fix_tailwind_classes, content)


# 5. Fix spaces in template interpolation
# ${ u.motivo_pausa } -> ${u.motivo_pausa} (This is valid JS but messy)
# The user's code has: `: ${ u.motivo_pausa } `
# This is fine, but let's clean it if we can. 
# The critical ones are the HTML tags and URLs.

# 6. Fix "fetch(/ agendamentos..." if it wasn't caught by exact string match
# Regex for fetch with spaces in path
fetch_pattern = r'fetch\(`/\s+agendamentos\s+/'
content = re.sub(fetch_pattern, "fetch(`/agendamentos/", content)


print("Applied syntax fixes.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
