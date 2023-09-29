import streamlit as st
import datetime
import re
from datetime import date
import random
import numpy as np
import wave
import io
from twilio.rest import Client
import sounddevice as sd
import face_recognition
import cv2
from streamlit_webrtc import VideoTransformerBase, webrtc_streamer


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

    # Input fields for username and passworda
    username = st.text_input("ID Number")
    password = st.text_input("Password", type="password")

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



    # Login button
    if st.button("Login"):
        # Perform authentication checks
        if not username or not password:
            st.error("Please enter both username and password.")
            
        elif username not in registered_users:
            st.error("Username not found. Please register first.")
        elif registered_users[username] != password:
            st.error("Invalid password. Please try again.")
        else:
            st.success("Login successful!")
            # Perform any additional actions after successful login
            
            
# ... (Other parts of the code)

# Face Recognition VideoTransformer


registered_users = {
    "id_number": {
        "password": "password123",
        "profile_image": None,
    },
    # Add more registered users as needed
}



# Face Recognition VideoTransformer
class FaceRecognitionTransformer(VideoTransformerBase):
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        if registered_users["id_number"]["profile_image"] is not None:
            # Load the known profile image for face recognition
            known_image = face_recognition.load_image_file(registered_users["id_number"]["profile_image"])
            known_face_encoding = face_recognition.face_encodings(known_image)[0]
            self.known_face_encodings.append(known_face_encoding)
            self.known_face_names.append("id_number")

    def transform(self, frame):
        # Convert the frame to RGB format for face recognition
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare the current face encoding with the known face encoding
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            if True in matches:
                name = self.known_face_names[matches.index(True)]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        return frame





