from flask import Flask, request, render_template, jsonify
import csv
import os
import openai
import json
import time

app = Flask(__name__)

# Check if the "openAIKey.txt" file exists
if os.path.exists("openAIKey.txt"):
    try:
        # Try to read the OpenAI key from the environment variables
        openai.api_key = os.getenv('OPENAI_KEY')
    except Exception as e:
        print(f"An error occurred while reading the key: {e}")
else:
    print("The 'openAIKey.txt' file does not exist.")

# Variable to store the fine-tuned GPT model (initialize it as None)
fine_tuned_model_id = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/in_terminal", methods=["POST"])
def in_terminal():
    """
    Handles POST requests to "/in_terminal". Extracts "itr", "message", and "hesitations" from JSON data,
    writes them to "data.csv", and returns a JSON response with a status of "success" and HTTP 200.
    """

    data = request.get_json()

    # Define the headers
    headers = ["itr", "message", "hesitations"]

    # Check if the CSV file exists, and if not, write the headers
    if not os.path.exists("data.csv"):
        with open("data.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    # Write the data to the CSV file
    with open("data.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([data["itr"], data["message"], data["hesitations"]])

    return {"status": "success"}, 200


@app.route("/reset_data", methods=["POST"])
def reset_data():
    """ "
    Erase all the data
    """
    try:
        if os.path.exists("data.csv"):
            os.remove("data.csv")
        if os.path.exists("training_data.jsonl"):
            os.remove("training_data.jsonl")
        return {"status": "success"}, 200
    except Exception as e:
        # Handle any exceptions or errors
        return f"Error: {str(e)}"


@app.route("/reset_model", methods=["POST"])
def reset_model():
    """ "
    Erase the model and the remote file
    """
    global fine_tuned_model_id
    if os.path.exists("ids.json"):
        with open("ids.json", "r") as f:
            ids = json.load(f)

        file_id = ids.get("file_id")
        fine_tuned_model_name = ids.get("fine_tuned_model_name")
        if file_id:
            # Delete the file from OpenAI
            try:
                file_delete_result = openai.File.delete(sid=file_id)
                print(f"file has been deleted {file_delete_result}")
            except openai.error.OpenAIError as e:
                print(f"Failed to delete file {file_id}: {e}")

        if fine_tuned_model_name:
            # Delete the model from OpenAI
            try:
                model_delete_result = openai.Model.delete(fine_tuned_model_name)
                print(f"Model has been deleted {model_delete_result}")
            except openai.error.OpenAIError as e:
                print(f"Failed to delete model {fine_tuned_model_name}: {e}")

        # Remove the file containing IDs
        os.remove("ids.json")
        fine_tuned_model_id = None
    else:
        print("No model exists to be deleted")
    return {"status": "success"}, 200


@app.route("/receive", methods=["POST"])
def receive():
    global fine_tuned_model_id

    data = request.get_json()

    # Check if the fine-tuned model is already created
    if fine_tuned_model_id is None:
        # Create and fine-tune the GPT model with data from the CSV file
        fine_tuned_model_id = get_fine_tune_model_id()

    # Prompt the request to the fine-tuned model
    response = prompt_to_model(
        fine_tuned_model_id,
        data["itr"],
        data["message"],
        data["confidence"],
    )

    return jsonify({"result": response}), 200


def get_fine_tune_model_id():
    # Check if there is a saved file ID and fine-tuning job ID
    if os.path.exists("ids.json"):
        with open("ids.json", "r") as f:
            ids = json.load(f)
        file_id = ids.get("file_id")
        fine_tuned_model_name = ids.get("fine_tuned_model_name")
    else:
        file_id = None
        fine_tuned_model_name = None

    if fine_tuned_model_name:
        print(f"Fine-tuning job already exists with name: {fine_tuned_model_name}")
        return fine_tuned_model_name
    else:
        # If there is no saved fine-tuning job ID, create a new one
        fine_tuned_model_name = create_and_fine_tune_model(file_id)
    return fine_tuned_model_name


def create_and_fine_tune_model(file_id):
    try:
        # Get the model ID
        model_id = "gpt-3.5-turbo"

        # If there is no saved file ID, create a new file
        if not file_id:
            file_id = create_remote_file()
        else:
            print(f"File already exists with ID: {file_id}")

        # Start the fine-tuning job using the OpenAI file
        fine_tuning_job = openai.FineTuningJob.create(
            training_file=file_id,
            model=model_id,
        )

        # Check the status of the fine-tuning job
        status = fine_tuning_job.status

        # Wait until the fine-tuning job is completed
        while status != "succeeded":
            print(
                f"Fine-tuning job status: {status}. Waiting for the job to be completed..."
            )
            status = openai.FineTuningJob.retrieve(fine_tuning_job.id).status
            time.sleep(30)
        print("Fine-tuning job is completed. Proceeding with prompting...")
        # Dummy prompt to the fine-tuned model
        fine_tuning_job = openai.FineTuningJob.retrieve(fine_tuning_job.id)

        # Save the file ID and fine-tuning job ID for future use
        with open("ids.json", "w") as f:
            json.dump(
                {
                    "file_id": file_id,
                    "fine_tuning_job_id": fine_tuning_job.id,
                    "fine_tuned_model_name": fine_tuning_job.fine_tuned_model,
                },
                f,
            )

        # Return the fine-tuning job ID
        return fine_tuning_job.fine_tuned_model

    except Exception as e:
        # Handle any exceptions or errors
        return f"Error: {str(e)}"


def create_remote_file():
    # Get the path to the JSON training data
    json_file_path = read_csv_data()

    # Create an OpenAI file for the JSON training data
    file = openai.File.create(file=open(json_file_path, "rb"), purpose="fine-tune")
    file_id = file.id

    # Check the status of the file
    status = file.status

    # Wait until the file is processed
    while status != "processed":
        print(f"File status: {status}. Waiting for the file to be processed...")
        time.sleep(10)
        file = openai.File.retrieve(file_id)
        status = file.status

    print("File has been processed. Proceeding with fine-tuning...")
    with open("ids.json", "w") as f:
        json.dump(
            {
                "file_id": file_id,
            },
            f,
        )

    return file_id


def read_csv_data():
    formatted_data = []
    jsonl_file_path = "training_data.jsonl"

    # Check if the "data.csv" file exists
    if not os.path.exists("data.csv"):
        print("The 'data.csv' file does not exist.")
        return "Error: The 'data.csv' file does not exist."

    try:
        # Read data from the CSV file and return it as a list of dictionaries
        with open("data.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                conversation = [
                    {"role": "system", "content": f"itr: {row['itr']}"},
                    {"role": "user", "content": f"message: {row['message']}"},
                    {
                        "role": "assistant",
                        "content": f"hesitations: {row['hesitations']}",
                    },
                ]
                formatted_data.append({"messages": conversation})
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return f"Error: {str(e)}"

    try:
        # Save the formatted training data to a JSONL file
        with open(jsonl_file_path, "w") as jsonlfile:
            for item in formatted_data:
                jsonlfile.write(json.dumps(item) + "\n")
    except Exception as e:
        print(f"An error occurred while writing the JSONL file: {e}")
        return f"Error: {str(e)}"

    return jsonl_file_path


def prompt_to_model(model, itr, message, confidence):
    # Define the master prompt (you can customize this as needed)
    master_prompt = "You are tasked with providing information on the payload separation system. Please do not return empty and answer the following in details:\n"

    # Combine the input data with the master prompt
    combined_prompt = (
        f"{master_prompt}itr: {itr}\nmessage: {message}\nConfidence: {confidence}\n"
    )

    try:
        # Send the combined prompt to the fine-tuned chat model
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": combined_prompt}],
        )

        # Extract and return the model's response
        return response.choices[0].message.content

    except Exception as e:
        # Handle any exceptions or errors
        return f"Error: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)
