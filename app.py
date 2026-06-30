import os
import tempfile 

import streamlit as st
import plotly.io as pio

from graph import build_graph
from state import initial_state


st.set_page_config(page_title = "Data Analyst multi-agents", page_icon = "📊", layout = "wide")
st.title("Data Analyst multi-agents")
st.caption("Upload un CSV : 4 agents (Explorer → Planner → Coder → Writer) "
           "l'analysent automatiquement.")


#The graph is compiled only once
@st.cache_resource
def get_app():
    return build_graph()


graph = get_app()

uploaded = st.file_uploader("choisis un fichiers CSV", type ="csv")
run = st.button("Lancer l'analyse", disabled = (uploaded is None))

if run and uploaded is not None:
    #Write the upload to a temporary file
    with tempfile.NamedTemporaryFile(delete = False, suffix = ".csv") as tmp:
        tmp.write(uploaded.getbuffer())
        csv_path = tmp.name
    
    try:
        #Launch the graph IN REAL TIME to view progress by agent
        final_state, seen = None, set()
        with st.status("Analyse multi-agents en cours...", expanded = True) as status:
            for snap in graph.stream(initial_state(csv_path), stream_mode = "values"):
                final_state = snap
                if snap.get("data_summary") and "exp" not in seen:
                    seen.add("exp"); st.write("Exploration des données terminées")
                if snap.get("plan") and "plan" not in seen:
                    seen.add("plan"); st.write(f"plan étabilt : {len(snap['plan'])} analyses")
                if (snap.get("figures") or snap.get("error")) and "code" not in seen:
                    seen.add("code"); st.write("Code généré et exécuté")
                if snap.get("insights") and "writ" not in seen:
                    seen.add("writ"); st.write("Insights rédigés")
            status.update(label="Analyse terminée", state = "complete")
        
        #stores the result in session so that it persists through subsequent reruns    
        st.session_state["result"] = final_state            
    
    finally:
        os.unlink(csv_path)                     #Cleaning up the temporary file
        

#----------- Affichage -----------
result = st.session_state.get("result")
if result:
    figures = result.get("figures", [])
    if figures:
        st.subheader(f"Grapphiques ({len(figures)})")
        for fig_json in figures: 
            fig = pio.from_json(fig_json)
            st.plotly_chart(fig, use_container_width= True)
    
    st.subheader("Insights")
    st.markdown(result.get("insights", "_(aucun insight)_"))              
                        
