import pathlib

p = pathlib.Path(r'c:/Users/Dell/Downloads/adaptive-engine/adaptive-engine/.env')
text = 'MONGO_URI=mongodb+srv://username_db_user:xxxx@cluster0.twvgrnr.mongodb.net/adaptive_engine?appName=Cluster0\nDB_NAME=adaptive_engine\nOPENAI_API_KEY=sk_OPEN_AI_KEY\n'
p.write_text(text, encoding='utf-8')
print('wrote', p.read_bytes()[:20])



