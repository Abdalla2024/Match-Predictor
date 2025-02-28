from flask import Flask, render_template, request, jsonify
from api.routes import api_bp
import os

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def home():
    """Home page route"""
    return render_template('index.html')

@app.route('/predict')
def predict():
    """Prediction page route"""
    return render_template('predict.html')

@app.route('/statistics')
def statistics():
    """Statistics page route"""
    return render_template('statistics.html')

if __name__ == '__main__':
    app.run(debug=True) 