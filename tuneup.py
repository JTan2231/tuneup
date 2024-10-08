import sys
import os
import json
import subprocess as sp

import requests

if len(sys.argv) != 2:
    print("Usage: python tuneup.py <url>")
    sys.exit(1)

with open('accomplishments', 'r') as f:
    accomplishments = f.read()

with open('template.tex', 'r') as f:
    template = f.read()


url = sys.argv[1]
posting = requests.get(url).text
start = posting.find('<body>')
end = posting.find('</body>')

if start == -1:
    posting = posting[start:end]


def get_replacement_string(x):
    return '{{ ' + str(x) + ' }}'


replacement_substrings = []
i = 0
while template.find(get_replacement_string(i)) > -1:
    replacement_substrings.append(get_replacement_string(i))
    i += 1


prompt = f"""
Below is a list of accomplishments I've completed over the past 1.5 years
at my current company.
```markdown
{accomplishments}
```

Using this job posting,
```html
{posting}
```
tailor {len(replacement_substrings)} of the given accomplishments to the
specifications of this job posting, highlighting the most relevant achievements
and skills that align with the job requirements. Emphasis quantifiable
metrics and tangible + relatable activities and technologies.

Don't be too on the nose. Emphasize concision--each bullet point should fit
on a single line. But don't sacrifice informational density!

Return a JSON list of format:
{{
    "accomplishments": [
        {{ "accomplishment": "..." }},
    ]
}}
"""

response = requests.post("https://api.openai.com/v1/chat/completions", json={
    "model": "gpt-4o",
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "response_format": {"type": "json_object"},
}, headers={
    "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
})

response_json = response.json()
accomplishments = response_json['choices'][0]['message']['content']
print(accomplishments)
accomplishments = json.loads(accomplishments)["accomplishments"]

assert (len(accomplishments) == len(replacement_substrings))
for i, (accomplishment, substring) in enumerate(zip(accomplishments, replacement_substrings)):
    template = template.replace(substring, accomplishment['accomplishment'])


output_name = 'resume.tex'
with open(output_name, 'w') as f:
    f.write(template)

sp.run(['./pdf.sh'])
