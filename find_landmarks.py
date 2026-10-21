import docx

doc = docx.Document(r"C:\Users\ASUS\Desktop\uni\TG2079\TG_2079.docx")

landmarks = []
for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if p.style.name.startswith("Heading") or any(txt.startswith(x) for x in ["Core Development", "1. Development", "2. Setup", "Version Control", "Visual Interface", "Desktop Responsive", "Mobile Responsive", "7. References", "ORDER", "Figure"]):
        landmarks.append((i, p.style.name, txt[:60]))

for idx, style, text in landmarks:
    safe_text = text.encode('ascii', 'replace').decode('ascii')
    print(f"Index {idx:03d} | Style: {style:<15} | Text: {safe_text}")
