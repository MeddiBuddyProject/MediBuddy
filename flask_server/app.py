from flask import Flask, render_template, request,jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)   

# DB 대신 배열
reservations = []

# # MySQL 데이터베이스 연결
# app.config['SQLALCHEMY_DATABASE_URI'] = ''
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.route('/')
def index():
    return render_template('information.html')
    
@app.route('/move', methods=['POST'])
def move():
    select = request.form['select']
    if select == 'reservation':
        return render_template('information.html')

@app.route('/information', methods=['GET', 'POST'])
def information():
    if request.method == 'POST':
        
        name = request.form['name']
    
        grade = request.form['grade']
        ban = request.form['ban']
        number = request.form['number']

        reservations.append({"name": name, "grade": grade, "ban": ban, "number": number,"isSelf" : None,"symptom" : None})
        print(reservations)
        return render_template('cure_method.html')
    
    return render_template('information.html')

@app.route('/cure_method', methods=['GET', 'POST'])
def cure_method():
    if request.method == 'POST':
        isSelf = request.form['isSelf']

        if reservations:
            reservations[-1]['symptoms'] = symptoms
            if isSelf == "true" :
                reservations[-1]['isSelf'] = True
            else :
                reservations[-1]['isSelf'] = False
            return render_template('symptoms.html')
        else:
            return "저장할 예약 정보가 없습니다.", 400
        
    return render_template('cure_method.html')

@app.route('/symptoms', methods=['GET', 'POST'])
def symptoms():
    if request.method == 'POST':
        symptoms = request.form['symptoms']

        if reservations:
            reservations[-1]['symptoms'] = symptoms
            return render_template('symptoms.html')
        else:
            return "저장할 예약 정보가 없습니다.", 400

    return render_template('final.html')

@app.route('/final')
def final():
    return render_template('final.html')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
