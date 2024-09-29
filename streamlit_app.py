import streamlit as st
import base64
import requests
import time
from googlesearch import search 

page_bg_img = '''
<style>
    [theme]
    primaryColor="#cbeaa6"
    backgroundColor="#c0d684"
    secondaryBackgroundColor="#f3f9d2"
    textColor="#386641" 
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

API_KEY_PLANT_ID = 'api-key'

def fetch_care_instructions(plant_name):
    query = f"{plant_name} plant care instructions"
    
    try:
        for result in search(query, num_results=1):
            return result  
    except Exception as e:
        return f"Error fetching care instructions: {e}"

st.title("🪴 Garden Gaze 🪴 ")
st.write("Plant Identification and Care Guide!")

uploaded_file = st.file_uploader("Upload an image of a plant or flower to identify and learn how to take care of it!", type=['jpg', 'jpeg', 'png'])

if 'images' not in st.session_state:
    st.session_state.images = []

if uploaded_file is not None:
    st.session_state.images.append(uploaded_file)  
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

st.sidebar.header("Gallery:")
if st.session_state.images:
    for img in st.session_state.images:
        st.sidebar.image(img, caption="Uploaded Image", use_column_width=True)
else:
    st.sidebar.write("No images uploaded yet.")

if st.session_state.images:
    images_base64 = [base64.b64encode(img.read()).decode('ascii') for img in st.session_state.images]

    response = requests.post(
        'https://api.plant.id/v3/identification',
        headers={'Api-Key': API_KEY_PLANT_ID},
        json={'images': images_base64}
    )

    if response.status_code == 201:
        task_result = response.json()

        if 'id' in task_result:
            task_id = task_result['id']
            st.write("Processing your image...")  

            while True:
                task_response = requests.get(
                    f'https://api.plant.id/v3/identification/{task_id}',
                    headers={'Api-Key': API_KEY_PLANT_ID}
                )

                if task_response.status_code == 200:
                    identification = task_response.json()

                    if identification['result']['is_plant']['binary']:
                        st.write("This is a plant!")
                        
                        suggestions = identification['result']['classification']['suggestions']
                        best_suggestion = max(suggestions, key=lambda x: x['probability'])
                        
                        plant_name = best_suggestion['name']
                        st.write(f"**Plant Name:** {plant_name}")
                        st.write(f"**Probability:** {best_suggestion['probability'] * 100:.2f}%")

                        care_link = fetch_care_instructions(plant_name)

                        if care_link:
                            st.subheader("Care Instructions")
                            link_text = f"Click here for Care Instructions for {plant_name}!"
                            st.markdown(f"[{link_text}]({care_link})", unsafe_allow_html=True)
                        else:
                            st.write("No care instructions found.")

                    else:
                        st.write("This is not a plant.")
                    break
                else:
                    st.write("Still processing... please wait.")
                time.sleep(5)

        else:
            st.write("Processing image...")
            if 'result' in task_result:
                identification = task_result['result']

                if identification['is_plant']['binary']:
                    st.write("This is a plant!")
                    
                    suggestions = identification['classification']['suggestions']
                    best_suggestion = max(suggestions, key=lambda x: x['probability'])
                  
                    plant_name = best_suggestion['name']
                    st.write(f"**Plant Name:** {plant_name}")
                    st.write(f"**Probability:** {best_suggestion['probability'] * 100:.2f}%")
                    
                    care_link = fetch_care_instructions(plant_name)

                    if care_link:
                        st.subheader("Care Instructions")
                        link_text = f"Click here for Care Instructions for {plant_name}!  🌱"
                        st.markdown(f"[{link_text}]({care_link})", unsafe_allow_html=True)
                    else:
                        st.write("No care instructions found.")

                else:
                    st.write("This is not a plant.")
    elif response.status_code == 400:
        st.write("Error 400: Bad Request")
        st.write("Response:", response.text)
    else:
        st.write(f"Error {response.status_code}: Unable to identify the plant.")
