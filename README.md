# Automated-Mail-Generating
This project is a Python-based browser automation agent designed to automatically login, compose, and send emails using a real email account. The script takes all required inputs (email ID, password, subject, body, receiver) from the command line, launches a browser, automates the full process, and finally sends the email without any manual typing.
The automation is built to satisfy the requirements of AuditRAM Assignment 2, where the agent must perform the following tasks sequentially:

1️⃣ Login Automation

Automatically opens a browser window

Navigates to the email login page

Enters the sender’s email ID and password

Authenticates the user securely

2️⃣ Compose Email

Opens the “Compose” window

Fills the receiver’s email address

Inserts the subject and message body (taken from command-line arguments)

3️⃣ Send Email

Clicks the “Send” button

Confirms successful delivery

Closes the browser automatically

4️⃣ Command-Line Based Execution

The program is executed like this:

python email_agent.py --email "yourmail@gmail.com" --password "xxxx" --to "scittest@auditram.com" --subject "Test Mail" --body "This is an automated mail."

5️⃣ Technologies Used

Python 3

Selenium / Browser Automation Tools

Command-line argument parsing

Web automation using ChromeDriver or EdgeDriver

6️⃣ Purpose of the Project

This agent demonstrates:

Real-world browser automation

Automated workflows

Email handling via programmatic control

Hands-free execution using command-line inputs

It is built to complete the assignment requirement of automating Login → Compose → Send in a fully autonomous flow.
