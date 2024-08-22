import time
from datetime import timedelta

from django.utils import timezone
from django.shortcuts import render
from django.conf import settings

from youtube_transcript_api import YouTubeTranscriptApi
import requests

from apps.models import VideoSubtitle


def _cache_transcript(video_id, lang, transcript):
    # if sub already exists, delete it first
    existing_subtitle = VideoSubtitle.objects.filter(
        video_id=video_id,
        lang_list=lang
    ).first()

    if existing_subtitle:
        existing_subtitle.delete()

    video_subtitle = VideoSubtitle(
        lang_list=lang,
        video_id=video_id,
        subtitle=transcript
    )

    video_subtitle.save()


def _get_transcript_from_cache(video_id, language):
    subtitle = VideoSubtitle.objects.filter(
        video_id=video_id,
        lang_list=language
    ).first()

    if subtitle:

        # if the subtitle is old, retrieve from youtube and re-cache
        one_month_ago = timezone.now() - timedelta(days=30)
        if subtitle.updated < one_month_ago:
            return None

        return subtitle.subtitle

    return None


def _get_transcript_from_youtube(video_id, lang_list):
    proxy_url = settings.YOUTUBE_TRANSCRIPT_API_PROXY

    try:
        if proxy_url is not None:
            transcript = YouTubeTranscriptApi.get_transcript(
                    video_id,
                    languages=lang_list,
                    proxies={'https': proxy_url}
                    )
        else:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=lang_list)
    except Exception as e:
        # TODO error log
        return None

    _cache_transcript(video_id, lang_list[0], transcript)

    return transcript


def _get_language_list(video_id):
    # find default available languages for transcript
    proxy_url = settings.YOUTUBE_TRANSCRIPT_API_PROXY

    try:
        if proxy_url is not None:
            transcript_list = YouTubeTranscriptApi.list_transcripts(
                    video_id, 
                    proxies={'https': proxy_url}
                    )
        else:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    except Exception as e:
        #TODO extract actual error message and give better error.
        return None

    lang_list = [i.language_code for i in transcript_list]

    if 'en' in lang_list:
        lang_list.insert(0, 'en')

    return lang_list


def youtube_video(request, video_id):
    transcript = None
    condensed_transcript = []

    #language may be passed as query string. ?lang=de
    #multiple comma seperated languages are acceptable i.e ?lang=en,de
    #if multiple language versions of subs exist first one will be used
    lang = request.GET.get('lang')

    if lang:
        lang_list = lang.split(',')

    # See if the transcript is cached for the language.
    if lang is None:
        # If no language was passed in the request assume English.
        transcript = _get_transcript_from_cache(video_id, 'en')
    else:
        transcript = _get_transcript_from_cache(video_id, lang_list[0])

    # transcript not found in cache, try to get it from youtube.
    if transcript is None:

        if lang is None:
            # get language list from youtube
            lang_list = _get_language_list(video_id)

            if lang_list is None:
                # No language list from youtube means no subs
                print('no lang')
                return render(request, 'youtube_not_found.html', {})

        transcript = _get_transcript_from_youtube(video_id, lang_list)

    if transcript is None:
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
