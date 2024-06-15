import streamlit as st
import joblib
import pandas as pd

# Set the app to wide mode
st.set_page_config(layout="wide")

# Load the trained model
model = joblib.load('decision_tree_model.pkl')

# Define the Person class for BMI, BMR, and calorie calculations
class Person:
    def __init__(self, age, height, weight, gender, activity):
        self.age = age
        self.height = height
        self.weight = weight
        self.gender = gender
        self.activity = activity
        self.height_m = height / 100  # Convert height from cm to meters
        self.bmi_calculated = self.weight / (self.height_m ** 2)

    def calculate_bmi(self):
        bmi = round(self.weight / ((self.height / 100) ** 2), 2)
        return bmi

    def display_result(self):
        bmi = self.calculate_bmi()
        bmi_string = f'{bmi} kg/m²'
        if bmi < 18.5:
            category = 'Underweight'
            color = 'Red'
        elif 18.5 <= bmi < 25:
            category = 'Normal'
            color = 'Green'
        elif 25 <= bmi < 30:
            category = 'Overweight'
            color = 'Yellow'
        else:
            category = 'Obesity'
            color = 'Red'
        return bmi_string, category, color

    def calculate_bmr(self):
        if self.gender == 'Male':
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
        return bmr

    def calories_calculator(self):
        activities = ['Little/no exercise', 'Light exercise', 'Moderate exercise (3-5 days/wk)', 'Very active (6-7 days/wk)', 'Extra active (very active & physical job)']
        weights = [1.2, 1.375, 1.55, 1.725, 1.9]
        weight_factor = weights[activities.index(self.activity)]
        maintain_calories = self.calculate_bmr() * weight_factor
        return maintain_calories

# Define the user interface
st.title("Obesity and Waist Size Risk Score Prediction")

# Input fields
age = st.number_input("Age", min_value=1, max_value=100, value=25)
waist = st.number_input("Waist (cm)", min_value=30, max_value=200, value=80)
weight = st.number_input("Weight (kg)", min_value=10, max_value=300, value=70)
height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)

# Zone selection
zone = st.selectbox("Zone", options=["N", "S", "E", "W", "NW", "NE", "SW", "SE"])

# Gender selection
gender = st.selectbox("Gender", options=["Male", "Female"])

# Physical activity inputs
moderate_activity = st.slider("Moderate Physical Activity (level)", min_value=0, max_value=6, value=1)
vigorous_activity = st.slider("Vigorous Physical Activity (level)", min_value=0, max_value=6, value=1)
daily_activity = st.slider("Daily Physical Activity (level)", min_value=0, max_value=6, value=1)

# Predict button
if st.button("Predict"):
    # Calculate BMI
    person = Person(age, height, weight, gender, 'Moderate exercise (3-5 days/wk)')  # For calorie calculations
    height_m = height / 100
    bmi_calculated = weight / (height_m ** 2)

    # Create a DataFrame for the input data
    input_data = pd.DataFrame({
        'Age': [age],
        'Waist': [waist],
        'Weight': [weight],
        'Height': [height],
        'Zone': [zone],
        'Gender': [gender],
        'Moderatephysicalactivity': [moderate_activity],
        'Vigorousphysicalactivity': [vigorous_activity],
        'Dailyphysicalactivity': [daily_activity],
        'Bmi_calculated': [bmi_calculated]
    })

    # Perform the prediction
    prediction = model.predict(input_data)
    risk_score = prediction[0]

    # Determine risk category and color
    if risk_score == 0:
        risk_category = 'Insufficient weight'
        risk_color = 'Blue'
    elif risk_score == 1:
        risk_category = 'Normal weight'
        risk_color = 'Green'
    elif risk_score == 2:
        risk_category = 'Overweight'
        risk_color = 'Yellow'
    elif risk_score == 3:
        risk_category = 'Obesity Type 1'
        risk_color = 'Orange'
    elif risk_score == 4:
        risk_category = 'Obesity Type 2'
        risk_color = 'Red'
    else:
        risk_category = 'Obesity Type 3'
        risk_color = 'Dark Red'

    # Display the prediction result
    st.write(f"The predicted Obesity and Waist Size Risk Score is: {risk_score}")
    new_title = f'<p style="font-family:sans-serif; color:{risk_color}; font-size: 25px;">{risk_category}</p>'
    st.markdown(new_title, unsafe_allow_html=True)

    # Display BMI result
    st.header('BMI Calculator')
    bmi_string, bmi_category, bmi_color = person.display_result()
    st.metric(label="Body Mass Index (BMI)", value=bmi_string)
    new_title = f'<p style="font-family:sans-serif; color:{bmi_color}; font-size: 25px;">{bmi_category}</p>'
    st.markdown(new_title, unsafe_allow_html=True)
    st.markdown("Healthy BMI range: 18.5 kg/m² - 25 kg/m².")

    # Display calories calculator result
    st.header('Calories Calculator')
    maintain_calories = person.calories_calculator()
    st.write('The results show a number of daily calorie estimates that can be used as a guideline for how many calories to consume each day to maintain, lose, or gain weight at a chosen rate.')
    plans = ["Maintain weight", "Mild weight loss", "Weight loss", "Extreme weight loss"]
    weights = [1, 0.9, 0.8, 0.6]
    losses = ['-0 kg/week', '-0.25 kg/week', '-0.5 kg/week', '-1 kg/week']
    for plan, weight_factor, loss, col in zip(plans, weights, losses, st.columns(4)):
        with col:
            st.metric(label=plan, value=f'{round(maintain_calories * weight_factor)} Calories/day', delta=loss, delta_color="inverse")

