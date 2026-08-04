!!! all the commands to be entered are mentioned after === 3 equal signs and start from a new line in the below text explanation for set up!!!

STEP 1 -> make sure u are in the folder like mine was 
===  cd "C:\Users\Goanshi Tandon\Desktop\vision-module"


STEP 2 -> create the venv for yuor device (mediapipe didn't work on some specific python version so i had to download this one so specify py 3.11 such that it knows which version of python u are using)
# create venv using Python 3.11 specifically
=== py -3.11 -m venv venv

STEP 3 -> after creating the venv sahi se activate it
# activate it
=== venv\Scripts\activate

STEP 4 -> install all the files in the requirements folder 
=== pip install -r requirements.txt

STEP 5 -> check once if the mediapipe install in last step works properly or not 
=== python -c "import mediapipe as mp; print(mp.solutions.pose)"

STEP 6 -> after u have given all these commands and they work without any errors, run this command to finally open the camera for testing of the project and to start detection
=== python main.py

the project till now is able to detect THUMBS-UP, THUMBS-DOWN, FIST, OPEN PALM, POINTING, PEACE signs 