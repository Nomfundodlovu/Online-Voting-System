import streamlit as st
import datetime
import re
import random
import numpy as np
import wave
import io
import psycopg2
import yaml
import sqlite3
from twilio.rest import Client
import sounddevice as sd
import face_recognition as frg
import cv2
# from utils import submitNew, get_info_from_id, deleteOne
from utils import recognize, build_dataset, get_database2
import pickle as pkl
from collections import defaultdict
information = defaultdict(dict)
cfg = yaml.load(open('config.yaml','r'),Loader=yaml.FullLoader)
DATASET_DIR = cfg['PATH']['DATASET_DIR']
PKL_PATH = cfg['PATH']['PKL_PATH']
PICTURE_PROMPT = cfg['INFO']['PICTURE_PROMPT']
WEBCAM_PROMPT = cfg['INFO']['WEBCAM_PROMPT']

# from streamlit_webrtc import VideoTransformerBase, webrtc_streamer


# Sample registered user credentials for demonstration purposes
registered_users = {
    "john_doe": "password123",
    "jane_smith": "passw0rd456",
    # Add more registered users as needed
}

registered_users = {
    "id_number": {
        "profile_image": "/Users/da_mac_41_/Downloads/DA-logo.png"  # Replace with the appropriate file path
    }
}



def is_valid_id_number(id_number):
    # ID Number validation: Should have exactly 13 characters
    return len(id_number) == 13

def is_valid_email(email):
    # Email validation using regular expression
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_pattern, email)


def is_valid_username(username):
    # Username validation: Should have a combination of characters and numbers
    return bool(re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]+$", username))

def is_valid_password(password):
    # Password validation: 8 or more characters, at least one digit, one uppercase, one lowercase, and one special character
    return bool(re.match(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%^*?&()-_=+[\]{}|;:'\",.<>/?])[A-Za-z\d@$!%^*?&()-_=+[\]{}|;:'\",.<>/?]{8,}$", password))

    
personal_info = {}
def send_otp(phone_number, otp):
    # Set up your Twilio account credentials
    account_sid = "YOUR_TWILIO_ACCOUNT_SID"
    auth_token = "YOUR_TWILIO_AUTH_TOKEN"
    twilio_phone_number = "YOUR_TWILIO_PHONE_NUMBER"

    client = Client(account_sid, auth_token)

    # Send the OTP via SMS to the user's phone number
    message = client.messages.create(
        body=f"Your OTP for password reset is: {otp}",
        from_=twilio_phone_number,
        to=phone_number
    )

def homepage():
    
    st.title("Welcome to VoteConnect!")
    # Add the logo at the top of the page
    st.image("/Users/da_mac_41_/Downloads/logs.png", caption="Every Vote Counts", width=200)


    st.markdown("## Introduction")
    st.write("The Online Voting System allows registered users to cast their votes "
             "in various elections securely and conveniently.")

    st.markdown("## Voter Registration")
    st.write("If you are a new user, you can register to vote in the upcoming elections.")
    register_button = st.button("Register Now")
    if register_button:
        # Redirect to the voter registration page
        st.write("Redirecting to the voter registration page...")
        # Add your logic to redirect the user to the registration page

    st.markdown("## Already Have an Account?")
    st.write("If you already have an account, you can log in to access your voting dashboard.")
    login_link = st.button("Log In")
    if login_link:
        # Redirect to the login page
        st.write("Redirecting to the login page...")
        # Add your logic to redirect the user to the login page


    
