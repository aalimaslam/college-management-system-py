import sqlite3
from ollama import chat
from ollama import ChatResponse

def get_all_data_from_db(db_path: str) -> str:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    context = ""

    try:
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table_name in tables:
            table = table_name[0]
            context += f"\nTable: {table}\n"

            # Get all rows from the table
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]
            context += f"Columns: {', '.join(column_names)}\n"

            for row in rows:
                row_data = ', '.join([str(item) for item in row])
                context += f"Row: {row_data}\n"

    except Exception as e:
        context += f"\nError fetching data: {e}"
    finally:
        conn.close()

    return context.strip()

# def generateResponse(prompt: str) -> str:
#     # Extract all DB data as context
#     context = get_all_data_from_db('college_management.db')

#     # Send it to the model
#     response: ChatResponse = chat(model="llama3.2", messages=[
#         {
#             'role': 'system',
#             'content': """You are an administrator of a college named "Caset College of Computer Science". 
#             Answer the questions that are related to the college and the given context. 
#             If anyone asks anything beyond the college database just say "I am not authorized to talk beyond the college." """
#         },
#         {
#             'role': 'user',
#             'content': f'Here is all the data from the sqlite database:\n{context}'
#         },
#         {
#             'role': 'user',
#             'content': prompt
#         }
#     ])

#     return response['message']['content']


def generateResponse(prompt: str) -> str:
    # Extract all DB data as context
    context = get_all_data_from_db('college_management.db')

    # Stream the response from Ollama
    stream = chat(
        model="llama3.2",
        messages=[
            {
                'role': 'system',
                'content': """You are an administrator of a college named "Caset College of Computer Science". 
                Answer the questions that are related to the college and the given context. 
                If anyone asks anything beyond the college database just say "I am not authorized to talk beyond the college." Don't mention any technical details in the response. """
            },
            {
                'role': 'user',
                'content': f'Here is all the data from the sqlite database:\n{context}'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        stream=True
    )

    response_text = ""
    for chunk in stream:
        content = chunk.get('message', {}).get('content', '')
        print(content, end='', flush=True)  # Stream to CLI
        response_text += content
    print()  # Newline after streaming
    return response_text