def registration_page():
    st.title("User Registration")

    # Create a form for the registration page
    with st.form("registration_form"):
        # Input fields for first name, last name, and ID number in the first column
        col1, col2, col3 = st.columns(3)
        first_name = col1.text_input("First Name")
        last_name = col1.text_input("Last Name")
        id_number = col1.text_input("ID Number", max_chars=13)

        # Input fields for date of birth, race, and phone number in the second column
        dob = col2.date_input("Date of Birth", datetime.date.today())
        race_options = ["White", "Black", "Asian", "Mixed", "Other"]
        race = col2.selectbox("Race", race_options)
        phone_number = col2.text_input("Phone Number", max_chars=10)

        # Input fields for gender, age, provinces, address, district, and ward number in the third column
        gender_options = ["Male", "Female"]
        gender = col3.selectbox("Gender", gender_options)
        age = col3.number_input("Age", min_value=0, max_value=120, step=1)
        provinces = ["Eastern Cape", "Free State", "Gauteng", "KwaZulu-Natal", "Limpopo", "Mpumalanga", "Northern Cape", "North West", "Western Cape"]
        province = col3.selectbox("Province", provinces)
        address = col3.text_input("Address")
        district = col3.text_input("District")
        ward_number = col1.text_input("Ward Number")
        

        # Input fields for email, username, password, and password confirmation
        email = col1.text_input("Email")
        # username = col1.text_input("Username")
        password = col2.text_input("Password", type="password")
        confirm_password = col2.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register")
        if submitted:
            if not all([first_name, last_name, id_number, phone_number, email, password, confirm_password, gender, age, dob, race, province, address, district, ward_number]):
                st.error("Please fill in all the fields.")
            elif not is_valid_email(email):
                st.warning("Invalid email format. Please enter a valid email address.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            
            elif not is_valid_password(password):
                st.error("Invalid password. It should be at least 8 characters long and contain at least one digit, one uppercase letter, one lowercase letter, and one special character.")
            else:
                # Store the user information in the registered_users dictionary
                registered_users[first_name.lower() + "_" + last_name.lower()] = {
                    "Password": password,
                    "ID Number": id_number,
                    "Phone Number": phone_number,
                    "Email": email,
                    "Gender": gender,
                    "Age": age,
                    "Date of Birth": dob,
                    "Race": race,
                    "Province": province,
                    "Address": address,
                    "District": district,
                    "Ward Number": ward_number,
                    # Add more user information as needed
                }
       
    # record_audio_button = st.button("Record Audio")
    # audio_data = None
    
    st.subheader("Voice Recognition")
    record_audio_button = st.button("Record Audio")
    audio_data = None
    if record_audio_button:
        with st.spinner("Recording..."):
            audio_data = record_audio()

    # Display the audio data as a waveform (optional)
    if audio_data is not None:
        st.write("Recorded Audio:")
        st.audio(audio_data, format="audio/wav")



# Function to record audio using sounddevice
def record_audio(sample_rate=44100, duration=5):
    # st.subheader("Voice Recognition")
    audio_data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()
    return audio_data.tobytes()


def face_recognition_page():
    st.subheader("Face Recognition")

    # Display the webcam video with face recognition
    webrtc_ctx = webrtc_streamer(
        key="face-recognition",
        video_transformer_factory=FaceRecognitionTransformer,
        async_transform=True,
    )

    # Button to take a picture and save it
    if st.button("Take Picture") and webrtc_ctx.video_transformer:
        # Save the current frame as the profile image for face recognition
        frame = webrtc_ctx.video_transformer.last_frame
        if frame is not None:
            image_path = "id_number.jpg"  # Replace with the appropriate file path
            cv2.imwrite(image_path, frame[:, :, ::-1])  # Save the image in RGB format
            registered_users["id_number"]["profile_image"] = image_path
            st.success("Profile image saved.")

    # Registration button
    # if st.button("Register"):
    #     # Your registration logic goes here
    #     st.success("User registered successfully!")
election = [
    {
        "name": "National",
        "Date": "Election open date is 05/09/2024",
        
    },
    {
      "name": "Provincial",
      "Date": "Election open date is 02/05/2024",  
    }
    ],
def local_elections():
    st.subheader("Local Elections")
    # st.write("List of upcoming local elections:")
    # ... (Your existing local_elections function code goes here)
    pass

def national_elections():
    st.subheader("National Elections")
    # st.write("List of upcoming national elections:")
    # ... (Your existing national_elections function code goes here)
    pass

# def election_page():
#     st.title("Upcoming Elections")

#     # Create radio buttons for choosing between Local and National elections
#     election_type = st.radio("Select Election Type", ["Local", "National"])

#     # Create a button to submit the user's election type selection
#     if st.button("Submit"):
#         st.write(f"Selected Election Type: {election_type}")

#         # Display the list of elections based on the selected type
#         # if election_type == "Local":
#         #     local_elections()
#         # elif election_type == "National":
#         #     national_elections()
            
def election_page():
    st.title("Election Page")

    # Fixed dates for National and Provincial elections
    national_election_date = date(2024, 9, 24)
    provincial_election_date = date(2024, 9, 24)

    # Radio buttons for election type (National or Provincial)
    election_type = st.radio("Select Election Type:", ("National", "Provincial"))

    # Display the open date based on the selected election type
    if election_type == "National":
        st.write(f"The open date for National Election is on {national_election_date.strftime('%d %B %Y')}.")
    elif election_type == "Provincial":
        st.write(f"The open date for Provincial Election is on {provincial_election_date.strftime('%d %B %Y')}.")

    # Submit button
    if st.button("Submit"):
        if election_type:
            # Store the selected date and election type in a dictionary
            election_details = {
                "Election Type": election_type,
                "Open Date": national_election_date if election_type == "National" else provincial_election_date
            }
            st.success("Election details submitted successfully!")
            st.write("Selected Election Type:", election_type)
            st.write("Selected Open Date:", election_details["Open Date"].strftime('%d %B %Y'))
        else:
            st.warning("Please select the Election Type.")



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
        "name": "Pan Africanist Congress of Azania (PAC)",
        "president": "Narius Moloto",
        "logo": "/Users/da_mac_41_/Downloads/PAC_logo.png",
        "age": 62,
        "education": "LLB, University of South Africa",
    },
]

def voting_page():
    st.title("Vote for your Favorite Party")

    # Create two columns
    col1, col2 = st.columns(2)

    # Display the radio buttons in each column
    with col1:
        selected_party_name_col1 = st.radio("Select Party", ["None"] + [party["name"] for party in parties[:len(parties)//2]])

    with col2:
        selected_party_name_col2 = st.radio("", ["None"] + [party["name"] for party in parties[len(parties)//2:]])

    selected_party_name = selected_party_name_col1 if selected_party_name_col1 != "None" else selected_party_name_col2

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
            st.success(f"You voted for {selected_party['name']}!")



def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("", ("Home","Login", "Register","Election","Vote"))
    
    if page == "Home":
        homepage()
        
    elif page == "Login":
        login_page()
        
    elif page == "Register":
        registration_page()
        face_recognition_page()
        
    elif page == "Record":
        record_audio()
    
    elif page == "Election":
        election_page()
    
    elif page == "Vote":
        voting_page()
      
     

if __name__ == "__main__":
    main()
