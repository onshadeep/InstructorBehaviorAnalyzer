# Instructor Behavior Analyzer

A web app to analyze instructor tone and behavior from Vimeo videos using OpenAI GPT or NLP.

I have used the following two raw files:
01. For unprofessional words https://raw.githubusercontent.com/onshadeep/unprofessional_words/refs/heads/main/unprofessional_words.txt
02. For red flag words https://raw.githubusercontent.com/onshadeep/unprofessional_words/refs/heads/main/red_flags.txt

Important: If you want to add more words or phrases to the unprofessional or red flag files, you can do so directly from your GitHub repository. You do not need to modify the existing or running code.

Steps to run the project on your local machine
01. pip install -r requirements.txt
02. python -m textblob.download_corpora
03. python backend/main.py


Steps to run the project on your development server:
01. Pull the latest code 
git pull repo_url
02. Activate the python env 
source instructor_behavior_env/bin/activate
03. Install the packages
pip install -r requirements.txt
04. Run the below command 
python -m textblob.download_corpora
05. Kill the running port 5000 by following steps
a. Run this to identify the process:
sudo lsof -i :5000
b. You'll get output like:
python3 12345 ubuntu ... TCP *:5000 (LISTEN)
c. Then kill it using:
sudo kill -9 12345
(replace 12345 with the actual PID)
d. Now try restarting your service:
sudo systemctl restart instructorapp
06. Run the below command to update the logs
nohup python3 backend/main.py > output.log 2>&1 &
07. Check if UFW (Uncomplicated Firewall) is enabled:
sudo ufw status
08. If it’s active, allow port 5000:
sudo ufw allow 5000
09. To run the server even you exit the instance, if you haven't created the flaskapp
tmux new -s flaskapp
09. To run the server even you exit the instance, if you already created the flaskapp
tmux attach -t flaskapp
10. Run your project or app
python backend/main.py
11. To save the current running status 
Ctr + B then D
12. Now you can deactivate your python env and exit the instance.


Refrences:

01. https://textblob.readthedocs.io/en/dev/install.html
02. 