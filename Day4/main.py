Paste FastAPI web application code.
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from workflow import graph

app = FastAPI()

# -----------------------------
# HOME PAGE
# -----------------------------

@app.get("/", response_class=HTMLResponse)
async def home():

    return """
    <html>

    <head>
        <title>Enterprise Banking AI Assistant</title>
    </head>

    <body style="
        font-family: Arial;
        background-color: #f4f4f4;
        padding: 40px;
    ">

        <div style="
            background: white;
            padding: 30px;
            border-radius: 10px;
            max-width: 900px;
            margin: auto;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
        ">

            <h1>🏦 Enterprise Banking AI Assistant</h1>

            <p>
                Ask questions related to:
                loans, fraud detection, compliance,
                KYC policies, and banking rules.
            </p>

            <form action="/analyze" method="post">

                <textarea
                    name="user_input"
                    rows="8"
                    style="
                        width: 100%;
                        padding: 15px;
                        font-size: 16px;
                        border-radius: 6px;
                    "
                    placeholder="Ask banking question here..."
                ></textarea>

                <br><br>

                <button
                    type="submit"
                    style="
                        background-color: #0078D4;
                        color: white;
                        padding: 12px 20px;
                        border: none;
                        border-radius: 5px;
                        font-size: 16px;
                        cursor: pointer;
                    "
                >
                    Analyze
                </button>

            </form>

        </div>

    </body>
    </html>
    """

# -----------------------------
# ANALYZE ROUTE
# -----------------------------

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(user_input: str = Form(...)):

    result = graph.invoke({

        "user_input": user_input
    })

    final_answer = result["final_result"]

    return f"""
    <html>

    <head>
        <title>AI Banking Decision</title>
    </head>

    <body style="
        font-family: Arial;
        background-color: #f4f4f4;
        padding: 40px;
    ">

        <div style="
            background: white;
            padding: 30px;
            border-radius: 10px;
            max-width: 1000px;
            margin: auto;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
        ">

            <h1>🏦 AI Banking Decision</h1>

            <h3>User Question</h3>

            <div style="
                background-color: #f0f0f0;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 25px;
                white-space: pre-wrap;
                line-height: 1.7;
            ">

                {user_input}

            </div>

            <h3>AI Response</h3>

            <div style="
                background-color: #eef6ff;
                padding: 20px;
                border-radius: 8px;
                white-space: pre-wrap;
                line-height: 1.9;
                font-size: 16px;
            ">

                {final_answer}

            </div>

            <br><br>

            <a href="/"
               style="
                    text-decoration: none;
                    color: #0078D4;
                    font-weight: bold;
               ">
               ← Ask Another Question
            </a>

        </div>

    </body>
    </html>
    """