def login_page():
    st.title("Login Page")
    
    firstname = 'Unknown'
    id_number = 'Unknown'
    # Input fields for ID Number and Password
    id_number = st.text_input("ID Number")
    password = st.text_input("Password", type="password")

    # Forgot Password button placed under the password textbox
    if st.button("Forgot Password"):
        reset_method = st.radio("Reset Method:", ("Email", "Phone Number"))

        if reset_method == "Email":
            email = st.text_input("Please enter your registered email")
            if email and is_valid_email(email):
                # Add your logic here to send the reset link to the user's email
                # After sending the reset link, show a success message to the user
                st.success(f"An email with password reset instructions has been sent to {email}.")
                st.write("Please check your email and follow the instructions to reset your password.")
            elif email:
                st.warning("Invalid email address. Please enter a valid email.")
        else:  # Reset method is Phone Number
            phone_number = st.text_input("Please enter your registered phone number")
            if phone_number and len(phone_number) == 10 and phone_number.isdigit():
                # Generate a random 6-digit OTP
                otp = str(random.randint(100000, 999999))
                # Add your logic to send the OTP to the user's phone number
                send_otp(phone_number, otp)
                st.success("An OTP has been sent to your registered phone number.")
                otp_input = st.text_input("Please enter the OTP to reset your password.")
                # Here, you can add your logic to verify the OTP and reset the password accordingly
                # For example, you can check if the OTP entered by the user matches the generated OTP
                # If it matches, you can proceed with the password reset process
                # You may use a button to trigger the password reset after verifying the OTP.
            elif phone_number:
                st.warning("Invalid phone number. Please enter a valid 10-digit number.")

#     cfg = yaml.load(open('config.yaml', 'r'), Loader=yaml.FullLoader)
    
#     conn = psycopg2.connect(
#     host="localhost",
#     port=5430,
#     database="food_ordering_system",
#     user="postgres"
# )


# # Create a cursor for database operations
#     cursor = conn.cursor()

# # Streamlit settings
    st.title("Face Recognition Login")
    st.sidebar.title("Settings")

# Create a menu bar
    menu = [ "None","Webcam"]
    choice = st.radio("Input type", menu)

# Put slide to adjust tolerance
    TOLERANCE = st.sidebar.slider("Tolerance", 0.0, 1.0, 0.5, 0.01)
    st.sidebar.info("Tolerance is the threshold for face recognition. The lower the tolerance, the more strict the face recognition. The higher the tolerance, the more loose the face recognition.")

# Information section
    st.sidebar.title("User Information")
    name_container = st.sidebar.empty()
    id_container = st.sidebar.empty()

    if choice == "Webcam":
        st.title("Webcam Face Recognition")
        st.title("Face Recognition App")
        st.write(WEBCAM_PROMPT)
        #Camera Settings
        cam = cv2.VideoCapture(0)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        FRAME_WINDOW = st.image([])
        
        while True:
            ret, frame = cam.read()
            if not ret:
                st.error("Failed to capture frame from camera")
                st.info("Please turn off the other app that is using the camera and restart app")
                st.stop()
            image, name, id = recognize(frame,TOLERANCE, id_number, firstname)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            #Display name and ID of the person
            
            name_container.info(f"Name: {name}")
            id_container.success(f"ID: {id}")
            FRAME_WINDOW.image(image)


            from PIL import Image
            from io import BytesIO
            import face_recognition
                    # Login button
            if st.button("Login"):
                if int(id_number) == int(id):
                    st.success("Face match found. Access granted.")
                    voting_page(parties)
                
        # recognize(image, TOLERANCE, id_number, password)
                # Capture an image using the webcam
        # cap = cv2.VideoCapture(0)
        # ret, captured_image = cap.read()

        # if not ret:
        #     st.error("Failed to capture image from the camera. Please make sure the camera is working.")
        # else:
        #             # Input fields for ID Number and Password
        #     # id_number = st.text_input("ID Number")
        #     # password = st.text_input("Password", type="password")
                    
        #     if not id_number or not password:
        #         st.error("Please enter both ID Number and Password.")
        #     else:
        #                 # Fetch user record from the database based on the provided ID Number and Password
        #         cursor.execute("SELECT * FROM users_info WHERE id_number = %s AND passwords = %s ", (id_number, password))
        #         users_info = cursor.fetchone()
        #         print(users_info)

        #         if users_info is None:
        #                     st.error("Invalid ID Number or Password. Please try again.")
        #         else:
        #             st.success(f"Logged in as {id_number}")

        #                     # Retrieve the image data from the user_info record
        #             image_data = users_info[14]  # Replace <index_of_image_column> with the actual index of the image column
        #             if image_data:
        #                         # Decode the image data from the database
        #                 stored_image = np.frombuffer(image_data, dtype=np.uint8)
        #                 stored_image = cv2.imdecode(stored_image, cv2.IMREAD_COLOR)

        #                         # Perform face recognition
        #                 captured_face_encoding = face_recognition.face_encodings(captured_image)
        #                 stored_face_encoding = face_recognition.face_encodings(stored_image)

        #                 if captured_face_encoding and stored_face_encoding:
        #                             # Compare the face encodings
        #                     match = face_recognition.compare_faces([stored_face_encoding[0]], captured_face_encoding[0])

        #                     if match[0]:
        #                         st.success("Face match found. Access granted.")
        #                     else:
        #                         st.error("Face match not found. Access denied.")
                            
        #                 else:
        #                         st.error("No image data found in the database. Access denied.")

                    cam.release()  # Release the webcam
                    cv2.destroyAllWindows()  # Close all OpenCV windows
                    conn.close()

    
    
    


            # Perform any additional actions after successful login
            
        







