#!/usr/bin/env python3
import pandas as pd
import json
import platform
import os

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

def get_path(filename):
	name = os.path.splitext(filename)[0]
	ext = os.path.splitext(filename)[1]
	
#	if platform.system() == "Darwin":
	from AppKit import NSBundle
	file = NSBundle.mainBundle().pathForResource_ofType_(name, ext)
	return file #or os.path.realpath(filename)
#	else:
#		return os.path.realpath(filename)
	
def make_readwise_format(filePath, splitQuotes, percentLocations):
	#filePath = get_path(filePath)
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
	if splitQuotes:
		df['Notes'] = ''
		df = df.apply(extract_and_update, axis=1)
	
	if percentLocations:
		df['percent'] = (df['percent'] * 100).round(0).astype(int)
		# Rename the 'percent' column to 'Location'
		df.rename(columns={'percent': 'Location'}, inplace=True)
	else:
		df.drop('percent', axis=1, inplace=True)
	
	return df
	
	