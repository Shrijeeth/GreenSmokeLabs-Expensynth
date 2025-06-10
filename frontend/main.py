import gradio as gr
import pandas as pd
import plotly.express as px
import requests


def get_financial_summary():
    try:
        response = requests.get("http://localhost:8000/api/financial_summary")
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        data = {"revenue": 1000, "expenses": 500, "profit": 500}
    return data

def display_financial_charts():
    df = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Revenue": [1000, 1200, 900, 1300, 1500, 1700],
        "Expenses": [400, 600, 500, 700, 800, 900]
    })
    df["Profit"] = df["Revenue"] - df["Expenses"]

    fig1 = px.line(df, x="Month", y="Revenue", title="Monthly Revenue")
    fig2 = px.bar(df, x="Month", y="Expenses", title="Monthly Expenses")
    fig3 = px.area(df, x="Month", y="Profit", title="Monthly Profit")
    latest = df.iloc[-1]
    fig4 = px.pie(
        names=["Revenue", "Expenses", "Profit"],
        values=[latest["Revenue"], latest["Expenses"], latest["Profit"]],
        title="Latest Financial Distribution"
    )
    return fig1, fig2, fig3, fig4

def chatbot_respond(user_message, history):
    history = history or []

    history.append({"role": "user", "content": user_message})
    
    try:
        payload = {"history": history}
        response = requests.post("http://localhost:8000/api/chat", json=payload)
        response.raise_for_status()
        bot_reply = response.json().get("reply", "Sorry, I didn't understand.")
    except Exception as e:
        bot_reply = "Server unavailable. This is a mocked reply."
        
    history.append({"role": "assistant", "content": bot_reply})
    
    return "", history, history

def reset_chat():
    """Reset chat history and clear the chatbot text box."""
    return "", [], []


# Frontend

with gr.Blocks(css="""
    #profile-icon {
        border-radius: 50%;
        margin-right: 10px;
               width: 100px;
               height: 100px;
    }
    .header h1 {
        margin: 0;
        font-family: 'Arial', sans-serif;
        color: #333;
    }
    .left-navbar {
        background-color: #fff;
        padding: 20px;
        border-right: 1px solid #ddd;
        min-height: 80vh;
    }
    .chat-panel {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 350px;
        background: #fff;
        border: 1px solid #ddd;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        border-radius: 8px;
        padding: 10px;
    }
    """) as demo:

    with gr.Row():
        gr.Image(value="assets/profile_pic.png", elem_id="profile-icon")
        gr.Markdown("<h1>Financial Health Dashboard</h1>", elem_classes="header")
    
    with gr.Row():
        with gr.Column(scale=1, elem_classes="left-navbar"):
            gr.Markdown("## Navigation")
            for nav in ["Dashboard", "Reports", "Analytics", "Settings"]:
                gr.Button(nav)
                
        with gr.Column(scale=3):
            with gr.Tabs():
                with gr.TabItem("Overview"):
                    summary = get_financial_summary()
                    gr.Markdown(f"""
                        ### Summary
                        **Revenue:** {summary['revenue']}  
                        **Expenses:** {summary['expenses']}  
                        **Profit:** {summary['profit']}
                        """)
                with gr.TabItem("Charts"):
                    fig1, fig2, fig3, fig4 = display_financial_charts()
                    gr.Plot(fig1)
                    gr.Plot(fig2)
                    gr.Plot(fig3)
                    gr.Plot(fig4)
    
    with gr.Column(elem_classes="chat-panel"):
        gr.Markdown("### Chatbot Support")
        chatbot_state = gr.State([])
        chatbot_ui = gr.Chatbot(type="messages")
        
        chatbot_input = gr.Textbox(placeholder="Type your message...", label="Your Message")
        with gr.Row():
            send_btn = gr.Button("Send")
            reset_btn = gr.Button("Reset Chat")
            
        send_btn.click(
            fn=chatbot_respond, 
            inputs=[chatbot_input, chatbot_state],
            outputs=[chatbot_input, chatbot_state, chatbot_ui],
            queue=False
        )
                       
        reset_btn.click(
            fn=reset_chat,
            inputs=None,
            outputs=[chatbot_input, chatbot_state, chatbot_ui],
            queue=False
        )

demo.launch()
