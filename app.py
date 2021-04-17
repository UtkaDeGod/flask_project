from flask import Flask
from flask_restful import Api
from data import db_session, anecdotes_resource


app = Flask(__name__)
api = Api(app)

api.add_resource(anecdotes_resource.AnecdotesResource, "/anecdote")
api.add_resource(anecdotes_resource.AnecdotesListResource, "/anecdotes/page")
api.add_resource(anecdotes_resource.AnecdotesTopResource, "/anecdotes/top")

if __name__ == '__main__':
    db_session.global_init('db/anecdotes.db')
    app.run(port=8080, host='0.0.0.0')
