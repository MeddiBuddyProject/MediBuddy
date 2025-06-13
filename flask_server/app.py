from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)

mongo_uri = "mongodb+srv://MediBuddyUser:MediBuddy2025@medibuddy.346h16q.mongodb.net/?retryWrites=true&w=majority&appName=MediBuddy"


client = MongoClient(mongo_uri)

db = client['medibuddy_db']
students = db['students']
health_records = db['health_records']

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
            "symptoms": symptoms,
            "confirmation": False
        })

        app.config.pop('current_record', None)

        return redirect(url_for('final'))

    return render_template('symptoms.html')


@app.route('/final')
def final():
    r = health_records.find_one(sort=[('date', -1)])
    if not r:
        return render_template('final.html', info={})

    sid, name, date = r['student_id'], r['name'], r['date']

    all = list(health_records.find().sort("date", 1))
    wait = list(health_records.find({"treatment": {"$exists": False}}).sort("date", 1))

    entry = next((i+1 for i, x in enumerate(all) if x['student_id'] == sid and x['date'] == date), -1)
    wnum = next((i+1 for i, x in enumerate(wait) if x['student_id'] == sid and x['date'] == date), -1)
    wcount = len(wait)

    return render_template('final.html', info={
        'entry': entry, 'name': name, 'wait_num': wnum, 'wait_count': wcount
    })

@app.route('/list', methods=['GET', 'POST'])
def list_records():
    if request.method == 'POST':
        delete_ids = request.form.getlist('delete_ids')
        if delete_ids:

            object_ids = [ObjectId(id) for id in delete_ids]

            health_records.update_many(
                {"_id": {"$in": object_ids}},
                {"$set": {"confirmation": True}} 
            )
            return redirect(url_for('list_records'))

    query = {"confirmation": False}

    records = list(health_records.find(query).sort("date", -1))
    for record in records:
        record['_id'] = str(record['_id'])
        if 'date' in record and isinstance(record['date'], datetime):
            record['date'] = record['date'].strftime("%Y-%m-%d")

    return render_template('list.html', reservations=records)


@app.route('/studentlist', methods=['GET', 'POST'])
def studentlist():
    query = {"student_id": "2115"}

    records = list(health_records.find(query).sort("date", -1))
    for record in records:
        record['_id'] = str(record['_id'])
        if 'date' in record and isinstance(record['date'], datetime):
            record['date'] = record['date'].strftime("%Y-%m-%d")
    
    return render_template('studentlist.html', reservations=records)

@app.route('/delete_all', methods=['POST'])
def delete_all():
    health_records.delete_many({})
    students.delete_many({})
    return redirect(url_for('list_records'))


if __name__ == '__main__':
    app.run(debug=True,port=5001)