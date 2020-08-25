$(document).ready(function(){
    var player, duration;

    var current_sub;

    var keep_sync = true;
    var show_highlight = true;
    var scroll_sub_down = true;

    var subtitle_elements = $('.sub');

    //var body_width = document.body.clientWidth

    //$(window).resize(function() {
        //body_width = document.body.clientWidth
    //});

    var times = [];

    var tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    var firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);


    function onYouTubeIframeAPIReady() {
        player = new YT.Player('video-player-iframe', {
            events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
            }
        });
        window.player = player;
    }

    function onPlayerReady(event) {
        setTimeout(function() {
            if (player) {
                player.playVideo();
            }
            else {
                return onPlayerReady(event);
            }
        }, 100);
    }

    var done = false;
    function onPlayerStateChange(event) {
    }

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
    window.onPlayerStateChange = onPlayerStateChange;

    window.scrollSubs = function() {
        var sel = $('#scroll-sub');

        if (scroll_sub_down) {
            $('.sub-box').scrollTop(100000);
            scroll_sub_down = false;
            $(sel).text('⏫');
        } else {
            $('.sub-box').scrollTop(0);
            scroll_sub_down = true;
            $(sel).text('⏬');
        };
    };

    window.updatePlayerTime = function(s) {
        player.seekTo(s, true);
    };

    window.toggleSync = function() {
        keep_sync = ! keep_sync;
    };

    window.toggleHighlight = function() {
        show_highlight = ! show_highlight;
    };

    window.searchSubs = function(t) {
        $('.sub').show();

        if (t.length < 3) {
            return;
        }

        $(subtitle_elements).each(function(i,sub) {

            var text = $(sub).find('.sub-text').first().text();

            var r = new RegExp(t, 'i')

            if (text.search(r) === -1) {
                $(sub).hide();
            }
        });
    };


    setInterval(function() {
        if (! keep_sync && ! show_highlight) {
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

            if (index == 0) {
                $('.sub-box').scrollTop(0);
            }

            el = subtitle_elements[index];

            if (el == current_sub) {
                if (!show_highlight) {
                    $('.highlight').removeClass('highlight');
                } else {
                    if (! $(el).hasClass('highlight')) {
                        $(el).addClass('highlight');
                    }
                }

                return;
            };

            $('.highlight').removeClass('highlight');
            if (show_highlight) {
                $(el).addClass('highlight');
            };

            if (! keep_sync) {
                return;
            };

            $('.sub-box').first().scrollTop($(el).position().top);

            current_sub = el;
        };

    }, 1000);

});
