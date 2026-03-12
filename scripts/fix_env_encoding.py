import pathlib

p = pathlib.Path(r'c:/Users/Dell/Downloads/adaptive-engine/adaptive-engine/.env')
text = 'MONGO_URI=mongodb+srv://username_db_user:xxxxx@cluster0.twvgrnr.mongodb.net/adaptive_engine?appName=Cluster0\nDB_NAME=adaptive_engine\nOPENAI_API_KEY=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\n'
p.write_text(text, encoding='utf-8')
print('wrote', p.read_bytes()[:20])


