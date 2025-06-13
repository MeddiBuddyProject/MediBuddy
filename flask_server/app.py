from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

mongo_uri = "mongodb+srv://MediBuddyUser:MediBuddy2025@medibuddy.346h16q.mongodb.net/?retryWrites=true&w=majority&appName=MediBuddy"


client = MongoClient(mongo_uri)

db = client['medibuddy_db']
students = db['students']
health_records = db['health_records']

sample_students = [
    {"student_id": "2107", "name": "이상연", "password": "1111"},
    {"student_id": "2110", "name": "임채이", "password": "2222"},
    {"student_id": "2115", "name": "조현서", "password": "3333"},
]
students.insert_many(sample_students)

sample_health_records = [
    {
        "date": datetime(2025, 6, 6),
        "student_id": "2107",
        "name": "이상연",
        "treatment": "스스로 치료",
        "symptom_checked": True,
        "symptoms": "코피"
    },
    {
        "date": datetime(2025, 6, 5),
        "student_id": "2110",
        "name": "임채이",
        "treatment": "스스로 치료",
        "symptom_checked": False,
        "symptoms": "타박상"
    },
    {
        "date": datetime(2025, 6, 4),
        "student_id": "2115",
        "name": "조현서",
        "treatment": "보건 선생님 도움",
        "symptom_checked": True,
        "symptoms": "복통"
    }
]
health_records.insert_many(sample_health_records)


@app.route('/')
def index():
    return render_template('information.html')

@app.route('/move', methods=['POST'])
def move():
    select = request.form.get('select')
    if select == 'reservation':
        return redirect(url_for('information'))
    return redirect(url_for('index'))


@app.route('/information', methods=['GET', 'POST'])
def information():
    if request.method == 'POST':
        name = request.form.get('name')
        grade = request.form.get('grade')
        ban = request.form.get('ban')
        number = request.form.get('number')

        student_id = f"{grade}{ban}{number}".zfill(4)

        students.update_one(
            {"student_id": student_id}, 
            {"$set": {"name": name}},
            upsert=True
        )

        app.config['current_record'] = {
            "student_id": student_id,
            "name": name,
            "date": datetime.now()
        }

        return redirect(url_for('cure_method'))

    return render_template('information.html')


@app.route('/cure_method', methods=['GET', 'POST'])
def cure_method():
    if request.method == 'POST':
        treatment = request.form.get('isSelf')

        if 'current_record' not in app.config:
            return "저장된 환자 정보가 없습니다.", 400

        app.config['current_record']['treatment'] = treatment
        return redirect(url_for('symptoms'))

    return render_template('cure_method.html')


@app.route('/symptoms', methods=['GET', 'POST'])
def symptoms():
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')

        if 'current_record' not in app.config:
            return "저장된 환자 정보가 없습니다.", 400

        record = app.config['current_record']
        symptom_checked = bool(symptoms and symptoms.strip())

        health_records.insert_one({
            "date": record['date'],
            "student_id": record['student_id'],
            "name": record['name'],
            "treatment": record.get('treatment', ''),
            "symptom_checked": symptom_checked,
            "symptoms": symptoms
        })

        app.config.pop('current_record', None)

        return redirect(url_for('final'))

    return render_template('symptoms.html')


@app.route('/final')
def final():
    return render_template('final.html')

from flask import request, redirect, url_for
from bson.objectid import ObjectId

@app.route('/list', methods=['GET', 'POST'])
def list_records():
    if request.method == 'POST':
        delete_ids = request.form.getlist('delete_ids')
        if delete_ids:
            health_records.delete_many({"student_id": {"$in": delete_ids}})
            return redirect(url_for('list_records'))
        
        student_id = request.form.get('student_id')
    else:
        student_id = request.args.get('student_id')

    query = {}
    if student_id:
        query['student_id'] = student_id
    
    records = list(health_records.find(query).sort("date", -1))
    
    for record in records:
        record['_id'] = str(record['_id'])
        if 'date' in record and isinstance(record['date'], datetime):
            record['date'] = record['date'].strftime("%Y-%m-%d")
    
    return render_template('list.html', reservations=records)





if __name__ == '__main__':
    app.run(debug=True,port=5001)