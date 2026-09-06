with open("src/App.tsx", "r") as f:
    content = f.read()

content = content.replace("} MessageSquare, MessageSquare } from 'lucide-react';", ", MessageSquare } from 'lucide-react';")

with open("src/App.tsx", "w") as f:
    f.write(content)

