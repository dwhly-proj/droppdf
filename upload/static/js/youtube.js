$(document).ready(function(){
    var player;

    function onYouTubeIframeAPIReady() {
        player = new YT.Player('video-player', {
            height: '390',
            width: '640',
            videoId: window.videoId, 
            events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
            }
        });
    }

    function onPlayerReady(event) {
        //event.target.playVideo();
    }

    var done = false;
    function onPlayerStateChange(event) {
        //if (event.data == YT.PlayerState.PLAYING && !done) {
            //setTimeout(stopVideo, 6000);
            //done = true;
        //}
    }

    function stopVideo() {
        player.stopVideo();
    }

    window.player = player;
    window.onYouTubeIframeAPIReady = onYouTubeIframeAPIReady;
    window.onPlayerReady = onPlayerReady;
    window.onPlayerStateChange = onPlayerStateChange;

});    
