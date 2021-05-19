import time

from django.shortcuts import render

from youtube_transcript_api import YouTubeTranscriptApi
import requests


def youtube_video(request, video_id):
    condensed_transcript = []

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except:
        return render(request, 'youtube_not_found.html', {})

    subseconds = 0
    condensed_entry = None
    start_times = [];

    for entry in transcript:
        start = entry.get('start')
        text = entry.get('text', '')
        duration = entry.get('duration', 0)

        text = text.replace('\n', ' ')

        try:
            duration = float(duration)
        except:
            continue

        if condensed_entry is None:
            condensed_entry = {'start': start, 'text': text, 'duration': duration}

        else:
            condensed_entry['duration'] += duration
            condensed_entry['text'] += ' ' + text 

        if condensed_entry.get('duration', 0) >= 23:
            condensed_entry['start_display'] = time.strftime('%H:%M:%S', 
                    time.gmtime(condensed_entry.get('start', 0))) 

            s = condensed_entry.get('start', 0)
            start_times.append(s)

            condensed_transcript.append(condensed_entry)
            subseconds = 0
            condensed_entry = None

        #last entry
        elif entry == transcript[-1]:
            condensed_entry['start_display'] = time.strftime('%H:%M:%S', 
                    time.gmtime(condensed_entry.get('start', 0))) 

            s = condensed_entry.get('start', 0)
            start_times.append(s)

            condensed_transcript.append(condensed_entry)


    source = 'https://www.youtube.com/embed/'
    source += video_id
    source += '?enablejsapi=1'
    #source += '?enablejsapi=1&origin='
    #source += 'https://docdrop.org'
    source += '&widgetid=1'
    source += '&start=0&name=me'

    canonical_url = 'https://www.youtube.com/watch?v='
    canonical_url += video_id 

    noembed_url = 'https://noembed.com/embed?url=' + canonical_url 
    r = requests.get(noembed_url)

    title = ''
    if r.status_code == 200:
        try:
            video_info = r.json()
            if video_info:
                title = video_info.get('title')

        except:
            pass


    return render(request, 'youtube.html', {'transcript': condensed_transcript,
        'video_id': video_id, 'start_times': start_times, 'canonical_url': canonical_url, 
        'iframe_src': source, 'title': title})
