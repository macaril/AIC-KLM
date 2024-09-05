from flask import Flask, request, jsonify
import joblib
import sqlite3
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

lr = joblib.load('model/SkillClass/ModelLogreg1.pkl')
label_encoder1 = joblib.load('model/SkillClass/label_encoder1.pkl')
tfidf1 = joblib.load('model/SkillClass/tfidf1.pkl')

gb = joblib.load('model/LinkClass/ModelGB.pkl')
label_encoder2 = joblib.load('model/LinkClass/labelEncoder.pkl')
tfidf2 = joblib.load('model/LinkClass/tfidf.pkl')

DATABASE = 'db/database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/predict', methods=['POST'])
def predictSkill():
    data = request.get_json()
    role = data.get('role')
    
    x1 = tfidf1.transform([role])
    skill = lr.predict(x1)
    skillPred = label_encoder1.inverse_transform(skill)[0]
    
    x2 = tfidf2.transform([role])
    link = gb.predict(x2)
    linkPred = label_encoder2.inverse_transform(link)[0]

    return jsonify({
        'skill': skillPred,
        'recommended_courses': linkPred
    })

@app.route('/data', methods=['GET'])
def get_data():
    year = request.args.get('year')
    month = request.args.get('month')
    page = int(request.args.get('page', 1))
    per_page = request.args.get('per_page', 100)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT * FROM grafik
        WHERE substr(JobPosting, 7, 4) = ?
    '''
    
    params = [year]
    
    if month:
        query += ' AND substr(JobPosting, 4, 2) = ?'
        params.append(month)
    
    if per_page:
        query += ' LIMIT ? OFFSET ?'
        params.extend([int(per_page), (page - 1) * int(per_page)])
    else:
        query += ' LIMIT -1'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    data = [dict(row) for row in rows]
    return jsonify(data)

@app.route('/role', methods=['GET'])
def get_roles_by_title():
    title = request.args.get('title')
    
    if not title:
        return jsonify({'error': 'Title parameter is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT DISTINCT Role FROM grafik
        WHERE JobTitle LIKE ?
    '''
    
    params = [f'%{title}%']
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    roles = [row['Role'] for row in rows]
    return jsonify({'roles': roles})

@app.route('/title', methods=['GET'])
def get_all_job_titles():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT DISTINCT JobTitle FROM grafik
    '''
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    titles = [row['JobTitle'] for row in rows]
    return jsonify({'titles': titles})


if __name__ == '__main__':
    app.run(debug=True)