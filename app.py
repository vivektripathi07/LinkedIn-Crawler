# app.py
import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import ast

st.set_page_config(page_title="LinkedIn Job Insights", layout="wide")
st.title("🔍 LinkedIn Job Data Insights Dashboard")
st.markdown("### Analyzing job postings from LinkedIn")

# =================== Load & Clean Data ===================
@st.cache_data
def load_data():
    df = pd.read_csv('check.csv')
    df.columns = df.columns.str.strip()  # Clean column names
    return df

df = load_data()

# Parse Job Meta Data
@st.cache_data
def parse_metadata(df):
    def safe_eval(x):
        try:
            return ast.literal_eval(x)
        except:
            return []

    df['Parsed_Meta'] = df['Job Meta Data'].apply(safe_eval)

    # Extract fields
    def extract_location(meta):
        for item in meta:
            if ',' in item and ('India' in item or 'Area' in item):
                return item.strip()
        return 'Not Specified'

    def extract_posted_time(meta):
        for item in meta:
            if 'ago' in item or 'reposted' in item:
                return item.strip()
        return 'Not Specified'

    def extract_applicants(meta):
        for item in meta:
            if 'applicants' in item or 'clicked apply' in item:
                return item.strip()
        return 'Not Specified'

    def extract_work_type(meta):
        if 'Remote' in meta: return 'Remote'
        if 'Hybrid' in meta: return 'Hybrid'
        if 'On-site' in meta: return 'On-site'
        return 'Not Specified'

    def extract_job_type(meta):
        return 'Internship' if 'Internship' in meta else 'Full-time'

    df['Location'] = df['Parsed_Meta'].apply(extract_location)
    df['Posted_Time'] = df['Parsed_Meta'].apply(extract_posted_time)
    df['Applicants'] = df['Parsed_Meta'].apply(extract_applicants)
    df['Work_Type'] = df['Parsed_Meta'].apply(extract_work_type)
    df['Job_Type'] = df['Parsed_Meta'].apply(extract_job_type)

    return df

df = parse_metadata(df)

# =================== Tech Stack Extraction ===================
tech_keywords = [
    'Python', 'Java', 'JavaScript', 'React', 'Vue', 'Node.js', 'PHP', 'C++', 'C#', 'Go', 'Golang',
    'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Kafka', 'Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure',
    'Git', 'CI/CD', 'Linux', 'TensorFlow', 'PyTorch', 'Spring Boot', 'Angular', 'TypeScript',
    'HTML', 'CSS', 'Microservices', 'REST', 'GraphQL', 'Agile', 'Scrum', 'DevOps', 'ML', 'AI',
    'LLM', 'Langchain', 'Prompt Engineering', 'GAN', 'VAE'
]

def extract_technologies(text):
    found = []
    for tech in tech_keywords:
        if re.search(r'\b' + re.escape(tech) + r'\b', str(text), re.IGNORECASE):
            found.append(tech)
    return list(set(found))

df['Technologies'] = df['Job Details'].apply(extract_technologies)
all_techs = [tech for tech_list in df['Technologies'] for tech in tech_list]
tech_counts = Counter(all_techs)

# =================== Experience Extraction ===================
def extract_experience(text):
    matches = re.findall(r'(\d+)\+\s*years|(\d+)\s+years', str(text), re.IGNORECASE)
    if matches:
        nums = [int(m[0]) if m[0] else int(m[1]) for m in matches]
        return max(nums) if nums else None
    return None

df['Max_Experience_Years'] = df['Job Details'].apply(extract_experience)

# =================== Dashboard Layout ===================
st.sidebar.header("📊 Dashboard Filters")
selected_location = st.sidebar.multiselect(
    "Filter by Location",
    options=df['Location'].unique(),
    default=[]
)
selected_company = st.sidebar.multiselect(
    "Filter by Company",
    options=df['Company Name'].unique(),
    default=[]
)
selected_work_type = st.sidebar.multiselect(
    "Filter by Work Type",
    options=df['Work_Type'].unique(),
    default=[]
)

# Apply filters
if selected_location:
    df = df[df['Location'].isin(selected_location)]
if selected_company:
    df = df[df['Company Name'].isin(selected_company)]
if selected_work_type:
    df = df[df['Work_Type'].isin(selected_work_type)]

# Summary Metrics
st.header("📌 Summary Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Jobs", len(df))
col2.metric("Unique Companies", df['Company Name'].nunique())
col3.metric("Most Common Work Mode", df['Work_Type'].mode()[0] if not df['Work_Type'].mode().empty else "N/A")
col4.metric("Top Tech Skill", tech_counts.most_common(1)[0][0] if tech_counts else "N/A")

# Charts
st.markdown("---")
st.header("📈 Visual Insights")

fig_cols = st.columns(2)

# 1. Top Companies
with fig_cols[0]:
    top_companies = df['Company Name'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x=top_companies.values, y=top_companies.index, ax=ax, palette='Blues_d')
    ax.set_title('Top 10 Hiring Companies')
    ax.set_xlabel('Number of Jobs')
    st.pyplot(fig)

# 2. Work Type
with fig_cols[1]:
    work_type_counts = df['Work_Type'].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(work_type_counts, labels=work_type_counts.index, autopct='%1.1f%%', startangle=90)
    ax.set_title('Work Mode Distribution')
    st.pyplot(fig)

# 3. Job Type (Full-time vs Internship)
st.markdown("---")
job_type_col, tech_col = st.columns(2)

with job_type_col:
    job_type_counts = df['Job_Type'].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(job_type_counts, labels=job_type_counts.index, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff'])
    ax.set_title('Job Type Distribution')
    st.pyplot(fig)

# 4. Top Technologies Word Cloud
with tech_col:
    if tech_counts:
        wordcloud = WordCloud(width=400, height=300, background_color='white', colormap='viridis').generate_from_frequencies(tech_counts)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Most In-Demand Technologies')
        st.pyplot(fig)
    else:
        st.write("No technology data to display.")

# 5. Experience Requirements
st.markdown("---")
exp_col, loc_col = st.columns(2)

with exp_col:
    exp_data = df['Max_Experience_Years'].dropna()
    if len(exp_data) > 0:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(exp_data, bins=10, kde=True, ax=ax, color='green')
        ax.set_title('Max Experience Required (Years)')
        ax.set_xlabel('Years of Experience')
        st.pyplot(fig)
    else:
        st.write("No experience data found.")

# 6. Top Locations
with loc_col:
    top_locs = df['Location'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(6, 4))
    top_locs.plot(kind='barh', ax=ax, color='skyblue')
    ax.set_title('Top Job Locations')
    ax.set_xlabel('Number of Jobs')
    st.pyplot(fig)

# 7. Recent Postings
st.markdown("---")
st.header("📅 Recently Posted Jobs")
recent_jobs = df[['Job Title', 'Company Name', 'Location', 'Posted_Time']].head(10)
st.dataframe(recent_jobs, use_container_width=True)

# Optional: Download enriched data
st.markdown("---")
st.markdown("### 💾 Download Processed Data")
@st.cache_data
def convert_df(x):
    return x.to_csv(index=False).encode('utf-8')

csv = convert_df(df[['Company Name', 'Job Title', 'Location', 'Work_Type', 'Job_Type', 'Technologies', 'Max_Experience_Years']])
st.download_button("Download CSV", csv, "linkedin_jobs_processed.csv", "text/csv")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | Data sourced from LinkedIn")