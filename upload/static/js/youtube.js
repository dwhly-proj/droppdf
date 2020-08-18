$(document).ready(function(){
    var player, duration;

    var subtitle_elements = [];
    var times = [];

    var source = 'https://www.youtube.com/embed/'
    source += window.videoId; 
    source += '?enablejsapi=1'
    //source += '?enablejsapi=1&origin='
    //source += window.location; 
    source += '&widgetid=1';

    $('#video-player-iframe').prop('src', source);

    function onYouTubeIframeAPIReady() {
        player = new YT.Player('video-player-iframe', {
            events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
            }
        });
    }

    function onPlayerReady(event) {
        player.playVideo();
    }

    var done = false;
    function onPlayerStateChange(event) {
    }

    function stopVideo() {
        player.stopVideo();
    }


    window.player = player;
    window.onYouTubeIframeAPIReady = onYouTubeIframeAPIReady;
    window.onPlayerReady = onPlayerReady;
    window.onPlayerStateChange = onPlayerStateChange;


    window.updatePlayerTime = function(s) {
        console.log(player);
        player.seekTo(s, true);
    }

    setInterval(function() {
        //TODO scroll as video plays
        //var sub = $('.sub'); 
        //var t = player.getCurrentTime();

        //console.log(t);

        //$(sub[20]).get(0).scrollIntoView();

    }, 5000);

});
