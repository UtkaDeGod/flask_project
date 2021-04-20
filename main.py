from flask import Flask, render_template, url_for, request, redirect
from form_anekdot import AddAnecdoteForm
from search_form import SearchForm
from user_data_form import UserData
from PIL import Image
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = AddAnecdoteForm()
    search_form = SearchForm()
    user_data = UserData()
    param = {"UserName": "Алёшка",
             "userid": "228ff",
             "name": "loh",
             "email": "fff@mail.com",
             "content": "fghgfd",
             "search_form": search_form,
             "form": form,
             "user_data": user_data,
             "avatar": url_for('static', filename='img/gg.jpg')}

    if request.method == 'GET':
        return render_template('user_page.html', **param)
    elif request.method == 'POST':
        # сохранение картинки
        uid = request.form["userid"]
        f = user_data.avatar.data
        filename = f"avater{uid}.png"
        f.save(os.path.join(app.instance_path, 'avatars', filename))
        im = Image.open(os.path.join("instance/avatars", filename))
        (width, height) = im.size
        if width > height:
            corr = (width - height) // 2
            im = im.crop((corr, 0, corr + height, height))
        elif width < height:
            corr = (height - width) // 2
            im = im.crop((0, corr, width, corr + width))
        im.save(os.path.join("instance/avatars", filename))
        return render_template('user_page.html', **param)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
