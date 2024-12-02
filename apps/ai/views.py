from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os
import vanna
from vanna.remote import VannaDefault
import pandas as pd
from django.contrib.auth.decorators import user_passes_test

def is_staff_user(user):
    return user.is_staff

api_key = os.environ.get('VANNA_API_KEY')
vanna_model_name = os.environ.get('VANNA_MODEL_NAME')
vanna_ai = VannaDefault(model=vanna_model_name, api_key=api_key)
vanna_ai.connect_to_postgres(host=os.environ.get('DB_HOST'),
                       dbname=os.environ.get('DB_NAME'),
                       user=os.environ.get('DB_USER'),
                       password=os.environ.get('DB_PASSWORD'),
                       port=os.environ.get('DB_PORT'))

@login_required
@user_passes_test(is_staff_user)
def ai_query(request):
    query = request.GET.get('query', '').lower()
    response = process_query(query)
    return JsonResponse(response)

def process_query(query):
    try:
        sql = vanna_ai.generate_sql(query)
        
        if vanna_ai.is_sql_valid(sql):
            df = vanna_ai.run_sql(sql)
            
            try:
                df_metadata = df.dtypes.to_dict()
                plotly_code = vanna_ai.generate_plotly_code(
                    question=query,
                    sql=sql,
                    df_metadata=df_metadata
                )
                
                fig = vanna_ai.get_plotly_figure(plotly_code=plotly_code, df=df)
                follow_up_questions = vanna_ai.generate_followup_questions(query, sql, df, n_questions=3)
                
                return {
                    'data': df.to_dict(orient='records'),
                    'columns': df.columns.tolist(),
                    'visualization': fig.to_json() if fig else None,
                    'follow_up_questions': follow_up_questions
                }
            except:
                return {
                    'data': df.to_dict(orient='records'),
                    'columns': df.columns.tolist(),
                    'follow_up_questions': vanna_ai.generate_followup_questions(query, sql, df, n_questions=3)
                }
        else:
            return {'error': "Rephrase your question or try a different one!"}
            
    except Exception as e:
        return {'error': "I'd love to help you, but I can`t answer that question!"}
