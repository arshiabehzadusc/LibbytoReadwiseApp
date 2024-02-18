#!/usr/bin/env python3
import pandas as pd
import json
import platform
import os
import requests
import certifi

def extract_and_update(row):
	highlight_text = row['Highlight']
	# Check for ASCII and typographic quotes
	if '"' in highlight_text or '“' in highlight_text:
		# Adapt to handle typographic quotes
		start_quote = highlight_text.find('“') if '“' in highlight_text else highlight_text.find('"')
		end_quote = highlight_text.find('”', start_quote) if '”' in highlight_text else highlight_text.rfind('"')
		quoted_text = highlight_text[start_quote+1:end_quote]
		# Remove the quoted text from the original, handling both ASCII and typographic quotes
		notes_text = highlight_text.replace(highlight_text[start_quote:end_quote+1], '').strip()
		# Update the DataFrame row
		row['Highlight'] = quoted_text
		row['Notes'] = notes_text
	# If there are no quotes, the original Highlight text remains, and Notes stay empty
	return row

def add_note_prefix(row):
	highlight_text = row['Highlight']
	if '"' not in highlight_text and  '“' not in highlight_text:
		row["Highlight"] = f"N: {highlight_text}"
	return row

def get_page_number_from_google_books(title, author, api_key):
	base_url = "https://www.googleapis.com/books/v1/volumes"
	# Include the author in the search query
	params = {"q": f"{title}+inauthor:{author}", "key": api_key}
	response = requests.get(base_url, params=params, verify=certifi.where())
	data = response.json()
	if response.status_code != 200:
		# Handle non-OK responses
		if "error" in data:
			raise Exception(f"{data['error']['message']} Try again without estimating page number")
		else:
			raise Exception("An unknown error occurred while fetching page data. Try again without estimating page number")
	page_count = None
	if data["totalItems"] > 0:
		book_data = data["items"][0]
		if title not in book_data["volumeInfo"]["title"] or author not in book_data['volumeInfo']['authors']:
			raise Exception("Book could not be found. Try again without page estimating page number")
		if "pageCount" in book_data["volumeInfo"]:
			page_count = book_data['volumeInfo']['pageCount']
		else:
			raise Exception(" Try again without page estimate") 
	else:
		raise Exception("Book could not be found. Try again without page estimating page number")
		
	if not page_count:
		raise Exception("Page count not available for estimate. Try again without estimating page number")

	return page_count

def estimate_page_number(row, page_count):
	percent = row['percent']
	estimate = int(round(percent * page_count))
	row['percent'] = estimate
	return row

		
def make_readwise_format(filePath, splitQuotes, estimatePageNumber, notePrefix):
	with open(filePath, 'r', encoding='utf-8') as file:
		data = json.load(file)
		
	# Extract the 'bookmarks' section
	bookmarks_data = data['bookmarks']
	title = data['readingJourney']['title']['text']
	author = data['readingJourney']['author']
	
	# Create a DataFrame
	df = pd.DataFrame(bookmarks_data)
	df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
	
	# Convert the datetime objects to the desired string format
	df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
	
	# Show the result
	df.rename(columns={'timestamp': 'Date', 'note': 'Highlight'}, inplace=True)
	df['Title'] = title
	df['Author'] = author
	
	# Apply the function across the DataFrame rows
	if notePrefix:
		df = df.apply(add_note_prefix, axis=1)
	if splitQuotes:
		df['Notes'] = ''
		df = df.apply(extract_and_update, axis=1)
	if estimatePageNumber:
		api_key = "AIzaSyCFIrcPgzZfwoZw4zhM_iKH1yNZy7dmnmw"
		page_count = get_page_number_from_google_books(title,author,api_key)
		df = df.apply(estimate_page_number, axis=1, page_count=page_count)
		df.rename(columns={'percent': 'Location'}, inplace=True)
	else:
		df.drop('percent', axis=1, inplace=True)
	return df
	
	