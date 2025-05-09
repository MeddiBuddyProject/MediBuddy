from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # 현재 페이지

@app.route('/next')
def next_page():
    return render_template('information.html')

@app.route('/information')
def information():
    return render_template('information.html')

@app.route('/cure_method')
def cure_method():
    return render_template('cure_method.html')

@app.route('/symptoms')
def symptoms():
    return render_template('symptoms.html')

@app.route('/final')
def final():
    return render_template('final.html')


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
