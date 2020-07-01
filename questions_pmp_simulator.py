
# coding: utf-8

# In[384]:


import requests
import urllib.request
import time
import pandas as pd
import os 

from bs4 import BeautifulSoup



# In[385]:


HOME_PAGE = "https://www.danielecheverria.com/pmpv3/"
LOGIN = "https://www.danielecheverria.com/pmpv3/ajax/login" # post 

NEW_ASSETMENT = "https://www.danielecheverria.com/pmpv3/preparador/nuevoestudio" 
# accion: crearsesion
# titulo: E

INDEX_PAGE = "https://www.danielecheverria.com/pmpv3/ajax/actualizartiemposesion" # COOKIE DE POST SESSION --> GET SESSION CREATED
SESION_ASSETMENT = "https://www.danielecheverria.com/pmpv3/preparador/estudio/[SESSION]"  # POST SESSION --> GET SESSION CREATED
RESPONSE_ASSETMENT = "https://www.danielecheverria.com/pmpv3/ajax/responder/[SESSION]"

# sesion: 51657
# respuesta: 1
# id: 2962312
#  id_pregunta: 622
#  accion_boton: responder

NEXT_QUESTION = "https://www.danielecheverria.com/pmpv3/ajax/marcar/[SESSION]"
# sesion: 51709
# id: 2963304
# id_pregunta: 3599
# accion_boton: marcar

LOGIN_EMAIL_FIELD = "email"
LOGIN_CLAVE_FIELD = "clave"

ACTION_FIELD = "accion"
TITLE_FIELD = "titulo"

AUTH_USER = "et18121038@estratecno.es"
AUTH_PASSWORD ="et18121038pass"

ACTION_VALUE = "crearsesion"
TITLE_VALUE = "E" # cualquiera 


# FILE SETTINGS 
# PREGUNTA, RESPUESTA1,CORRECTA1_S_N, RESPUESTA2,CORRECTA2_S_N, RESPUESTA3,CORRECTA3_S_N, RESPUESTA4,CORRECTA4_S_N
QUESTIONS_FILE = "pmp_questions.csv"

MAX_QUESTIONS = 200


# In[386]:


# LOGIN 
#payload = {LOGIN_EMAIL_FIELD:AUTH_USER,LOGIN_CLAVE_FIELD : AUTH_PASSWORD}
#r = requests.post(LOGIN,  data = payload)
#print(r.url)


# In[387]:


class display(object):
    """Display HTML representation of multiple objects"""
    template = """<div style="float: left; padding: 10px;">
    <p style='font-family:"Courier New", Courier, monospace'>{0}</p>{1}
    </div>"""
    def __init__(self, *args):
        self.args = args
        
    def _repr_html_(self):
        return '\n'.join(self.template.format(a, eval(a)._repr_html_())
                         for a in self.args)
    
    def __repr__(self):
        return '\n\n'.join(a + '\n' + repr(eval(a))
                           for a in self.args)


# In[388]:


# LOGIN 
payload = {LOGIN_EMAIL_FIELD:AUTH_USER,LOGIN_CLAVE_FIELD : AUTH_PASSWORD}
r = requests.post(LOGIN,  data = payload)


_session = dict(PHPSESSID = r.cookies["PHPSESSID"])
payload = {ACTION_FIELD:ACTION_VALUE,TITLE_FIELD : TITLE_VALUE}
r1 = requests.post(NEW_ASSETMENT,  cookies = _session, data = payload)

soup2 = BeautifulSoup(r1.content, 'html.parser')
querystring = r1.url.split("/")
assetment_id = querystring[len(querystring)-1]
question_id = soup2.find('input', {'name': 'id_pregunta'}).get('value')
generic_id = soup2.find('input', {'name': 'id'}).get('value')    

df = pd.DataFrame() # Note that there are now row data inserted.



for i in range(1, MAX_QUESTIONS+1):
    
    #print("session:" + SESION_ASSETMENT)
    session_url = SESION_ASSETMENT 
    session_url = session_url.replace("[SESSION]", assetment_id)
    session_url = session_url + "/" + str(i)        
    print("session:" + session_url)
   
    request = requests.post(session_url,  cookies = _session, data = payload_answer)
    # GET SIMULATED ANSWERS CONTENT  FROM INITIAL RENDER
    soup = BeautifulSoup(request.content, 'html.parser') 
    question = soup.find("div", { "class" : "titular" }).get_text()
    question_id = soup.find('input', {'name': 'id_pregunta'}).get('value')
    generic_id = soup.find('input', {'name': 'id'}).get('value')
    
    categories  = soup.findAll("div", { "class" : "bloque" })   
    for x in categories:
        blocks = x.findAll('p')
        # HAY P de categorias
        if len(blocks)>0:        
            group  = blocks[1].get_text().replace("Grupo:","")
            area =  blocks[2].get_text().replace("Area:","")
    
    print(group)
    print(area)
    answers = soup.find_all("div", { "class" : "respuesta_texto" })
    counter = 1
    l_answers = []
    for answer in answers:
          l_answers.append(answer.get_text());
    
     # GET QUESTION CORRECTED 
    payload_answer = {"sesion" :assetment_id,"respuesta" : "1", "id" : generic_id , "id_pregunta" : question_id, "accion_boton" : "responder"}
    RESPONSE_ASSETMENT = RESPONSE_ASSETMENT.replace("[SESSION]", assetment_id)   
    r3_answer = requests.post(RESPONSE_ASSETMENT,  cookies = _session, data = payload_answer)
    
    json_correction = r3_answer.json()
    correct_answer_index =  json_correction["respuesta_bien"]


    data = {'Question': question, 'Answer1': l_answers[0],'Answer1Correct': correct_answer_index =='1',
             'Answer2': l_answers[1], 'Answer2Correct': correct_answer_index =='2',
            'Answer3': l_answers[2], 'Answer3Correct': correct_answer_index =='3', 
            'Answer4': l_answers[3], 'Answer4Correct': correct_answer_index =='4',
            'Feedback':json_correction["respuesta_comentarios"],
            'Group:' : group, "Area" : area}
   
    
    # <div class="bloque">
    #<p>Pregunta 5 de 203</p>
    #<p>Grupo: EjecuciÃ³n</p>
    #<p>Area: Comunicaciones</p>
    #</div>      
    df = df.append(data, ignore_index=True)
    
   


# In[389]:


df


# In[390]:


csv_path = os.path.join(os.getcwd(),QUESTIONS_FILE)
if os.path.exists(csv_path):
    df_existing = pd.read_csv(csv_path)
else:
    df_existing = pd.DataFrame() # Note that there are now row data inserted.


# In[391]:


df_final = pd.concat([df,df_existing])


# In[392]:


df_final.to_csv(csv_path,encoding='utf-8', index=False)


# In[393]:


df_final.shape


# In[394]:


display('df', 'df_existing', 'pd.concat([df,df_existing])')

