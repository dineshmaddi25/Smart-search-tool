import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from difflib import get_close_matches

# URL of the page to scrape (with pagination)
url = "https://courses.analyticsvidhya.com/collections?page={}"

@st.cache_data(show_spinner=False)
def scrape_all_courses():
    """Scrape all pages and cache the result"""
    all_courses = []
    for page in range(1, 9):  # Assuming there are 8 pages
        response = requests.get(url.format(page))
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        courses = soup.find_all('a', class_='course-card course-card__public published')

        for course in courses:
            title = course.find('h3').text.strip()
            category = course.find('h4').text.strip()
            reviews = course.find('span', class_='review__stars-count').text if course.find('span', class_='review__stars-count') else "No reviews"
            rating = len(course.find_all('i', class_='fa-star')) if course.find_all('i', class_='fa-star') else 0
            lessons = course.find('span', class_='course-card__lesson-count').text if course.find('span', class_='course-card__lesson-count') else "No lessons"
            price = course.find('span', class_='course-card__price').text.strip() if course.find('span', class_='course-card__price') else "Unknown price"
            img_url = course.find('img', class_='course-card__img')['src']
            link = course['href']

            all_courses.append({
                "Title": title,
                "Category": category,
                "Reviews": reviews,
                "Rating": rating,
                "Lessons": lessons,
                "Price": price,
                "Image": img_url,
                "Link": link
            })
    return pd.DataFrame(all_courses)

def display_courses(df):
    """Display course data in a responsive grid layout with hover effects"""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

        body {
            font-family: 'Poppins', sans-serif;
            background-color: #f0f4f8;
        }

        /* Modern gradient background for the entire app */
        .block-container {
            padding-top: 30px;
            padding-bottom: 30px;
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            border-radius: 20px;
        }

        /* Card container for smooth animations and modern shadow effects */
        .course-card {
            border: 0;
            padding: 20px;
            margin: 15px;
            border-radius: 15px;
            text-align: center;
            display: inline-block;
            width: 100%;
            max-width: 330px;
            background: #fff;
            transition: transform 0.4s ease-in-out, box-shadow 0.4s ease-in-out;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            height: 100%;
        }

        /* Make the cards more interactive with hover animations */
        .course-card:hover {
            transform: translateY(-10px) scale(1.03);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
        }

        /* Image settings for courses */
        .course-card img {
            width: 100%;
            height: 180px;
            object-fit: cover;
            border-radius: 10px;
            transition: transform 0.4s ease-in-out;
        }

        /* Add a zoom effect on image hover */
        .course-card:hover img {
            transform: scale(1.1);
        }

        /* Style the headings with gradient colors */
        .course-card h3 {
            background: -webkit-linear-gradient(45deg, #007BFF, #00FFCC);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 600;
            margin-bottom: 10px;
        }

        /* Styling the course details */
        .course-card p {
            color: #4d4d4d;
            font-size: 15px;
            margin: 10px 0;
        }

        /* Style for buttons and links */
        .course-card a {
            text-decoration: none;
            color: #007BFF;
            font-weight: 500;
        }

        .course-card a:hover {
            text-decoration: underline;
            color: #004080;
        }

        /* Style the search bar with rounded corners and a sleek look */
        input[type="text"] {
            border-radius: 25px;
            border: 1px solid #d6d6d6;
            padding: 10px;
            width: 100%;
            max-width: 500px;
        }

        /* Style for the sidebar */
        .css-1d391kg {
            background-color: #007BFF !important;
            color: #ffffff !important;
            border-radius: 25px !important;
        }

        /* Make the sidebar headers visually appealing */
        .css-1v3fvcr {
            color: #ffffff !important;
            text-align: center;
        }

        /* Style for the page title */
        .st-bc {
            font-size: 36px;
            font-weight: 700;
            color: #ffffff;
            background: -webkit-linear-gradient(45deg, #7b61ff, #e34ca0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding-bottom: 20px;
            text-align: center;
        }

        </style>
        """, unsafe_allow_html=True
    )

    cols = st.columns(3)  # Three columns for cards
    for idx, row in df.iterrows():
        col = cols[idx % 3]  # Select the current column
        temp = row['Link']  # Extract the relative link
        link = f"https://courses.analyticsvidhya.com{temp}"
        with col:
            st.markdown(
                f"""
                <div class="course-card">
                    <a href="{link}" target="_blank">
                        <img src="{row['Image']}" alt="{row['Title']}"/>
                        <h3>{row['Title']}</h3>
                    </a>
                    <p><strong>Category:</strong> {row['Category']}</p>
                    <p><strong>Reviews:</strong> {row['Reviews']} | <strong>Rating:</strong> {'★' * row['Rating']}{'☆' * (5 - row['Rating'])}</p>
                    <p><strong>Lessons:</strong> {row['Lessons']}</p>
                    <p><strong>Price:</strong> {row['Price']}</p>
                </div>
                """, unsafe_allow_html=True
            )

# Function to provide search suggestions
def get_search_suggestions(query, courses):
    """Return course titles similar to the query"""
    return get_close_matches(query, courses['Title'].tolist(), n=5, cutoff=0.3)

# Main Streamlit app
def app():
    st.markdown("""
        <style>
        .st-bc {
            font-size: 36px;
            font-weight: 700;
            color: #ffffff;
            padding-bottom: 20px;
        }

        .css-1q1n0ol {
            color: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🚀 Course Search - Analytics Vidhya")

    # Load the data once and cache it
    courses_df = scrape_all_courses()

    # Sidebar for navigation
    st.sidebar.header("✨ Filter Courses")
    nav_options = ["All Courses", "Free Courses", "Paid Courses"]
    selected_option = st.sidebar.radio("Select Course Type", nav_options)

    # Filter courses based on selected option
    if selected_option == "Free Courses":
        filtered_courses = courses_df[courses_df['Price'] == "Free"]
    elif selected_option == "Paid Courses":
        filtered_courses = courses_df[courses_df['Price'] != "Free"]
    else:
        filtered_courses = courses_df

    # Search bar with auto-suggestions
    query = st.text_input("🔍 Search for a course", placeholder="Type course name...")

    if query:
        # Provide search suggestions
        suggestions = get_search_suggestions(query, filtered_courses)
        if suggestions:
            st.write("Did you mean:")
            for suggestion in suggestions:
                st.markdown(f"- {suggestion}")

        # Filter based on query
        filtered_courses = filtered_courses[filtered_courses['Title'].str.contains(query, case=False)]

        if filtered_courses.empty:
            st.write("No courses found matching your search query.")
    else:
        st.write("Showing all courses.")

    # Display courses
    display_courses(filtered_courses)

# Run the Streamlit app
if __name__ == "__main__":
    app()