def get_dob_from_id(id_number):
    if len(id_number) == 13:
        # Extract the YYMMDD part from the ID number and convert it to a date
        dob_str = id_number[0:6]
        dob = datetime.datetime.strptime(dob_str, "%y%m%d").date()
        return dob
    else:
        return None
 



  
conn = psycopg2.connect(
    host="localhost",
    port=5430,
    database="food_ordering_system",
    user="postgres"
)

# Create a cursor for database operations
cursor = conn.cursor()

# Create a table to store user registration data if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users_info (
        id_number VARCHAR(13) PRIMARY KEY,
        first_name VARCHAR(250),
        last_name VARCHAR(250),
        dob DATE,
        gender VARCHAR(20),
        race VARCHAR(250),
        age INT,
        phone_number VARCHAR(10),
        province VARCHAR(250),
        ward_number INT,
        password VARCHAR(250),
        address_no VARCHAR(250),
        district VARCHAR(250),
        email VARCHAR(250),
        picture BYTEA
    )
''')
conn.commit()

def registration_page():
    st.title("User Registration")
    
    current_date = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)

    # Set the minimum and maximum dates
    min_date = datetime.date(1900, 1, 1)
    max_date = current_date
    
    # Create a form for the registration page
    with st.form("registration_form"):
        # Input fields for first name, last name, and ID number in the first column
        col1, col2, col3 = st.columns(3)
        first_name = col1.text_input("First Name")
        last_name = col1.text_input("Last Name")
        id_number = col1.text_input("ID Number", max_chars=13)

        # Input fields for date of birth, race, and phone number in the second column
        dob = col2.date_input("Date of Birth", min_value=min_date, max_value=max_date, value=datetime.date.today())
        st.session_state.dob = dob
        race_options = ["White", "Black", "Asian", "Mixed", "Other"]
        race = col2.selectbox("Race", race_options)
        phone_number = col2.text_input("Phone Number", max_chars=10)

        # Input fields for gender, age, provinces, address, district, and ward number in the third column
        gender_options = ["Male", "Female"]
        gender = col3.selectbox("Gender", gender_options)
        age = col3.text_input("Age")
        provinces = ["Eastern Cape", "Free State", "Gauteng", "KwaZulu-Natal", "Limpopo", "Mpumalanga", "Northern Cape", "North West", "Western Cape"]
        province = col3.selectbox("Province", provinces)
        district = col3.text_input("District")
        email = col3.text_input("Email")
        ward_number = col1.text_input("Ward Number")

        # Input fields for email, username, password, and password confirmation
        address = col1.text_input("Address")
        password = col2.text_input("Password", type="password")
        confirm_password = col2.text_input("Confirm Password", type="password")
        
        img_file_buffer = col3.camera_input("Take a picture")
        submitted = st.form_submit_button("Register")
        if img_file_buffer is not None:
            bytes = img_file_buffer.getvalue()
            img = cv2.imdecode(np.frombuffer(bytes, np.uint8), cv2.IMREAD_COLOR)

        # Form submission button
        
        
        
        
        
        
        
        
        
        if submitted:

            if not all([first_name, last_name, id_number, phone_number, email, password, confirm_password, gender, age, dob, race, province, address, district, ward_number]):
                st.error("Please fill in all the fields.")
            elif not is_valid_email(email):
                st.warning("Invalid email format. Please enter a valid email address.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            
            elif not is_valid_password(password):
                st.error("Invalid password. It should be at least 8 characters long and contain at least one digit, one uppercase letter, one lowercase letter, and one special character.")
            elif img_file_buffer is None:
                st.error("Please take a picture for registration.")
            else:
                # Read image file buffer with OpenCV:
                bytes_data1 = img_file_buffer.getvalue()
                picture1 = psycopg2.Binary(bytes_data1)
                
                bytes_data = img_file_buffer.getvalue()
                picture = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                
                if type(picture) != np.ndarray:
                    picture = cv2.imdecode(np.fromstring(picture.read(), np.uint8), 1)
                    
                encoding = frg.face_encodings(picture)[0]
                # encoding = encoding.astype(int)

                # Insert user information into the database
                cursor.execute('''
                    INSERT INTO users_info (
                        id_number,
                        firstname,
                        lastname,
                        dob,
                        gender,
                        race,
                        age,
                        phone_number,
                        province,
                        ward_number,
                        passwords,
                        address_no,
                        district,
                        email,
                        encoding
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                ''', (
                    id_number, first_name, last_name, dob, gender, race, age,
                    phone_number, province, ward_number, password, address,
                    district, email, picture1
                ))
                conn.commit()
                database2 = get_database2()
                
                database2[id_number] = {
                        'encoding':encoding}
                with open(PKL_PATH,'wb') as f:
                    pkl.dump(database2,f)
                return True
                
                
                st.success("Registration successful. User added to the database.")

    conn.close()


 



import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

def display_election_dashboard():
    # Function to fetch data from the database and create DataFrames
    def fetch_data(election_type):
        conn = psycopg2.connect(
            host="localhost",
            port=5430,  # Change the port if necessary
            database="food_ordering_system",
            user="postgres",
        )

        # Create a cursor
        cursor = conn.cursor()

        # Initialize variables to store counts for both local and national elections
        total_registered_voters = 0
        total_votes = 0
        party_votes_data = []

        # Fetch the count of registered voters from the user_info table for both local and national elections
        cursor.execute("SELECT COUNT(*) FROM user_info;")
        total_registered_voters = cursor.fetchone()[0]

        # Fetch the count of votes cast for both local and national elections from the voting_info table
        if election_type == "None":
            cursor.execute("SELECT COUNT(*) FROM votings_info;")
        else:
            cursor.execute("SELECT COUNT(*) FROM votings_info WHERE election_type = %s;", (election_type,))
        total_votes = cursor.fetchone()[0]

        # Fetch party names and their vote counts for both local and national elections from the voting_info table
        if election_type == "None":
            cursor.execute("SELECT party_name, COUNT(*) FROM votings_info GROUP BY party_name;")
        else:
            cursor.execute("SELECT party_name, COUNT(*) FROM votings_info WHERE election_type = %s GROUP BY party_name;", (election_type,))
        party_votes_data = cursor.fetchall()

        # Fetch province, party_name, and vote counts for both local and national elections from the voting_info table
        if election_type == "None":
            cursor.execute("SELECT province, party_name, COUNT(*) FROM votings_info GROUP BY province, party_name;")
        else:
            cursor.execute("SELECT province, party_name, COUNT(*) FROM votings_info WHERE election_type = %s GROUP BY province, party_name;", (election_type,))
        province_party_votes_data = cursor.fetchall()

        # Close the cursor and the connection
        cursor.close()
        conn.close()

        # Create DataFrames
        party_results = pd.DataFrame(party_votes_data, columns=['Party', 'Votes'])
        province_party_results = pd.DataFrame(province_party_votes_data, columns=['Province', 'Party', 'Votes'])

        return total_registered_voters, total_votes, party_results, province_party_results, party_votes_data

    # Streamlit app title
    st.title("Election Dashboard")
    # Add a selector (dropdown) to switch between national, local, and both elections
    election_type = st.selectbox("Select Election Type", ["None", "National", "Local"])

    # Create a layout with three columns
    col1, col2, col3 = st.columns(3)

    # Display registered voters count in the first column
    with col1:
        total_registered_voters, total_votes, party_results, province_party_results, party_votes_data = fetch_data(election_type)
        st.subheader("Registered Voters")
        st.info(f"{total_registered_voters}")

    # Display votes cast count in the second column
    with col2:
        st.subheader("Votes Cast")
        st.info(f"{total_votes}")

    # Calculate and display the vote percentage in the third column
    with col3:
        st.subheader("Total Votes")
        vote_percentage = (total_votes / total_registered_voters) * 100
        st.info(f"{vote_percentage:.2f}%")

    # Create a bar chart for party-wise results using Altair
    col4, col5 = st.columns([1, 2])
    with col4:
        st.subheader("Party-wise Results")

        # Calculate vote percentages
        party_results['Vote Percentage'] = (party_results['Votes'] / total_votes) * 100

        # Create a bar chart for party-wise results using Altair
        chart = alt.Chart(party_results).mark_bar().encode(
            x='Party',
            y='Vote Percentage:Q'
        ).properties(
            width=400,
            height=300
        )

        st.altair_chart(chart)

    # Pivot the province-party results
    province_party_pivot = province_party_results.pivot(index='Party', columns='Province', values='Votes').fillna(0).astype(int)

    # Create a table for province-wise results
    st.header("Province-wise Results")
    st.table(province_party_pivot)
    
   


parties = [
    {
        "name": "African National Congress",
        "president": "Cyril Ramaphosa",
        "logo": "/Users/da_mac_41_/Downloads/African_National_Congress_logo.svg.png",
        "age": 68,
        "education": "LLB, University of South Africa",
    },
    {
        "name": "Democratic Alliance",
        "president": "John Steenhuisen",
        "logo": "/Users/da_mac_41_/Downloads/DA-logo.png",
        "age": 46,
        "education": "BA (Hons), University of Pretoria",
    },
    {
        "name": "Economic Freedom Fighters",
        "president": "Julius Malema",
        "logo": "/Users/da_mac_41_/Downloads/EFF_log.png",
        "age": 40,
        "education": "No formal tertiary qualification",
    },
    {
        "name": "Congress of the People (COPE)",
        "president": "Mosiuoa Lekota",
        "logo": "/Users/da_mac_41_/Downloads/COPE_logo.png",
        "age": 73,
        "education": "LLB, University of the North",
    },
    {
        "name": "United Democratic Movement (UDM)",
        "president": "Bantu Holomisa",
        "logo": "/Users/da_mac_41_/Downloads/UDM_logo.png",
        "age": 66,
        "education": "BA, University of Transkei",
    },
    {
        "name": "Inkatha Freedom Party (IFP)",
        "president": "Mangosuthu Buthelezi",
        "logo": "/Users/da_mac_41_/Downloads/IFP_logo.png",
        "age": 93,
        "education": "BA, University of Fort Hare",
    },
    {
        "name": "African Transformation Movement (ATM)",
        "president": "Vuyolwethu Zungula",
        "logo": "/Users/da_mac_41_/Downloads/ATM_logo.png",
        "age": 35,
        "education": "LLB, University of South Africa",
    },
    {
        "name": "Pan Africanist Congress (PAC)",
        "president": "Narius Moloto",
        "logo": "/Users/da_mac_41_/Downloads/PAC_logo.png",
        "age": 62,
        "education": "LLB, University of South Africa",
    },
]

# def voting_page():
#     st.title("Vote for your Favorite Party")
#     election_page()
#     # Create two columns
#     col1, col2 = st.columns(2)

#     # Display the radio buttons in each column
#     with col1:
#         selected_party_name_col1 = st.radio("Select Party", ["None"] + [party["name"] for party in parties[:len(parties)//2]])

#     with col2:
#         selected_party_name_col2 = st.radio("", ["None"] + [party["name"] for party in parties[len(parties)//2:]])

#     selected_party_name = selected_party_name_col1 if selected_party_name_col1 != "None" else selected_party_name_col2

#     if selected_party_name != "None":
#         selected_party = next((p for p in parties if p["name"] == selected_party_name), None)

#         # Display party information
#         st.subheader(selected_party["name"])
#         st.image(selected_party["logo"], caption=selected_party["name"], width=100)
#         st.write(f"President: {selected_party['president']}")
#         st.write(f"Age: {selected_party['age']}")
#         st.write(f"Educational Background: {selected_party['education']}")

#         # Create a checkbox to confirm the vote
#         vote_confirmed = st.checkbox(f"I confirm my vote for {selected_party['name']}")

#         # Create a submit button
#         submit_button = st.button("Submit Vote")

#         if vote_confirmed and submit_button:
#             # Add your logic to save the vote to the database or backend here
#             st.success(f"You voted for {selected_party['name']}!")

conn = psycopg2.connect(
    host="localhost",
    port=5430,
    database="food_ordering_system",
    user="postgres",

)


# Create a cursor object
cursor = conn.cursor()

# Create a table for storing user information
create_table_query = '''
    CREATE TABLE IF NOT EXISTS user_info (
        user_id SERIAL PRIMARY KEY,
        hour TIMESTAMP,
        dates DATE,
        province VARCHAR(250),
        party_name VARCHAR(250),
        election_type VARCHAR(250)
        
        
        
    )
'''
cursor.execute(create_table_query)
conn.commit()

##from datetime import datetime
def voting_page(parties):
    st.title("Vote for your Favorite Party")

    # Get the selected election type from the Election Page
    election_type = st.selectbox("Select Election Type", ["National", "Local"])

    if election_type == "National":
        st.header("National Elections")
        # Include national election results here
    else:
        st.header("Local Elections")
        
    province_type = st.selectbox("Select Province", ["Eastern Cape", "Free State", "Gauteng","Kwazulu-Natal", "Limpopo","Mpumalanga","North West","Northern Cape","Western Cape"])


    col1, col2 = st.columns(2)

    # Display the radio buttons in each column
    with col1:
        selected_party_name_col1 = st.radio("Select Party", [party["name"] for party in parties[:len(parties)]])

    selected_party_name = selected_party_name_col1
    if selected_party_name != "None":
        selected_party = next((p for p in parties if p["name"] == selected_party_name), None)

        # Display party information
        st.subheader(selected_party["name"])
        st.image(selected_party["logo"], caption=selected_party["name"], width=100)
        st.write(f"President: {selected_party['president']}")
        st.write(f"Age: {selected_party['age']}")
        st.write(f"Educational Background: {selected_party['education']}")

        # Create a checkbox to confirm the vote
        vote_confirmed = st.checkbox(f"I confirm my vote for {selected_party['name']}")

        # Create a submit button
        submit_button = st.button("Submit Vote")

        if vote_confirmed and submit_button:
            # Add your logic to save the vote to the database or backend here

            # Get the current date and time
            hour = datetime.now()
            dates = datetime.now().date()

            # Insert the vote information into the database
            insert_vote_query = '''
                INSERT INTO votings_info (hour, dates,province,party_name,election_type)
                VALUES (%s,%s, %s,%s, %s)
            '''
            cursor.execute(insert_vote_query, (hour, dates,province_type,selected_party_name, election_type))
            conn.commit()

            st.success(f"You voted for {selected_party['name']}!")

    # if selected_election_type:
    #     # Get the current date and time
    #     vote_time = datetime.now()
    #     vote_date = datetime.now().date()

    #     # Insert the election type into the database
    #     insert_election_query = '''
    #         INSERT INTO user_info (election_type, vote_time, vote_date)
    #         VALUES (%s, %s, %s)
    #     '''
    #     cursor.execute(insert_election_query, (selected_election_type, vote_time, vote_date))
    #     conn.commit()
        
        
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("", ("Home","Login", "Register","Vote","view"))
    
    if page == "Home":
        homepage()
        
    elif page == "Login":
        login_page()
        
    elif page == "Register":
        registration_page()
        
        
    # elif page == "Record":
    #     record_audio()
    
    # elif page == "Election":
    #     election_page()
    
    elif page == "Vote":
        voting_page(parties)
    
    elif page == "view":   
         display_election_dashboard()
    
     

if __name__ == "__main__":
    main()
