import os
import requests
import time
from dotenv import load_dotenv
load_dotenv()
bright_data_api_key = os.getenv("BRIGHT_DATA_API_KEY")




def trigger_dataset(url):
	api_url = "https://api.brightdata.com/datasets/v3/trigger"
	headers = {
		"Authorization": f"Bearer {bright_data_api_key}",
		"Content-Type": "application/json",
	}
	params = {
		"dataset_id": "gd_l1viktl72bvl7bjuj0",
		"include_errors": "true",
	}
	data = [
		{"url":url},
	]

	response = requests.post(api_url, headers=headers, params=params, json=data)
	return response.json().get("snapshot_id")


def get_dataset_progress(snapshot_id):
	url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
	headers = {
		"Authorization": f"Bearer {bright_data_api_key}",
	}

	response = requests.get(url, headers=headers)
	return response.json().get("status")


def get_dataset_snapshot(url):

	tigger_id = trigger_dataset(url)
	progress = get_dataset_progress(tigger_id)

	while progress != "ready":
		time.sleep(30)
		print(f"Snapshot is not ready, waiting for {progress} seconds")
		progress = get_dataset_progress(tigger_id)

	url = f"https://api.brightdata.com/datasets/v3/snapshot/{tigger_id}"
	headers = {
		"Authorization": f"Bearer {bright_data_api_key}",
	}
	params = {
		"format": "json",
	}

	response = requests.get(url, headers=headers, params=params)
	return response.json()







