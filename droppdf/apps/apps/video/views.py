import time

from django.shortcuts import render
from django.conf import settings

from youtube_transcript_api import YouTubeTranscriptApi
import requests


def youtube_video(request, video_id):
    condensed_transcript = []

    # if proxy url was provided
    proxy_url = settings.YOUTUBE_TRANSCRIPT_API_PROXY

    #language may be passed as query string. ?lang=de
    #multiple comma seperated languages are acceptable i.e ?lang=en,de
    #if multiple language versions of subs exist first one will be used
    lang = request.GET.get('lang')

    if lang:
        lang_list = lang.split(',')

    else:
        #find default available languages for transcript
        try:
            if proxy_url is not None:
                transcript_list = YouTubeTranscriptApi.list_transcripts(
                        video_id, 
                        proxies={'https': proxy_url}
                        )
            else:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        except Exception as e:
            print(e)
            #TODO extract actual error message and give better error.
            return render(request, 'youtube_not_found.html', {})

        lang_list = [i.language_code for i in transcript_list]

        #default to English if it exists
        #apparently first language in list is used in get_transcript
        if 'en' in lang_list:
            lang_list.insert(0, 'en')

    try:
        if proxy_url is not None:
            transcript = YouTubeTranscriptApi.get_transcript(
                    video_id,
                    languages=lang_list,
                    proxies={'https': proxy_url}
                    )
        else:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=lang_list)
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
