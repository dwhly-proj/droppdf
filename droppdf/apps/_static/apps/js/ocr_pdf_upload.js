
//const CSRF_TOKEN = document.querySelector('[name=csrfmiddlewaretoken]').value;

(function() {

    upload_in_progress = false;

    uploaded_file_info = null;

    _uploadAndCheckText = function() {
        var percentComplete;

        $('.button-box').hide();
        $('#upload-error').hide();
        $('#in-progress').show();


        var formData = new FormData();
        formData.append('pdf-file', $('#pdf-file')[0].files[0]);
        formData.append('csrfmiddlewaretoken', CSRF_TOKEN);


        $.ajax({
            url : '/ocr/upload',
            type : 'POST',
            data : formData,
            xhr: function() {
                var xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener("progress", function(evt) {
                    if (evt.lengthComputable) {
                        percentComplete = (evt.loaded / evt.total) * 100;

                        $('#progress-bar-inner').css('width', percentComplete / 2 + '%');

                        //processing time on server (guess)
                        if (percentComplete >= 100) {

                            var prog = setInterval(function() {

                                if ((percentComplete / 2) >= 100) {
                                    clearInterval(prog);
                                    return;
                                }

                                percentComplete += 1;
                                $('#progress-bar-inner').css('width', percentComplete / 2 + '%');

                            }, 70);
                        }
                    }
               }, false);
               return xhr;
            },
            processData: false,
            contentType: false,
            success : function(response) {

                if (response && response.file_info) {

                    uploaded_file_info = response.file_info;

                    $('.button-box').show();
                    $('#in-progress').hide();

                    $('#progress-bar-inner').css('width', '0%');

                    upload_in_progress = false;

                    $('#pdf-file').attr('disabled', false);

                    $('#drag-instruction').show();

                    if (response.file_info.processing_error) {

                        $('#upload-error')
                            .text(response.file_info.processing_error)
                            .show();

                        $('#run-button')
                            .addClass('disabled')
                            .attr('disabled', true)
                    } else {
                        $('#run-button')
                            .removeClass('disabled')
                            .attr('disabled', false)
                    }
                };
            },
            fail: function(error) {
                var msg;

                if (! error) {
                    msg = 'error uploading document';
                } else {
                    msg = error;
                }

                $('#in-progress').hide();

                $('#pdf-file').attr('disabled', false);

                $('#progress-bar-inner').css('width', '0%');

                upload_in_progress = false;

                $('#drag-instruction').show();

                $('#upload-error')
                    .text(msg)
                    .show();
            },
            statusCode: {
                404: function() {
                    this.fail();
                },
                406: function() {
                    this.fail('file not provided');
                },
            },
        });
    };

    window.checkThenUpload = function() {
        if (upload_in_progress) {
            return;
        };

        if (updateFileName()) {
            _uploadAndCheckText();

            $('#pdf-file').attr('disabled', true);

            $('#drag-instruction').hide();

            upload_in_progress = true;
        };
    };

    runOCR = function(force) {
        var form =  $('<form action="/ocr/result" method="POST"></form>');

        if (force) {
            var force_field = $('<input id="force_flag" name="force_flag" value="true" type="hidden">');
            $(form).append(force_field);
        };

        var file_info = JSON.stringify(uploaded_file_info);

        var file_info_field = $('<input id="file_info" name="file_info" type="hidden">');
        $(file_info_field).val(file_info);

        var csrf_token_form = $('<input name="csrfmiddlewaretoken" value="' + CSRF_TOKEN + '">');

        $(form).append(file_info_field, csrf_token_form);

        $('body').append(form);

        $(form).submit();
    };

    $(document).ready(function() {
        upload_in_progress = false;
        $('.button-box').hide();
        $('#in-progress').hide();
        $('#pdf-file').attr('disabled', false);
        $('#progress-bar-inner').css('width', '0%');
        $('#pdf-file')
            .attr('disabled', false)
            .val(null)
    });

}());
