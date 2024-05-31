from flask import Flask, request, jsonify
import uuid
from openai import OpenAI
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()  # Load environment variables from .env file

# Dictionary to store session IDs and associated questions
sessionDict = {}

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

exampleChunks = ["The purpose of this Regulation is to improve the functioning of the internal market by laying down a uniform legal framework in particular for the development, the placing on the market, the putting into service and the use of artificial intelligence systems (AI systems) in the Union, in accordance with Union values, to promote the uptake of human centric and trustworthy artificial intelligence (AI) while ensuring a high level of protection of health, safety, fundamental rights as enshrined in the Charter of fundamental rights of the European Union (the ‘Charter’), including democracy, the rule of law and environmental protection, against the harmful effects of AI systems in the Union, and to support innovation. This Regulation ensures the free movement, crossborder, of AI-based goods and services, thus preventing Member States from imposing restrictions on the development, marketing and use of AI systems, unless explicitly authorised by this Regulation. This Regulation should be applied in accordance with the values of the Union enshrined as in the Charter, facilitating the protection of natural persons, undertakings, democracy, the rule of law and environmental protection, while boosting innovation and employment and making the Union a leader in the uptake of trustworthy AI.",
 " AI systems can be easily deployed in a large variety of sectors of the economy and many parts of society, including across borders, and can easily circulate throughout the Union. Certain Member States have already explored the adoption of national rules to ensure that AI is trustworthy and safe and is developed and used in accordance with fundamental rights obligations. Diverging national rules may lead to the fragmentation of the internal market and may decrease legal certainty for operators that develop, import or use AI systems. A consistent and high level of protection throughout the Union should therefore be ensured in order to achieve trustworthy AI, while divergences hampering the free circulation, innovation, deployment and the uptake of AI systems and related products and services within the internal market should be prevented by laying down uniform obligations for operators and guaranteeing the uniform protection of overriding reasons of public interest and of rights of persons throughout the internal market on the basis of Article 114 of the Treaty on the Functioning of the European Union (TFEU). To the extent that this Regulation contains specific rules on the protection of individuals with regard to the processing of personal data concerning restrictions of the use of AI systems for remote biometric identification for the purpose of law enforcement, of the use of AI systems for risk assessments of natural persons for the purpose of law enforcement and of the use of AI systems of biometric categorisation for the purpose of law enforcement, it is appropriate to base this Regulation, in so far as those specific rules are concerned, on Article 16 TFEU. In light of those specific rules and the recourse to Article 16 TFEU, it is appropriate to consult the European Data Protection Board."]

@app.route('/api/messages/receive', methods=['POST'])
def receive_message():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({
            'status': 'error',
            'message': 'The question field is required.'
        }), 400

    question = data['question']
    session_id = data.get('sessionId')

    if session_id is None or session_id not in sessionDict:
        # Create a new session ID if it's not provided or doesn't exist in the dictionary
        if(session_id == None):
            session_id = str(uuid.uuid4())
        sessionDict[session_id] = []

    # Add the question to the list of questions for this session ID
    sessionDict[session_id].append(question)
    response_message = process_question(question, sessionDict[session_id], session_id)

    return jsonify({
        'status': 'success',
        'message': response_message,
        'sessionId': session_id
    })

def process_question(question,history ,session_id):
    # Function to process the question and generate a response
    # For simplicity, the response just echoes the session info and question count
    return (promptGPT(createPrompt(question,history, exampleChunks)))


def createPrompt(question, history, chunks):
    # Assuming 'chunks' and 'history' are lists that are already defined
    background_documents = '\n    '.join(chunks)
    chat_history = '\n    '.join(history)

    formatted_response = f'''
    
    Background Documents:
    ### {background_documents} ###

    Chat History:
    ### {chat_history} ###

    Asked Question:
    ### {question} ###

    Task:
    Utilize the information from the background documents and the context provided by previously asked questions to 
    generate a comprehensive, accurate, and contextually relevant answer to the current user question. Consider 
    cross-referencing data and themes from the documents and past questions to provide a holistic response. 
    Focus on delivering clear, concise, and informative content that addresses the specifics of the user's 
    inquiry while maintaining a conversational tone.
    '''
    print(formatted_response)
    return formatted_response


def promptGPT(prompt):
   
    if not prompt:
        return None

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(e)

if __name__ == '__main__':
    app.run(debug=True, port=3000)