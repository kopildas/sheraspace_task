import os
import spacy
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
cors = CORS(app, origins='http://localhost:5173')

# Initialize spaCy English language model
nlp = spacy.load("en_core_web_sm")

# Function to preprocess text using spaCy
def preprocess_text(text):
    doc = nlp(text.lower())
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    preprocessed_text = ' '.join(tokens)
    return preprocessed_text

# Function to find the closest matching answer using NLP
def find_most_similar_question(user_question):
    user_question_processed = preprocess_text(user_question)
    best_match_score = 0
    best_match_question = None

    connection, database_questions = get_db_connection()

    for question in database_questions:
        question_processed = preprocess_text(question)
        user_doc = nlp(user_question_processed)
        question_doc = nlp(question_processed)
        similarity = user_doc.similarity(question_doc)

        if similarity > best_match_score:
            best_match_score = similarity
            best_match_question = question

    if best_match_score < 0.5:
        return None, None

    cursor = connection.cursor()
    cursor.execute("SELECT answer FROM questions_answer WHERE question = %s", (best_match_question,))
    answer = cursor.fetchone()[0]
    cursor.close()
    connection.close()

    return answer, best_match_score

# Database connection object (initially None)
connection = None
database_questions = None

# Database connection function
def get_db_connection():
    global connection
    global database_questions

    if connection is None or database_questions is None:
        try:
            db_url = os.getenv("DATABASE_URL")
            connection = psycopg2.connect(db_url)

            if database_questions is None:
                cursor = connection.cursor()
                cursor.execute("SELECT question FROM questions_answer")
                database_questions = [row[0] for row in cursor.fetchall()]
                cursor.close()
        except Exception as e:
            print(f"Error connecting to database: {e}")
            exit(1)
    return connection, database_questions

@app.post("/api/answer")
def answer_question():
    if request.is_json:
        data = request.get_json()
        question = data.get("question")
        if question:
            try:
                connection, database_questions = get_db_connection()
                answer, similarity = find_most_similar_question(question)
                if answer:
                    return jsonify({"answer": answer, "similarity": similarity})
                else:
                    return jsonify({"answer": "Your question is not relatable to our service."})
            except Exception as e:
                print(f"Error accessing database: {e}")
                return jsonify({"error": "Database error occurred."}), 500
        else:
            return jsonify({"error": "Missing required field 'question'"}), 400
    else:
        return jsonify({"error": "Unsupported Media Type. Please use JSON."}), 415

@app.get("/")
def index():
    return jsonify({"msg": "home occurred."})