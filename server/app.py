import os
import spacy
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)
cors = CORS(app, origins='http://localhost:5173')

# Initialize spaCy English language model
nlp = spacy.load("en_core_web_sm")
print("nlp downld")



# Function to preprocess text using spaCy
def preprocess_text(text):
    doc = nlp(text.lower())  # Lowercase text
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]  # Remove stop words and punctuation
    # Join the tokens with a space to form a string
    preprocessed_text = ' '.join(tokens)
    return preprocessed_text




# Function to find the closest matching answer using NLP
def find_most_similar_question(user_question, database_questions):
    # Preprocess the user question
    user_question_processed = preprocess_text(user_question)

    # Initialize variables for tracking the best match
    best_match_score = 0
    best_match_question = None

    # Loop through each database question
    for question in database_questions:
        # Preprocess the database question
        question_processed = preprocess_text(question)

        # Calculate similarity between the user question and the current database question
        user_doc = nlp(user_question_processed)
        question_doc = nlp(question_processed)
        similarity = user_doc.similarity(question_doc)

        # Update the best match if the current similarity is higher
        if similarity > best_match_score:
            best_match_score = similarity
            best_match_question = question

    # Check if a close enough match was found
    if best_match_score < 0.5:
        return None, None

    # Retrieve the answer from the database for the best match (using the question itself)
    # cursor = connection.cursor() 
    # cursor.execute("SELECT answer FROM questions_answer WHERE question = %s", (best_match_question,))
    # answer = cursor.fetchone()[0]
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT answer FROM questions_answer WHERE question = %s", (best_match_question,))
        answer = cursor.fetchone()[0]
        # connection.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error getting best_match_question data from DB: ", error)
    finally:
        cursor.close()

    return answer, best_match_score




# Database connection object (initially None)
connection = None
database_questions = None
cursor = None

# Database connection function
def get_db_connection():
    global connection
    global database_questions
    global cursor

    if connection is None:
        print("db connect")
        try:
            db_url = os.getenv("DATABASE_URL")
            connection = psycopg2.connect(db_url)
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT question FROM questions_answer")
                database_questions = [row[0] for row in cursor.fetchall()] 
                # connection.commit()
            except (Exception, psycopg2.Error) as error:
                print("Error getting data from DB: ", error)
            finally:
                cursor.close()
        except Exception as e:
            print(f"Error connecting to database: {e}")
            exit(1)
    return connection,database_questions



@app.post("/api/answer")
def answer_question():
    if request.is_json:
        data = request.get_json()
        question = data.get("question")
        if question:
            # Connect to database
            connection, database_questions = get_db_connection()
            cursor = connection.cursor()  # Define the cursor variable

            try:
                # Fetch all questions from the database
                # cursor.execute("SELECT question FROM questions_answer")
                # database_questions = [row[0] for row in cursor.fetchall()]

                # Find the most similar question and answer using NLP
                answer, similarity = find_most_similar_question(question, database_questions)

                if answer:
                    # Return the answer and optionally the similarity score
                    return jsonify({"answer": answer, "similarity": similarity})
                else:
                    return jsonify({"error": "Your question is not relatable to our service."}), 404

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