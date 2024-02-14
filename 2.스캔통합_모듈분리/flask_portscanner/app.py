from flask import Flask, render_template, request
import multi

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        host = request.form.get('host')
        results = multi.scan_all(host)
        return render_template('results.html', host=host, results=results)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
