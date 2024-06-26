
from manim import *
import json
import re
import os

import dotenv
import boto3

dotenv.load_dotenv()
s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_S3_ACCESS_ID'), aws_secret_access_key=os.environ.get('AWS_S3_ACCESS_KEY'))


# def lambda_handler(event, context):
#     # Extract S3 bucket and key from the event
#     bucket_name = event['bucket_name']
#     lyrics_key = event['lyrics_key']
#     timestamps_key = event['timestamps_key']

#     # Load lyrics from S3
#     lyrics_file = s3.get_object(Bucket=bucket_name, Key=lyrics_key)
#     lyrics = [line.decode('utf-8').strip().split() for line in lyrics_file['Body'].readlines()]
#     lyrics = [line for line in lyrics if line]  # remove empty lists

#     # Load timestamps from S3
#     timestamps_file = s3.get_object(Bucket=bucket_name, Key=timestamps_key)
#     timestamp_json = json.loads(timestamps_file['Body'].read().decode('utf-8'))
#     song_length = timestamp_json['nonspeech_sections'][-1]['end']
#     timestamps = process_timestamps(timestamp_json)

#     # Sync lyrics with timestamps
#     synced_lyrics = sync_lyrics_with_timestamps(lyrics, timestamps)

#     # Your processing logic here (e.g., generating animations)
#     # Note: Due to the constraints of AWS Lambda (e.g., execution time limit, no display),
#     # you may need to adjust how you generate and store animations.

#     # Example:
#     scene = KaraokeScene()
#     scene.render(synced_lyrics, song_length)

#     return {
#         'statusCode': 200,
#         'body': json.dumps('Process completed successfully!')
#     }

class KaraokeScene(Scene):
    def construct(self):
        frame_rate = config.frame_rate
        one_frame_dration = 1 / frame_rate
        # Load lyrics
        with open('lyrics.txt') as f:
            lyrics = [line.strip().split() for line in f.readlines()]
        timestamp_json = json.load(open('timestamps.json'))
        timestamps = []
        # remove emptylists from lyrics
        lyrics = [line for line in lyrics if line]

        # Load timestamps

        song_length = timestamp_json['nonspeech_sections'][-1]['end']
        # Process timestamps
        for segment in timestamp_json['segments']:
            for word in segment['words']:
                start = word['start']
                end = word['end']
                # if next word doesn't start with a space, append it to the previous word
                if not word['word'].startswith(' '):
                    start = timestamps[-1][1]
                    timestamps[-1] = (start, end, timestamps[-1][2] + word['word'])
                else:
                    word_text = re.sub(r"\s+", "", word['word'])  # Clean word text
                    timestamps.append((start, end, word_text))

        # Sync lyrics with timestamps
        i = 0
        synced_lyrics = []
        for line in lyrics:
            one_line = []
            for word in line:
                if i >= len(timestamps):
                    break
                start, end, text = timestamps[i]
                one_line.append((start, end, text))
                i += 1
            print(line)
            print(one_line)
            synced_lyrics.append(one_line)

        # Display lyrics

        previous_end_time = 0  # Keep track of the end time of the last word
        for sentence in synced_lyrics:
            self.clear()

            pause_duration = sentence[0][0] - previous_end_time - one_frame_dration 
            pause_duration = max(0, pause_duration)

            line_group = VGroup()  # Group for the current line of lyrics

            for word_info in sentence:
                start, end, word_text = word_info
                word = Text(word_text, color=WHITE).scale(0.7)
                line_group.add(word)  # Add the word to the line group

            line_group.arrange(RIGHT, buff=0.1)  # Arrange words in a row
            self.add(line_group)  # Display the line

            if pause_duration > 0:
                self.wait(pause_duration)  # Wait for the duration of the pause

            # Highlight words sequentially
            for i, word_info in enumerate(sentence):
                start, end, _ = word_info
                duration = end - start
                if duration <= 0:  # If duration is zero, highlight immediately
                    self.add(line_group[i].set_color(YELLOW))
                else:  # For non-zero durations, proceed with normal animation
                    self.play(line_group[i].animate.set_color(YELLOW), run_time=duration)
                # now wait for the remaining duration
                if i < len(sentence) - 1:
                    remaining_duration = sentence[i + 1][0] - end
                    if remaining_duration > 0:
                        self.wait(remaining_duration)

            previous_end_time = sentence[-1][1]
        # Wait for the remaining duration
        remaining_duration = song_length - previous_end_time
        if remaining_duration > 0:
            self.wait(remaining_duration)

scene = KaraokeScene()
scene.render()
