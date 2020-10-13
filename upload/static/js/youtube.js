$(document).ready(function(){
    var player, duration;

    var current_sub;

    var keep_sync = true;

    var scroll_sub_down = true;

    var subtitle_elements = $('.sub');

    var times = [];

    var has_been_started_by_user = false;

    var tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    var firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);


    function onYouTubeIframeAPIReady() {
        player = new YT.Player('video-player-iframe', {
            playerVars: {
                'autoplay': 1,
                'mute': 1
            },
            events: {
            'onReady': onPlayerReady,
            'onStateChange': onStateChange
            }
        });
        window.player = player;
    };

    function onPlayerReady(event) {
        //binding button (or inline "onclick") don't seem to work initially if 
        //instantiated before player is ready.
        //(sometimes)

        //external play button doesn't work initially if not muted.
        //a recent change in both chrome and firefox apparently.
        //we can start the video (muted) externally, but unmuting caused video to stop
        //player.mute();

        $('#play-button').on('click', function() {
            window.playVideo();
        });
    };

    function onStateChange(event) {
        var st = $('#substart-text');

        if (event.data === YT.PlayerState.PLAYING) {
            $('#play-button').hide();
            $('#play-button-waiting').hide();
            $('#pause-button').show();

            has_been_started_by_user = true;
        };

        if (! has_been_started_by_user) {
            return;
        };

        if ($(st).text().indexOf('Click play') != -1) {
            $(st).text('Beginning of transcript');
        };

        if (event.data === YT.PlayerState.PAUSED) {
            $('#play-button').show();
            $('#pause-button').hide();
        }
    };

    function stopVideo() {
        player.stopVideo();
    };

    function _getCurrentTimeIndex(arr, t) {
        if (arr.length == 1) {
            return window.startTimes.indexOf(arr[0]);
        }

        var mid_index = Math.floor(arr.length / 2);

        if (t >= arr[mid_index]) {
            return _getCurrentTimeIndex(arr.slice(mid_index, arr.length), t);
        }
        return _getCurrentTimeIndex(arr.slice(0, mid_index), t);
    };

    window.player = player;
    window.onYouTubeIframeAPIReady = onYouTubeIframeAPIReady;
    window.onPlayerReady = onPlayerReady;
    window.onStateChange = onStateChange;

    window.playVideo = function() {
        player.playVideo();

        $('#play-button').hide();
        $('#pause-button').show();
    };

    window.pauseVideo = function() {
        player.pauseVideo();

        $('#pause-button').hide();
        $('#play-button').show();
    };

    window.scrollSubs = function(d) {
        if (d == 'down') {
            $('.sub-box').scrollTop(1000000);
        } else {
            $('.sub-box').scrollTop(0);
        };
    };

    window.updatePlayerTime = function(s) {
        player.seekTo(s, true);
    };

    window.toggleSync = function() {
        var b = $('#autoscroll-button');

        keep_sync = ! keep_sync;

        if (keep_sync) {
            $(b)
                .removeClass('button-off')
                .find('i')
                .removeClass('fa-ban')
                .addClass('fa-thumbs-up')

        } else {
            $(b)
                .addClass('button-off')
                .find('i')
                .removeClass('fa-thumbs-up')
                .addClass('fa-ban')
        }
    };

    window.syncScroll = function() {
        console.log('syncing');

        var t = player.getCurrentTime();

        if (t) {
            index = _getCurrentTimeIndex(window.startTimes, t);

            el = subtitle_elements[index];

            $('.sub-box').scrollTop(0, 0);

            $('.sub-box').scrollTop($(el).position().top);
        }
    };

    window.searchSubs = function(t, clear) {
        var substart_text = $('#substart-text');
        var subend_text = $('#subend-text');
        var hit_count = 0;
        var match_text = 'matches';

        $('.sub').show();

        $('.search-highlight').each(function(i, v) {
            $(v).before($(v).text());
            $(v).remove();
        });

        //no search, clear results
        if (clear || t.length < 1 || t.replace(/\s\s+/g, ' ') == ' ') {
            $(substart_text).text('Beginning of transcript');
            $(subend_text).text('End of transcript');
            $('#search-input').val('');
            return;
        };

        //if (t.length < 3) {
            //$(substart_text).text('Beginning of transcript');
            //$(subend_text).text('End of transcript');

            //if (clear) {
                //$('#search-input').val('');
            //};

            //return;
        //};

        $(subtitle_elements).each(function(i,sub) {
            var new_content = '';
            var match_sjart, match_stop, pre, post
            var current_startpoint = 0;
            var new_subtext = $('<div class="sub-text"></div>');

            var subtext = $(sub).find('.sub-text').first();
            var text = $(subtext).text();
            var clicktrigger = $(subtext).attr('onclick')

            var r = new RegExp(t, 'ig')

            if (text.search(r) === -1) {

                $(sub).hide();
            }
            else {
                while ((match = r.exec(text)) !== null) {
                    hit_count += 1;
                    match_start = match.index;
                    match_stop = r.lastIndex;

                    pre = text.substring(current_startpoint, match_start)
                    post = text.substring(match_stop)

                    $(new_subtext).append(pre);
                    $(new_subtext).append('<span class="search-highlight">' + match[0] + '</span>');

                    var current_startpoint = match_stop;
                }
                $(new_subtext).append(post);

                $(sub).find('.sub-text')
                    .off('click')
                    .replaceWith(new_subtext);

                $(new_subtext).attr('onclick', clicktrigger);
            }
        });

        if (hit_count == 1) {
            match_text = 'match';
        };

        $(substart_text).text('Beginning of search for ' + t + ' (' + hit_count + ' ' + match_text + ')');
        $(subend_text).text('End of search for ' + t + ' (' + hit_count + ' ' + match_text + ')');
    };

    //pause video when current sub mousedown (for H highlight to prevent scroll leaving sub).
    $('.sub-text').mousedown(function() {
        if (! keep_sync) {
            //if autoscroll isn't enabled, don't pause vid.
            return true;
        };

        //is sub the current one?
        if ($(this).parent().hasClass('highlight')) {
            pauseVideo();
        }
    });


    setInterval(function() {
        if (! keep_sync) {
            $('.highlight').removeClass('highlight');
            return;
        };

        if (! player || ! player.getPlayerState) {
            return;
        };

        if (player.getPlayerState() != 1) {
            return;
        };

        var t = player.getCurrentTime();

        if (t) {
            index = _getCurrentTimeIndex(window.startTimes, t);

            el = subtitle_elements[index];

            if (el == current_sub) {
                if (! $(el).hasClass('highlight')) {
                    $(el).addClass('highlight');
                }

                return;
            };

            $('.highlight').removeClass('highlight');
            $(el).addClass('highlight');

            if (! keep_sync) {
                return;
            };

            $('.sub-box').scrollTop(0, 0);

            $('.sub-box').scrollTop($(el).position().top);

            current_sub = el;
        };

    }, 1000);

});
