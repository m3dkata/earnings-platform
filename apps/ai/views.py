from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import os
from vanna.remote import VannaDefault
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache

api_key = os.environ.get("VANNA_API_KEY")
vanna_model_name = os.environ.get("VANNA_MODEL_NAME")
vanna_ai = VannaDefault(model=vanna_model_name, api_key=api_key)
vanna_ai.connect_to_postgres(
    host=os.environ.get("DB_HOST"),
    dbname=os.environ.get("DB_NAME"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    port=os.environ.get("DB_PORT"),
)


def is_staff_user(user):
    return user.is_staff


def get_cache_key(user_id):
    return f"ai_chat_{user_id}"


def cache_chat_message(user_id, message, is_user=False):
    cache_key = f"ai_chat_{user_id}"
    current_chat = cache.get(cache_key) or []

    if isinstance(message, dict):
        content = {
            "data": message.get("data"),
            "columns": message.get("columns"),
            "visualization": message.get("visualization"),
            "follow_up_questions": message.get("follow_up_questions"),
        }
    else:
        content = message

    current_chat.append(
        {
            "content": content,
            "is_user": is_user,
            "timestamp": datetime.now().isoformat(),
        }
    )
    cache.set(cache_key, current_chat, timeout=86400)


@login_required
@user_passes_test(is_staff_user)
def ai_query(request):
    query = request.GET.get("query", "").lower()
    response = process_query(query)

    cache_chat_message(request.user.id, query, is_user=True)
    cache_chat_message(request.user.id, response)

    return JsonResponse(response)


@login_required
def get_chat_history(request):
    cache_key = f"ai_chat_{request.user.id}"
    chat_history = cache.get(cache_key) or []
    return JsonResponse({"history": chat_history})


def process_query(query):
    try:
        sql = vanna_ai.generate_sql(query)

        if vanna_ai.is_sql_valid(sql):
            df = vanna_ai.run_sql(sql)

            try:
                df_metadata = df.dtypes.to_dict()
                plotly_code = vanna_ai.generate_plotly_code(
                    question=query, sql=sql, df_metadata=df_metadata
                )

                fig = vanna_ai.get_plotly_figure(plotly_code=plotly_code, df=df)
                follow_up_questions = vanna_ai.generate_followup_questions(
                    query, sql, df, n_questions=3
                )

                return {
                    "data": df.to_dict(orient="records"),
                    "columns": df.columns.tolist(),
                    "visualization": fig.to_json() if fig else None,
                    "follow_up_questions": follow_up_questions,
                }
            except Exception:
                return {
                    "data": df.to_dict(orient="records"),
                    "columns": df.columns.tolist(),
                    "follow_up_questions": vanna_ai.generate_followup_questions(
                        query, sql, df, n_questions=3
                    ),
                }
        else:
            return {"error": "Rephrase your question or try a different one!"}

    except Exception:
        return {"error": "I'd love to help you, but I can`t answer that question!"}
