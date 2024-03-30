from manim import *
import json
import re
import os
import dotenv
import boto3
import ffmpeg

dotenv.load_dotenv()
s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_S3_ACCESS_ID'), aws_secret_access_key=os.environ.get('AWS_S3_ACCESS_KEY'))


def lambda_handler(event, context):
    outdir = '/tmp'
    
    song_name = event['song_name']
    s3.download_file('auto-karaoke', f'{song_name}/base_song.mp3',f'{outdir}/base_song.mp3' )
    s3.download_file('auto-karaoke', f'{song_name}/no_vocals.mp3', f'{outdir}/no_vocals.mp3')
    s3.download_file('auto-karaoke', f'{song_name}/lyrics.txt', f'{outdir}/lyrics.txt')
    s3.download_file('auto-karaoke', f'{song_name}/timestamps.json', f'{outdir}/timestamps.json')

    scene = KaraokeScene()
    scene.render()

    input_video = ffmpeg.input("/tmp/output.mp4")
    input_audio = ffmpeg.input(f'{outdir}/no_vocals.mp3')

    ffmpeg.concat(input_video, input_audio, v=1, a=1).output('tmp/lyric_video.mp4').run()
    ffmpeg.concat(input_video, input_audio, v=1, a=1).output('tmp/karaoke.mp4').run()

    # upload to s3
    s3.upload_file('tmp/lyric_video.mp4', 'auto-karaoke', f'{song_name}/lyric_video.mp4')
    s3.upload_file('tmp/karaoke.mp4', 'auto-karaoke', f'{song_name}/karaoke.mp4')

    return "DONE"    


class KaraokeScene(Scene):
    def construct(self):
        frame_rate = config.frame_rate
        one_frame_dration = 1 / frame_rate
        config.frame_height = 480  # Set the frame height to 480 pixels
        config.frame_width = 854
        # Load lyrics
        with open('/tmp/lyrics.txt') as f:
            lyrics = [line.strip().split() for line in f.readlines()]
        timestamp_json = json.load(open('/tmp/timestamps.json'))
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

        self.play("Hello".animate, run_time=5)
        # Display lyrics

        # previous_end_time = 0  # Keep track of the end time of the last word
        # for sentence in synced_lyrics:
        #     self.clear()

        #     pause_duration = sentence[0][0] - previous_end_time - one_frame_dration 
        #     pause_duration = max(0, pause_duration)

        #     line_group = VGroup()  # Group for the current line of lyrics

        #     for word_info in sentence:
        #         start, end, word_text = word_info
        #         word = Text(word_text, color=WHITE).scale(0.7)
        #         line_group.add(word)  # Add the word to the line group

        #     line_group.arrange(RIGHT, buff=0.1)  # Arrange words in a row
        #     self.add(line_group)  # Display the line

        #     if pause_duration > 0:
        #         self.wait(pause_duration)  # Wait for the duration of the pause

        #     # Highlight words sequentially
        #     for i, word_info in enumerate(sentence):
        #         start, end, _ = word_info
        #         duration = end - start
        #         if duration <= 0:  # If duration is zero, highlight immediately
        #             self.add(line_group[i].set_color(YELLOW))
        #         else:  # For non-zero durations, proceed with normal animation
        #             self.play(line_group[i].animate.set_color(YELLOW), run_time=duration)
        #         # now wait for the remaining duration
        #         if i < len(sentence) - 1:
        #             remaining_duration = sentence[i + 1][0] - end
        #             if remaining_duration > 0:
        #                 self.wait(remaining_duration)

        #     previous_end_time = sentence[-1][1]
        # # Wait for the remaining duration
        # remaining_duration = song_length - previous_end_time
        # if remaining_duration > 0:
        #     self.wait(remaining_duration)

if __name__ == "__main__":
    song_name = "YO! MY SAINT (Film Version)"
    lambda_handler({'song_name': song_name}, None)