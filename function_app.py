import logging
import json
import azure.functions as func


app= func.FunctionApp()

@app.timer_trigger(schedule="0 * 9 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False)
def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.warning("The timer is past due!")

    logging.info("Python timer trigger function started.")

    try:
        with open("tasks.json", "r", encoding="utf-8") as file:
            tasks = json.load(file)

        for task in tasks:
            logging.info(f"Task: {task['task']}")

    except FileNotFoundError:
        logging.error("File tasks.json not found.")
    except json.JSONDecodeError:
        logging.error("Error decoding JSON file.")

    logging.info("Python timer trigger function executed.")



