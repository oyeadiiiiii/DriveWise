<h1>Guardian Ride</h1>
<p>Guardian Ride is an innovative application designed to enhance safety and accountability within taxi rental services by evaluating driver performance in real time. Employing machine learning technology, Guardian Ride assesses drivers based on attentiveness, alertness, and dadherence to traffic regulations during journeys. This README provides an overview of Guardian Ride's functionality, features, and implementation.</p>
<h2>How Does It Work?</h2>
<p>Guardian Ride uses advanced technology to analyze the driver's behavior and detect potential safety risks. Here's a breakdown of how it works:</p>
<h3>1. Face Detection:</h3>
<p>Guardian Ride first locates the driver's face in the camera view using specialized algorithms</p>
<h3>2. Keypoint Prediction:</h3>
<p>Once the face is detected, Guardian Ride predicts key facial landmarks such as eyes, nose, and mouth to track movement and orientation.</p>
<h3>3. Computed Scores:</h3>
<b>- EAR (Eye Aspect Ratio):</b><p> Determines if the driver's eyes are open wide or starting to close, alerting to potential drowsiness.</p>
   <b>- Gaze Score:</b> <p>Monitors the direction of the driver's gaze to ensure focus on the road ahead.</p>
   <b>- Head Pose:</b> <p> Checks for proper head alignment to prevent distracted driving.</p>
   <b>- PERCLOS (PERcentage of CLOSure eye time):</b> <p> Tracks the frequency and duration of eye closures, indicating fatigue or drowsiness.</p>
<h3>4. Driver States:</h3> 
   <b>- Driving Properly:</b> <p>No issues detected, and no alerts are triggered.</p> 
   <b>- Asleep:</b> <p>Warns the driver if prolonged eye closures suggest the possibility of falling asleep at the wheel.</p> 
   <b>- Distracted:</b> <p> Provides a gentle reminder to refocus attention if the head pose suggests distraction or inattentiveness.</p>
<h3>6. Face Recognition:</h3> 
   <b>-Camera Installation:</b> <p>Guardian Ride incorporates a camera positioned on the windshield, directly facing the driver, enabling continuous monitoring.</p> 
  <b>-Driver Identification:</b>  <p>Utilizing the KNN algorithm (Haarcascade_frontalface_default.xml), Guardian Ride accurately identifies drivers based on facial recognition.</p> 
   <b>-Pre-Registration:</b> <p> Before deployment, employers register all drivers within the system, ensuring accurate identification and eliminating cases where the KNN algorithm classifies unregistered output as one of the classes.</p> 
  <b> -Violation Tracking:</b> <p> If a driver commits a traffic violation, government-installed cameras capture the car's license plate and timestamp, leading to a fine. Subsequently, the employer or owner can identify the driver responsible for the infraction while driving the specific vehicle at that time, facilitating appropriate reprimand. </p>

[Demo Video](https://drive.google.com/file/d/1V-uoC5xJaSCxFCnI9AZIyVQTp1n90zx6/view?usp=sharing)


<h2>Installation and Setup</h2> 
<p>
-Clone the Guardian Ride repository from GitHub.<br>
-Install Python verison 3.10.0.<br>
-Install required dependencies as listed in the requirements.txt file.<br>
-Open app.py and run it using the python version 3.10.0<br>
</p>
