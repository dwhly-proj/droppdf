var dropzone;

var type = "";

//Google Drive Authentication
function handleAuthClick(event) {
    //give notice if auth keys not present
    if (CLIENT_ID == '' ||  API_KEY == '' || SCOPES == []) {
        alert('Google authorization keys not present. Check configs exist.');
        return;
    }
    gapi.auth.authorize(
            {client_id: CLIENT_ID,
            scope: SCOPES.join(' '),
            immediate: false},
            handleauthresult);
    return false;
};

function handleauthresult(authresult) {
    if (authresult && !authresult.error) {
        //auth was successful.
        //open google drive in new tab
        var d = document.createElement('a');
        d.id = 'open-google-drive';
        d.href = 'https://drive.google.com/drive/my-drive';
        d.target = '_blank';
        document.body.appendChild(d);
        d.click();

        //window.open('https://drive.google.com/drive/my-drive', '_blank');
    } else {
        //auth failed
        return;
    }
}

$(document).ready(function(){
    var valid_extensions = ['.pdf', '.docx', '.xlsx', '.doc', '.xls', '.ods', '.csv', '.epub',
        '.odt', '.ott', '.rtf', '.odp', '.ppt', '.pptx']

    var options = {
        url: "/upload/",
        headers: {
        'x-csrftoken': CSRF_TOKEN
        },

        paramName: "file",

        autoProcessQueue: true,

        acceptedFiles: valid_extensions.join(','), 

        timeout: 120000,

        clickable: false,

        uploadprogress: function(file, progress, bytes) {
            //account for upload from server to cloud
            var width = progress * .66;

            $('[data-dz-uploadprogress]').css('width', width + '%');

            //there is lag between full upload and complete because of upload 
            //time from server to cloud. in process.
            //complete progressbar
            var period = 150;

            if (file.size && file.size > 3500000) {
                period = 200;
            }

            if (file.size && file.size > 7500000) {
                period = 250;
            }

            if (file.size && file.size > 10000000) {
                period = 350;
            }

            if (progress >= 100) {
                $('#process-content-text')
                    .text('Processing...')

                var intvl = setInterval(function() {
                    if (width >= 100) {
                        clearInterval(intvl);
                        return;
                    };
                    width += 1;
                    $('[data-dz-uploadprogress]').css('width', width + '%');
                }, period);
            };
        },

        accept: function(file, done) {
            $('#main-content-text').hide();

            $('#process-content-text')
                .text('Uploading...')
                .show();

            done();
        },

        init: function() {
            this.on("addedfile", function(file) {
                var extension = file.name.split(".");
                extension = extension[extension.length-1];
                extension = extension.toLowerCase();
            
                if (valid_extensions.includes('.' + extension)) {
                    type = extension;
                }
                else {
                    var html = '<div>Invalid filetype</div>';
                    displayError(html);
                    return false;
                }
            });

            this.on("success", function(file, filename) {
                $('[data-dz-uploadprogress]').css('width', '100%');

                if (type == 'pdf') {
                    window.location.href = '/pdf/' + filename + '/'
                }
                else if (type == 'csv') {
                    window.location.href = '/csv/' + filename + '/'
                }
                else if (type == 'epub') {
                    window.location.href = '/epub/' + filename + '/'
                }

                else if (['doc', 'docx', 'epub', 'odt', 'ott', 'rtf', 'odp', 'ppt', 'pptx'].indexOf(type) != -1) {
                    window.location.href = '/pdf/' + filename + '/'
                }

                else if (['xls', 'xlsx', 'ods'].indexOf(type) != -1) {
                    window.location.href = '/csv/' + filename + '/'
                }


                else {
                    var html = '<div>Filetype not supported</div>'; 
                    displayError(html);
                }
            });

            this.on("error", function(file, error, xhr) {
                console.log(file, error, xhr)


                /* if 406 "Not Acceptable" pdf has no text */
                if (xhr && xhr.status == 406) {
                    var ocr_url = window.location.origin + '/ocr';

                    var html = '<div>This document is an image PDF or has no annotable text.</div><div>If you would like to turn it into an annotable document please use the OCR feature at '; 
                    html += '<span><a href="'
                    html += ocr_url; 
                    html += '">' + ocr_url + '</a></span>';

                    displayError(html);
                };

                if (xhr && xhr.status == 422) {
                    var html = '<div>There was a problem processing your document. Perhaps try again later.</div>'; 
                    displayError(html);
                }

            });

            this.on("removedfile", function(file) {
            });
        },

    };

    function displayError(html) {
        $('#upload-error-content')
            .empty()
            .html(html);

        $('#upload-error')
            .show();

        $('#process-content-text').hide();

    };

    window.closeError = function() {
        window.location.reload(true);
    };

    dropzone = new Dropzone("div#dropzone", options);

    $('#drop-icon').on('click', function() {
        new_options = Object.assign(options);
        new_options.clickable = true;

        dropzone.destroy();

        dropzone = new Dropzone("div#dropzone", new_options);

        $('#dropzone').click();

    });
});


function openYouTubeUrl() {
    var match, video

    var url = $('#youtube-url').val();

    if (url.length < 1 || !url) {
        $('#youtube-url-error')
            .text('')
            .hide();
        return;
    };

    if ((url.indexOf('youtube.com/watch?') == -1) && (url.indexOf('youtu.be') == -1)) {
        $('#youtube-url-error')
            .text('not a valid youtube video link')
            .show();
            return;
    };

    if ( (url.indexOf('youtu.be') != -1) && (url.indexOf('youtube') == -1) )  {
        video = url.split('/').slice(-1).pop(); 
    } else {
        match = RegExp('[?&]' + 'v=([^&]*)').exec(url);
        video = decodeURIComponent(match[1].replace(/\+/g, ' '));
    }

    if (!video || video.length < 5) {
        $('#youtube-url-error')
            .text('missing or incorrect video id in link')
            .show();
            return;
    };

    window.open('/video/' + video + '/', '_blank');

}
