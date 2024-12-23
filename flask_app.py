from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import asyncio
from icecream import ic
from helper import ask, pdf_text_read, greet_check_chain, answer_chain
from drive import save_to_google_sheet

# Enable icecream for debugging
ic.enable()
# ic.disable()

# Flask app setup
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Global variable for references
references_dict = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.json
        user_message = data.get('message')

        if not user_message:
            return Response("No message provided.", status=400, content_type='text/plain')

        ic(user_message)

        # Check for greeting
        greet_score = greet_check_chain.invoke({"user_query": user_message})
        ic(greet_score)

        if greet_score.binary_score == "yes":
            response_text = "I'm sorry, I didn't understand your input. Is there anything I can help you with?"
            save_to_google_sheet(user_message, response_text)
            return Response(response_text, content_type='text/plain')

        # Process non-greeting messages
        global references_dict
        references_dict, jina_text, pdf_links = ask(user_message)

        # Read PDF text asynchronously
        pdf_text = asyncio.run(pdf_text_read(pdf_links))

        def generate_response():
            full_res = ""
            for chunk in answer_chain.stream({
                "user_query": user_message,
                "jina_text": jina_text,
                "pdf_text": pdf_text
            }):
                
                yield chunk
                full_res += str(chunk)
            ic(full_res)
            save_to_google_sheet(user_message, full_res)

        return Response(generate_response(), content_type='text/plain')

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": "An internal error occurred"}), 500

@app.route('/references', methods=['POST'])
def references():
    global references_dict

    if references_dict:
        ic(references_dict)
        refs = [f'[{key}]({value})' for key, value in references_dict.items()]
        references_dict = {}  # Clear references after returning
        return jsonify({"references": refs})

    return jsonify({"references": []})

if __name__ == '__main__':
    app.run(debug=True)
