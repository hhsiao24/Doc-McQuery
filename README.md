<img height="250" alt="image" src="https://github.com/user-attachments/assets/a52c4794-3970-456a-883c-6821004fbd08" />

# Welcome to Doc McQuery!
# 🦛 Inspiration
In medicine, knowledge is constantly evolving as new conditions are discovered and innovative treatments are developed. Case studies, which are detailed examinations of individual or group patient cases, are one of the richest sources of this evolving knowledge. However, busy healthcare professionals often lack the time to sift through and analyze these studies in detail. Inspired to bridge this gap, we created Doc McQuery, a service designed to streamline the search for relevant case studies, synthesize their insights, and deliver them efficiently. In addition to searching for case studies in reputable medical sources, such as PubMed, we analyze all the electronic medical records (EMRs) within the hospital to find any similar cases, providing health care professionals with as much information in as little time as possible. By reducing the time doctors spend searching, Doc McQuery empowers them to focus more on personalized patient care and make better informed clinical decisions.

# 🦛 What it does
After selecting their hospital and logging in, the user (health professional) can select the desired patient from a list of patients and input any relevant information they observed from this visit, such as symptoms, diagnoses, etc. Doc McQuery then returns a summary of the top three relevant case studies taken from reputable medical sources such as PubMed, as well as a summary of medical reports of similar patients at that hospital. 

# 🦛 How we built it
## Backend
### 1. Database
We used a PostgreSQL database to store all the patients’ EMRs. Because we do not have access to patient medical records, we used Synthea to generate 1000 simulated patient records. In order for us to more easily compare EMRs, we embedded relevant parts of their EMR that tell us about their condition with the Sentence Transformers framework. 

### 2. Parsing User Input
The user is initially prompted to enter any information they would like about the patient. To best utilize this information, we parse the user input by giving the input to the OpenAI API, which sorts the information into categories: conditions, symptoms, medications, treatments, and diagnoses. 

### 3. Summarizing Patient's EMR
Using the populated database, we extract basic information about the patient (ID, name, gender, age, etc.) as well as past conditions, symptoms, and observations. We then utilize the OpenAI API to summarize the data, providing a concise description of the patient’s history.

### 4. Accessing Case Study Summaries
By combining the user inputs and the patient’s EMR summary as an input, we utilize the OpenAI API to generate a query that we use to parse through PubMed. With this query, we prompt the NIH API to find the most relevant case studies. However, when parsing through the articles, we have to be careful about our algorithm being too strict and looking for articles where every keyword is included, as this could lead to no results being found. To combat this challenge, we parse through PubMed in tiers. Tier 1 is the strictest in which most of the keywords should be included, followed by Tier 2 where demographic information is excluded from the query. In Tier 3, the treatments are also dropped, and Tier 4 only includes conditions and a couple of symptoms. For optimal performance, we stop at the first tier in which we find three relevant articles and store the PubMed IDs for all three articles. Then, we utilize the OpenAI API to summarize these three articles, providing a snapshot into the demographics, conditions, symptoms, treatments, diagnoses, and results of patients in these case studies. 

### 5. Accessing Relevant EMRs
We also find the most relevant patients within the hospital’s database of EMRs so that healthcare professionals can seamlessly consult in-house experts at their own hospital. To do this, we take in the same patient ID and user input used to generate case study summaries. The user input is passed to the OpenAI API, which creates an array of individual symptoms mentioned. For each symptom, we embed it and compare it to all embedded observations in the database, extracting the k1 most similar patients. With this master list, we then rank similarities based on the patient demographics and return the k2 most similar patients. Finally, we summarize and return each patient’s EMR with the same logic used in the PubMed query flow. 

### 6. Flask
The Flask API connects the frontend and backend, allowing the user to input relevant information about a patient. We utilized POST requests to get the patient information and details and GET requests to send back the case study and similar EMR summaries. 

## Frontend
We use React to create a web application that allows the user to log in to their hospital, after which they can select a patient from a drop down menu and fill out a search query with relevant information about the patient’s current state (symptoms, observations, etc.). The query returns two results: a summary of the three most relevant case studies and a summary of similar medical reports from other patients in the hospital. The user is also given an option to search again.

# 🦛 Challenges we ran into
When parsing PubMed articles, we initially faced a challenge: many searches returned no relevant case studies. We discovered this was because our algorithm was too strict, requiring all keywords to appear in an article. To address this, we developed a four-tier system that progressively relaxes query requirements. Tier 1 is the strictest, including most keywords. Tier 2 removes demographic constraints, Tier 3 drops treatment-related keywords, and Tier 4 is the most flexible, using only conditions and a limited number of symptoms. This approach ensures we balance precision with breadth, improving the likelihood of finding useful case studies.

When we initially compared the embeddings of the user input to embedded observations in the database, we received a homogenous list of patients. The results tended to hyperfocus on a singular symptom mentioned by the user. Since we want a varied, and hopefully more accurate, list of patients, we changed our logic to instead compare each symptom to our database and create a master list of the most similar patients. This provides a more holistic representation of what patients in the hospital would most likely be similar to the patient being currently treated.

# 🦛 Accomplishments that we're proud of
This was our first time working with technologies such as text embedding and API endpoints, and we are proud of the work we did to use these technologies to create a web app to solve a real-world problem. We leveraged the Sentence Transformers library to create embeddings that lift a text string into a higher-dimensional vector space. We also used the OpenAI and NIH APIs to build queries and engineer prompts summarize case studies and patient EMRs.

Since our web app employs multiple microservices, we created a Docker container to centralize resources and simplify the set up process. The Docker container makes the application portable and easy to deploy on any machine.

# 🦛 What we learned
While creating the app, we learned how to use embedding algorithms to analyze the similarity of complex text data. We also integrated several APIs: we used OpenAI to generate queries and summarize search results, and we used the NIH API to find case studies pertinent to the selected patient. 

# 🦛 What's next for Doc McQuery
We hope to expand Doc McQuery’s knowledge and capabilities by giving it access to sources beyond those on PubMed. To allow Doc McQuery to search a vast library of information, we would like to incorporate retrieval augmented generation technology to enhance the accuracy and relevance of the results. We would also like to add features to streamline the UX flow such as a “Learn More” button that links to the original articles and highlights specific sections to investigate further, or displaying the EMR when hovering over a patient ID for even easier access.



