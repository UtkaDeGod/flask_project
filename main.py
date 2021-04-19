from flask import Flask, render_template, url_for, request, redirect
from form_anekdot import AddAnecdoteForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = AddAnecdoteForm()
    param = {"UserName": "Алёшка",
             "form": form,
             "avatar": url_for('static', filename='img/gg.jpg')}

    if request.method == 'GET':
        return render_template('main_page.html', **param)
    elif request.method == 'POST':
        print(form.name.data)
        print(form.text.data)
        print(form.category_black.data)
        print(form.category_tuolet.data)
        print(form.category_censure.data)
        return render_template('main_page.html', **param)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')