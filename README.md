# emergent-property-finding-machine
## Project Outline
This project provides a front-end web-based interface that allows users to input simple text into one of three distinct fields. The text is handled on a backend for easy compounding storage. When initiated, the stored information is formatted into a fine-tuning training set for a GPT model. Once the GPT model is fine-tuned with the data, it can be queried by the user via the web interface. The user’s query is concatenated with a prompt on the backend before being sent to the model. A simple text output is returned to the user.

## Installation
1. Clone this repository.
2. Navigate to the project directory.
3. Run ``` pip install -r requirements.txt ``` to install all necessary dependencies.

## Usage
1. To use the OpenAI API in your Python project, you'll need to provide your API key securely. Here's how to do it using environment variables:

    - Create a .env file (Optional but Recommended):

    While not strictly necessary, creating a file named .env in the root directory of your project (where your main Python script resides) is a recommended practice for storing sensitive information like API keys. This keeps your credentials out of version control systems like Git, enhancing security.

    Important: This file should not be committed to version control.

    - or Set the OPENAI_KEY Environment Variable:

    Open your terminal or command prompt and navigate to your project directory. Set the OPENAI_KEY environment variable with your actual OpenAI API key using the appropriate command for your operating system:

    Linux/macOS:
    ```
    export OPENAI_KEY=YOUR_OPENAI_API_KEY
    ```

    Replace YOUR_OPENAI_API_KEY with your actual OpenAI API key obtained from your OpenAI account.
2. Provide at least 10 inputs in the terminal before trying to use the out terminal.
3. Run the Flask app following these steps:
    - Set the environment variable FLASK_APP to your application. For example, you can set the environment variable like this:
        On Unix or MacOS, use export FLASK_APP=epfm.py
        On Windows CMD, use set FLASK_APP=epfm.py
        For PowerShell, use $env:FLASK_APP = "epfm.py"
    - Run the application with the command flask run. This will start a development web server hosting your application1234.
  
    *Alternatively, you can also run the Flask application directly using Python:

    ```
    python .\epfm.py
    ```
    This command will start the Flask server and you should be able to access the application in your web browser at http://localhost:5000.


    Please note that this method assumes that your Flask application is defined in `epfm.py` and that you're in the same directory as `epfm.py`. If your application is defined in a different file or if you're in a different directory, you'll need to adjust the command accordingly. Also, the default port for Flask is 5000, but if your application is set to use a different port, you'll need to adjust the URL accordingly.  

4. Do not open the `index.html` file alone as it has links to `.css` and `.js` in the static directory. For the best user experience, it's better to run the Flask app and use the provided link.
5. The initial request may take several minutes to process as the model is being fine-tuned. You can monitor the current status by observing the terminal where Flask was executed.  
