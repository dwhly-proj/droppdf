(function() {
    //var in_process = false;

    function _showError(m) {
        $('#upload-error')
            .text(m)
            .show();
    };

    function _hideError() {
        $('#upload-error')
            .text('')
            .hide();
    };

    function _checkFileError(file) {
        //check file type and size
        //return null if good, otherwise return error.

        _hideError();

        if (file.type.indexOf('pdf') === -1) {
            return 'document is not a pdf!'
        };

        if (file.size > 157287000) {
            return 'file is too large (150MB limit)'
        };

        return null
    };

    function _updateFileName() {
        _hideError();

        var filename = '';

        var file = $('#pdf-file').prop('files')[0];

        if (file) {
            var check_error = _checkFileError(file);

            if (check_error) {
                _showError(check_error);

                return false;
            }

            filename = file.name;

            $('#filename').text(filename);
            $('#filesize').text(file.size + 'bytes');
        };

        return true;
    };

    function _restoreReady() {
        $('#upload-button').removeClass('disabled');
        $('#wait-icon').hide();
        $('#pdf-file').prop('disabled', false);

        $('#pdf-file').val(null);
        $('#filename').text('');

        $('#copy-count').val(1);

    };

    function _showProcessed(file_htmls) {
        var el = $('#result-copies');

        $(el).empty();

        $.each(file_htmls, function(i, v) {
            $(el).append(v);
        });
    };

    function _uploadPDF() {
        _hideError();

        var csrf_token_form = $('<input id="csrf_form_token" name="csrfmiddlewaretoken" value="' + CSRF_TOKEN + '" style="visibility: hidden">');

        var file = $('#pdf-file').prop('files')[0];

        if (! file) {
            return _showError('Please select a file first');
        }

        var check_error = _checkFileError(file);
        if (check_error) {
            return _showError(check_error);
        }

        $('#param-form').append(csrf_token_form);

        var formData = new FormData($('#param-form')[0]);

        $.ajax({
            url : '/fingerprinter/upload/',
            type : 'POST',
            data : formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response && response.directory && response.task_id) {
                    $('#csrf_form_token').hide();
                    $('#upload-button').hide();
                    $('#in-progress').show();

                    var try_count = 0;
                    //check if processing is complete
                    var intvl = setInterval(function() {
                        if (try_count > 40) {
                            clearInterval(intvl);
                            _showError('File processing failed to complete. Please try a smaller file');
                        };

                        $.ajax({
                            url: '/fingerprinter/check_complete/',
                            type: 'POST',
                            data: {task_id: response.task_id, csrfmiddlewaretoken: CSRF_TOKEN},
                            success: function(rslt) {
                                if (rslt && rslt.status == 'SUCCESS') {
                                    clearInterval(intvl);
                                    window.location.href = '/fingerprinter/result/?dir=' + response.directory
                                }
                            },
                            fail: function(e) {
                                clearInterval(intvl);
                                _showError('Processing failed. Check file and try again.');
                            },
                        });

                        try_count += 1;

                    }, 5000);

                } else {
                    _showError('Problem processing file. Please check name and file type and try again.');
                }
            },
            fail: function(error) {
                _showError('Upload failed');
            },
            statusCode: {
                404: function() {
                    _showError('Upload failed');
                },
                406: function() {
                   _showError('file not provided');
                },
            },
        });
    };

    window.uploadPDF = _uploadPDF;
    window.updateFileName = _updateFileName;

}());
